import os

class FastAPIServerConfig:
    # クラス変数
    host = os.getenv("HOST", "0.0.0.0")
    port = os.getenv("PORT", "5000")
    upload_dir = os.getenv("UPLOAD_DIR", "tmp")
    debug = bool(os.getenv("DEBUG", "False"))
