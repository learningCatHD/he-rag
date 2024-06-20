import redis
import pickle
# 设置Redis服务器地址和端口号
# host = '3.39.236.188'
host = '52.78.46.237'
port = 6379

try:
    # 创建Redis连接对象
    r = redis.Redis(host=host, port=port)

    # 获取所有键
    all_keys = r.keys()

    # 打印所有键
    if all_keys:
        print(f"Redis中共有 {len(all_keys)} 个键:")
        for key in all_keys:
            print(key.decode())
        print('LLM: ',len(r.hgetall('LLM').keys()))
        print('LLM_roadmap: ', len(r.hgetall('LLM_roadmap').keys()))
    else:
        print("Redis中没有任何键")
    

    # if all_keys:
    #     r.delete(*all_keys)
    #     print("已成功删除所有键")
    # else:
    #     print("Redis中没有任何键")
    

except Exception as e:
    print(f"无法连接Redis服务器: {e}")    
    
    