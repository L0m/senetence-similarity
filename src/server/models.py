from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, constr


class NewText(BaseModel):
    text: constr(min_length=1, max_length=1000000) = Field(..., title='Text')


class NewTextResponse(BaseModel):
    id: str = Field(..., title='Id')


class Sentence(BaseModel):
    sentence_id: int = Field(..., title='Sentence Id')
    start_pos: int = Field(..., title='Start Pos')
    end_pos: int = Field(..., title='End Pos')
    sentence: str = Field(..., title='Sentence')


class SimilarSentence(BaseModel):
    text_id: str = Field(..., title='Text Id')
    sentence_id: int = Field(..., title='Sentence Id')
    sentence: str = Field(..., title='Sentence')
    similarity: float = Field(..., title='Similarity')


class SimilarSentencesMeta(BaseModel):
    took: int = Field(..., title='Took')


class SimilarSentencesResponse(BaseModel):
    meta: SimilarSentencesMeta
    sentence: str = Field(..., title='Sentence')
    similar_sentences: List[SimilarSentence] = Field(..., title='Similar Sentences')


class TextListMeta(BaseModel):
    took: int = Field(..., title='Took')
    total: int = Field(..., title='Total')


class TextPreview(BaseModel):
    id: str = Field(..., title='Id')
    preview: str = Field(..., title='Preview')
    created: datetime = Field(..., title='Created')


class TextResponse(BaseModel):
    id: str = Field(..., title='Id')
    created: datetime = Field(..., title='Created')
    sentences: List[Sentence] = Field(..., title='Sentences')


class ValidationError(BaseModel):
    loc: List[str] = Field(..., title='Location')
    msg: str = Field(..., title='Message')
    type: str = Field(..., title='Error Type')


class HTTPValidationError(BaseModel):
    detail: Optional[List[ValidationError]] = Field(None, title='Detail')


class TextListResponse(BaseModel):
    meta: TextListMeta
    texts: List[TextPreview] = Field(..., title='Texts')
