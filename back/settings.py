import environ
import os

env = environ.Env()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

match env("ENVIRONMENT_NAME"):
    case "production":
        print("Running with production settings.")
        from back.production_settings import *
    case "production_debug":
        print("Running with debug production settings.")
        from back.production_debug_settings import *
    case "development":
        print("Running with development settings.")
        from back.development_settings import *