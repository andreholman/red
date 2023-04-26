import environ
import os

env = environ.Env()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

if env("ENVIRONMENT_NAME") == "production":
    print("Running with production settings.")
    from back.production_settings import *
elif env("ENVIRONMENT_NAME") == "development":
    print("Running with development settings.")
    from back.development_settings import *