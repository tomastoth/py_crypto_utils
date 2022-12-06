import os


class Config:
    COVALENT_KEY = os.getenv("COVALENT_API_KEY")
    W3_PROVIDER = os.getenv("W3_PROVIDER")
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


config = Config()
