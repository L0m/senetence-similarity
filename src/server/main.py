from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.db.database_main import database_main
from . import api_operations
from .models import (
    NewText,
    NewTextResponse,
    SimilarSentencesResponse,
    TextListResponse,
    TextResponse
)

app = FastAPI(
    title="Sentence Similarity Backend",
    description="The backend for a test assesment.",
    version="0.1.0",
)

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await database_main.connect()


@app.on_event("shutdown")
async def shutdown():
    await database_main.disconnect()


@app.get('/', response_model=Any)
async def index__get() -> Any:
    pass


@app.get('/v1/text/', response_model=TextListResponse)
async def list_texts_v1_text__get() -> TextListResponse:
    """
    List Texts
    """
    return await api_operations.list_texts()


@app.post('/v1/text/', response_model=NewTextResponse)
async def post_text_v1_text__post(body: NewText) -> NewTextResponse:
    """
    Post Text
    """
    return await api_operations.post_text(
        body,
    )


@app.get('/v1/text/{text_id}', response_model=TextResponse)
async def get_text_v1_text__text_id__get(text_id: str) -> TextResponse:
    """
    Get Text
    """
    return await api_operations.get_text(
        text_id,
    )


@app.get(
    '/v1/text/{text_id}/{sentence_id}/similar', response_model=SimilarSentencesResponse
)
async def find_similar_sentences_v1_text__text_id___sentence_id__similar_get(
    text_id: str, sentence_id: int
) -> SimilarSentencesResponse:
    """
    Find Similar Sentences
    """
    return await api_operations.find_similar_sentences(
        text_id,
        sentence_id,
    )
