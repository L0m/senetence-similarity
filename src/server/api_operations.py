from server.db.database_main import database_main
from server.db.database_vec import database_vec, make_documents
from server.db.nlp import text_embedding
from server import models
from server.config import config


async def list_texts():
    db_texts = await database_main.get_texts()
    num_db_texts = len(db_texts)
    meta = models.TextListMeta(took=num_db_texts, total=num_db_texts)
    texts = [models.TextPreview(
        id=str(t.id),
        preview=t.preview,
        created=t.created) for t in db_texts]
    return models.TextListResponse(meta=meta, texts=texts)


async def post_text(body: models.NewText):
    text = await database_main.create_new_text(body.text)
    sentences = await database_main.get_sentences(text.id, 0)

    sentence_ids = []
    texts = []
    for s in sentences:
        if len(texts) >= config.text_embedding_batch_size:
            vectors = text_embedding.embed_texts(texts)
            documents = make_documents(sentence_ids, vectors)
            database_vec.add_documents(documents)
            texts.clear()
            sentence_ids.clear()
        else:
            texts.append(s.content)
            sentence_ids.append(s.id)
    if len(texts) > 0:
        vectors = text_embedding.embed_texts(texts)
        documents = make_documents(sentence_ids, vectors)
        database_vec.add_documents(documents)

    return models.NewTextResponse(id=str(text.id))


async def get_text(text_id: str):
    text_id_num = int(text_id)
    db_text = await database_main.get_text(text_id_num)
    db_sentences = await database_main.get_sentences(text_id_num, config.sentence_limit)
    sentences = [models.Sentence(
        sentence_id=s.id,
        start_pos=s.start_pos,
        end_pos=s.end_pos,
        sentence=s.content,
    ) for s in db_sentences]
    return models.TextResponse(
        id=text_id,
        created=db_text.created,
        sentences=sentences,
    )


async def find_similar_sentences(text_id: str, sentence_id: int):
    sentence = await database_main.get_sentence(sentence_id)
    vector = text_embedding.embed_texts([sentence.content])[0]
    similars = database_vec.search_similar(vector, config.similar_sentence_count + 1)
    response_sentences = []
    for i in range(len(similars)):
        similar = similars[i]
        if similar.sentence_id == sentence_id:
            continue
        if len(response_sentences) == config.similar_sentence_count:
            break
        similar_sentence = await database_main.get_sentence(similar.sentence_id)
        response_sentences.append(models.SimilarSentence(
            text_id=similar_sentence.owner_id,
            sentence_id=similar_sentence.id,
            sentence=similar_sentence.content,
            similarity=similar.score,
        ))
    response_meta = models.SimilarSentencesMeta(took=len(similars))
    return models.SimilarSentencesResponse(
        meta=response_meta,
        sentence=sentence.content,
        similar_sentences=response_sentences,
    )
