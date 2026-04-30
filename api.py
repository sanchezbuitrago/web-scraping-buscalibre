import json

import uvicorn
from http import HTTPStatus
from fastapi import FastAPI, Response

from domain.model import commands, buscalibre as buscalibre_model
from domain.services import buscalibre, scraper
from commons.adapters import mongo_uow


_UOW = mongo_uow.MongoUOW()
_SCRAPER = scraper.BuscaLibreScraper()

app = FastAPI()

@app.get("/")
def read_root():
    return {"mensaje": "¡Hola, mundo desde FastAPI!"}


@app.get("/books")
def get_books():
    response = buscalibre.get_books(uow=_UOW)
    return response.model_dump()


@app.post("/books")
def create_book(create_book_request: commands.CreateBookRequestBody):
    try:
        response = buscalibre.create_book(uow=_UOW, scraper=_SCRAPER, cmd=create_book_request)
        return Response(status_code=HTTPStatus.OK, content=response.model_dump_json())
    except buscalibre_model.BookAlreadyExistsError:
        return Response(status_code=HTTPStatus.BAD_REQUEST, content=json.dumps({"message": "Book already exists"}))



if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=9000, reload=True)