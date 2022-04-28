import json
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
from starlette.background import BackgroundTask
from kafka import KafkaProducer
from kerani import config


async def events(request):
    payload = await request.json()
    data = payload.get("events", [])
    task = BackgroundTask(publish_to_kafka, data)
    message = {"status": "success"}
    return JSONResponse(message, background=task)


async def healthcheck(request):
    message = {"status": "ok"}
    return JSONResponse(message)


async def publish_to_kafka(data):
    producer = KafkaProducer(
        bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda x: json.dumps(x).encode("utf-8"),
        compression_type="gzip",
    )
    for datum in data:
        topic = datum.get("name", "default-topic")
        properties = datum.get("properties")
        producer.send(topic, properties)

    producer.close()


routes = [
    Route("/healthcheck", healthcheck, methods=["GET"]),
    Mount(
        "/api",
        routes=[
            Mount("/v1", routes=[Route("/events", events, methods=["POST"])]),
        ],
    ),
]

app = Starlette(routes=routes)
