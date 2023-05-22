from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from deta import Deta
import dotenv
import os

dotenv.load_dotenv()
deta = Deta(os.getenv("DB_KEY"))
app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}