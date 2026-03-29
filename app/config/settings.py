import dotenv
import os 

dotenv.load_dotenv()

class Settings:
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    DEFAULT_MODEL=os.environ.get("DEFAULT_MODEL")
    FAST_MODEL=os.environ.get("FAST_MODEL")


setting=Settings()