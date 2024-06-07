# Plato

Create a `.env` file in the root directory:

```
.
├── src
└── .env
```

```
# imitater or openai
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=sk-xxx

# models
EMBED_MODEL=text-embedding-ada-002
CHAT_MODEL=gpt-3.5-turbo
TOKENIZER_PATH=01-ai/Yi-6B-Chat

# text splitter
CHUNK_SIZE=200
CHUNK_OVERLAP=30

# storages
STORAGE=redis
SEARCH_TARGET=content
REDIS_URI=redis://localhost:6379
ELASTICSEARCH_URI=http://localhost:9001

# vectorstore
VECTORSTORE=chroma
CHROMA_PATH=./chroma
MILVUS_URI=http://localhost:19530
MILVUS_TOKEN=0
```

## Build Hybrid Index

```bash
python src/launcher.py --action build
```

> [!TIP]
> If the input folder is `data/test`, the cache file will be saved as `data/test.pkl`.

## Launch Server

```bash
python src/launcher.py --action launch
```

## Test Mentor

```bash
python tests/test_mentor.py
```
