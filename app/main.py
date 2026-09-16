from fastapi import FastAPI, status, Request
from .models import Base
from .database import engine
from . import routes

app = FastAPI()

@app.get("/healthy", status_code=status.HTTP_200_OK)
def health_check():
    return {"status" : "Healthy"}


app.include_router(routes.router)


