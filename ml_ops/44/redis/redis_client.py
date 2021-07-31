import os
import redis

import sys
sys.path.append(os.path.join(os.getcwd(), '../'))
from config.config import ResidConfig

# Redis サーバーに接続
redis_client = redis.Redis(host=ResidConfig.host, port=ResidConfig.port, db=ResidConfig.database_id)
