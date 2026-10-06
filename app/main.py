from contextlib import asynccontextmanager

from fastapi import FastAPI, status

from . import routes
from .scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):

    start_scheduler()

    yield

    stop_scheduler()


app = FastAPI(lifespan=lifespan)


@app.get("/healthy", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "Healthy"}


app.include_router(routes.router)