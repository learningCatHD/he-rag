import redis
import json

# 配置 Redis 连接
host = 'localhost'
port = 6379
redis_client = redis.StrictRedis(host=host, port=port, db=0)

def store_refer_info(ref: str, refer_info: dict, expire: int = 120) -> bool:
    try:
        redis_client.hset(f"_SeamLess_sms_{ref}", mapping=refer_info)
        redis_client.expire(f"_SeamLess_sms_{ref}", expire)
        return True
    except Exception as e:
        print(f"Error storing refer info in Redis: {e}")
        return False

def get_refer_info(ref: str) -> dict:
    try:
        refer_info = redis_client.hgetall(f"_SeamLess_sms_{ref}")
        if refer_info:
            # Decode bytes to string
            refer_info = {k.decode('utf-8'): v.decode('utf-8') for k, v in refer_info.items()}
            return refer_info
        return {}
    except Exception as e:
        print(f"Error retrieving refer info from Redis: {e}")
        return {}
