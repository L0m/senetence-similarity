from typing import List, Optional
from datetime import datetime
from databases import Database
from sqlalchemy import MetaData, Table, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy import create_engine
from pydantic import BaseModel

from . import nlp
from server.config import config


class TextModel(BaseModel):
    id: Optional[int]
    preview: str
    created: datetime


class SentenceModel(BaseModel):
    id: Optional[int]
    start_pos: int
    end_pos: int
    content: str
    owner_id: int


class DatabaseMain:
    def __init__(self, url: str, text_preview_length: int):
        self.database = Database(url)
        self.metadata = MetaData()
        self.engine = create_engine(url)
        self._create_tables()
        self.text_preview_length = text_preview_length

    async def connect(self):
        await self.database.connect()

    async def disconnect(self):
        await self.database.disconnect()

    async def get_texts(self) -> List[TextModel]:
        query = self.texts.select()
        texts = await self.database.fetch_all(query)
        return [TextModel(**t) for t in texts]

    async def get_text(self, text_id: int) -> TextModel:
        query = self.texts.select(self.texts.c.id == text_id)
        text = await self.database.fetch_one(query)
        return TextModel(**text)

    async def get_sentences(self, owner_id: int, limit: int) -> List[SentenceModel]:
        query = self.sentences.select(self.sentences.c.owner_id == owner_id)
        if limit > 0:
            query = query.limit(limit)
        sentences = await self.database.fetch_all(query)
        return [SentenceModel(**s) for s in sentences]

    async def get_sentence(self, sentence_id: int) -> SentenceModel:
        query = self.sentences.select(self.sentences.c.id == sentence_id)
        sentence = await self.database.fetch_one(query)
        return SentenceModel(**sentence)

    async def create_new_text(self, text: str) -> TextModel:
        text_model = TextModel(
            id=0,
            preview=nlp.make_text_preview(text, self.text_preview_length),
            created=datetime.now()
        )
        text_query = self.texts.insert()
        text_id = await self.database.execute(text_query, text_model.dict(exclude={'id'}))
        sentences_query = self.sentences.insert()
        sentences_models = [SentenceModel(
            id=0,
            start_pos=s,
            end_pos=e,
            content=text[s:e],
            owner_id=text_id) for (s, e) in nlp.get_sentence_spans(text)]
        sentence_values = [s.dict(exclude={'id'}) for s in sentences_models]
        await self.database.execute_many(sentences_query, sentence_values)
        return await self.get_text(text_id)

    def _create_tables(self):
        self.texts = Table(
            "texts",
            self.metadata,
            Column("id", Integer, primary_key=True, index=True, unique=True),
            Column("preview", String),
            Column("created", DateTime),
        )
        self.sentences = Table(
            "sentences",
            self.metadata,
            Column("id", Integer, primary_key=True, index=True, unique=True),
            Column("start_pos", Integer),
            Column("end_pos", Integer),
            Column("content", String),
            Column("owner_id", Integer, ForeignKey("texts.id")),
        )
        self.metadata.create_all(self.engine)


database_main = DatabaseMain(config.database_main_url, config.text_preview_length)
