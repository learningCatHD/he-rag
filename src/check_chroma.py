import chromadb
import redis

client = chromadb.PersistentClient(path="/home/ubuntu/he-rag/chroma/")
print(client.list_collections())
r = redis.Redis(host='localhost', port=6378, db=0)
keys = r.keys('*')
print(keys)