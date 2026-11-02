"""Enqueue an inference job via Celery (publish → RabbitMQ)."""

import base64
import os
import sys
from pathlib import Path

# Allow `python scripts/producer.py` from the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault(
    "CELERY_BROKER_URL",
    "amqp://guest:guest@127.0.0.1:5672//",
)
os.environ.setdefault(
    "CELERY_RESULT_BACKEND",
    "redis://127.0.0.1:6379/0",
)

from app.celery_app import celery_app  # noqa: E402

WEIGHT_PATH = "weights/best.pt"
IMAGE_PATH = PROJECT_ROOT / "data" / "uploads" / "multi.png"


def main():
    image_b64 = base64.b64encode(IMAGE_PATH.read_bytes()).decode("ascii")
    async_result = celery_app.send_task(
        "infrascan.inference",
        args=[WEIGHT_PATH, image_b64],
        kwargs={"filename": IMAGE_PATH.name},
    )
    print(f"queued task_id={async_result.id}")
    print(f"weight_path={WEIGHT_PATH} image={IMAGE_PATH.name}")


if __name__ == "__main__":
    main()
