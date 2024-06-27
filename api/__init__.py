import time

import structlog
from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from api import article, channel, locale, publisher
from api.utils import ep_err_msg
from config import get_config

config = get_config()
logger = structlog.getLogger(__name__)


app = FastAPI(
    title="DataAPI of News Aggregator",
    description="This API is designed to handle news data.",
)


metric_collector = (
    Instrumentator(excluded_handlers=["/metrics"], should_ignore_untemplated=True)
    .instrument(
        app,
        metric_namespace="today",
        metric_subsystem="DataAPI",
    )
    .expose(app)
)

app.include_router(article.router, tags=["article"])
app.include_router(channel.router, tags=["channel"])
app.include_router(locale.router, tags=["locale"])
app.include_router(publisher.router, tags=["publisher"])


@app.exception_handler(status.HTTP_404_NOT_FOUND)
async def http_exception_handler(request, exc):
    return JSONResponse({"detail": ep_err_msg}, status_code=status.HTTP_404_NOT_FOUND)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


return_html = f"""
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Links with Descriptions</title>
</head>
<body>
    <h1>Welcome to News Data API</h1>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def root():
    return return_html
