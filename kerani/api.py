import json

from kafka import KafkaProducer
from starlette.applications import Starlette
from starlette.background import BackgroundTask
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from starlette.status import HTTP_400_BAD_REQUEST

from kerani import config


async def events(request):
    try:
        payload = await request.json()
        data = payload["events"]
    except json.decoder.JSONDecodeError:
        message = {"status": "error", "detail": "Unable to parse body"}
        return JSONResponse(message, status_code=HTTP_400_BAD_REQUEST)
    except KeyError:
        message = {"status": "error", "detail": "events not found"}
        return JSONResponse(message, status_code=HTTP_400_BAD_REQUEST)

    task = BackgroundTask(publish_to_kafka, data)
    message = {"status": "published"}
    return JSONResponse(message, background=task)


async def ping(request):
    message = {"status": "ok"}
    return JSONResponse(message)


async def publish_to_kafka(events):
    for event in events:
        identifier = event.get("identifier", {})
        topic = identifier.get("topic", "kerani-topic")
        group = identifier.get("group", "kerani-group")
        properties = event.get("properties", {})
        producer.send(topic, key=group, value=properties)


async def start_producer_pool():
    global producer
    producer = KafkaProducer(
        bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda x: json.dumps(x).encode("utf-8"),
        key_serializer=lambda x: x.encode("utf-8"),
        compression_type="gzip",
    )


async def stop_producer_pool():
    producer.close()


routes = [
    Route("/ping", ping, methods=["GET"]),
    Mount(
        "/api",
        routes=[
            Mount("/v1", routes=[Route("/events", events, methods=["POST"])]),
        ],
    ),
]

middleware = [Middleware(CORSMiddleware, allow_origins=config.CORS_ALLOW_ORIGINS)]

app = Starlette(
    routes=routes,
    on_startup=[start_producer_pool],
    on_shutdown=[stop_producer_pool],
    middleware=middleware,
)
