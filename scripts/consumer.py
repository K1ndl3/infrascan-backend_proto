import pika
import json
import time
#connect to rabbit MQ by establishing connection and channel
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
channel = connection.channel()
channel.basic_qos(prefetch_count=1)
#declare the target queue
channel.queue_declare(queue="inference_jobs", durable=True)
#define callback function to process jobs
# needs channel, properties, method, payload
def process_jobs(ch, method, properties, body):
    json_string = body.decode("UTF-8")
    obj = json.loads(json_string)
    time.sleep(10)
    print("job_id:", obj["job_id"])
    print("image_path", obj["image_path"])
    ch.basic_ack(delivery_tag=method.delivery_tag)
#tell rabbitMQ to consume incoming messages
channel.basic_consume(
    queue="inference_jobs",
    on_message_callback=process_jobs,
    auto_ack=False
)
#start consuming
try:
    # The script blocks right here, processing messages indefinitely
    channel.start_consuming()
    
except KeyboardInterrupt:
    print(' [!] Stopping consumer...')
    # 1. Stop consuming messages cleanly
    channel.stop_consuming()
    
finally:
    # 2. Close the connection gracefully (guaranteed to run on exit)
    if connection.is_open:
        connection.close()
        print(' [x] Connection closed safely.')