"""POST each image in data/uploads to the FastAPI /inference endpoint sequentially."""

import json
import mimetypes
import os
import sys
import uuid
import urllib.error
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
UPLOADS_DIR = PROJECT_ROOT / "data" / "uploads"
API_URL = os.environ.get("INFRASCAN_API_URL", "http://127.0.0.1:8000/inference")

IMAGES = [
    UPLOADS_DIR / "image.jpeg",
    UPLOADS_DIR / "image.webp",
    UPLOADS_DIR / "multi.png",
]


def post_image(path: Path) -> dict:
    boundary = f"----infrascan{uuid.uuid4().hex}"
    content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    file_bytes = path.read_bytes()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{path.name}"\r\n'
        f"Content-Type: {content_type}\r\n"
        f"\r\n"
    ).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    request = urllib.request.Request(
        API_URL,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def main():
    for path in IMAGES:
        if not path.is_file():
            print(f"skip missing file: {path}", file=sys.stderr)
            continue
        try:
            result = post_image(path)
        except urllib.error.URLError as exc:
            print(f"failed {path.name}: {exc}", file=sys.stderr)
            sys.exit(1)
        print(f"{path.name} -> task_id={result.get('task_id')} status={result.get('status')}")


if __name__ == "__main__":
    main()
