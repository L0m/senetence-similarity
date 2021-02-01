from os import getenv


def getenv_int(key, default):
    return int(getenv(key, default=str(default)))


class Config:
    database_main_url = getenv("DATABASE_MAIN_URL", default="postgresql://sesi:sesi@db/sesi")

    database_vec_host = getenv("DATABASE_VEC_HOST", default="db_vec")
    database_vec_port = getenv("DATABASE_VEC_PORT", default=9200)
    database_vec_index_file = getenv("DATABASE_VEC_INDEX_FILE", default="/opt/elastic/index.json")

    text_embedding_model_url = getenv("TEXT_EMBEDDING_MODEL_URL", default="/opt/USE/")
    text_embedding_batch_size = getenv_int("TEXT_EMBEDDING_BATCH_SIZE", default=256)
    text_preview_length = getenv_int("TEXT_PREVIEW_LENGTH", default=64)

    similar_sentence_count = getenv_int("SIMILAR_SENTENCE_COUNT", default=10)
    sentence_limit = getenv_int("SENTENCE_LIMIT", default=100)


config = Config()
