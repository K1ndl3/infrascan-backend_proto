import base64
import os
import time
from celery.signals import worker_process_init

from app.celery_app import celery_app
from app.inference import get_model, inference_service

# Same default the producer uses (path as seen inside the worker container).
DEFAULT_WEIGHT_PATH = os.environ.get("INFRASCAN_WEIGHT_PATH", "weights/best.pt")


@worker_process_init.connect
def preload_model(**kwargs):
    """Warm YOLO weights in each prefork child so the first task is not a cold load."""
    get_model(DEFAULT_WEIGHT_PATH)


@celery_app.task(name="lab.add")
def add(x, y):
    return x + y


@celery_app.task(name="infrascan.inference")
def inference_worker(weight_path, image_b64, filename=None):
    image_bytes = base64.b64decode(image_b64)
    time.sleep(4)
    result = inference_service(weight_path, image_bytes, filename=filename)
    return {"status": "completed", "result": result}