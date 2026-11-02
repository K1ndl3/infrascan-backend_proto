import base64
import os

from fastapi import FastAPI, File, UploadFile

from app.celery_app import celery_app

app = FastAPI()

MODEL_PATH = os.environ.get("INFRASCAN_WEIGHT_PATH", "weights/best.pt")


@app.post("/inference")
async def run_inference(image: UploadFile = File(...)):
    image_bytes = await image.read()
    image_b64 = base64.b64encode(image_bytes).decode("ascii")

    async_result = celery_app.send_task(
        "infrascan.inference",
        args=[MODEL_PATH, image_b64],
        kwargs={"filename": image.filename},
    )
    return {"task_id": async_result.id, "status": "queued"}
