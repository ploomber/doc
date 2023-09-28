from typing import Union

from fastapi import FastAPI, APIRouter

app = FastAPI()


prefix_router = APIRouter(prefix="/__PROJECT_ID__")


@prefix_router.get("/")
def read_root():
    return {"Hello": "World"}


@prefix_router.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


app.include_router(prefix_router)
