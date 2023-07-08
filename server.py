from fastapi import FastAPI
from pymongo import MongoClient
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

app = FastAPI()

# MongoDB 연결 설정
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
collection = db["sentences"]

# 정적 파일 서비스 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

class SentenceInput(BaseModel):
    sentence: str

@app.get("/")
async def get_index():
    return FileResponse("static/index.html")

@app.post("/sentences")
async def save_sentence(sentence_input: SentenceInput):
    sentence_data = {"sentence": sentence_input.sentence}
    result = collection.insert_one(sentence_data)
    # result = collection.insert_one(sentence_input)
    return {"message": "Sentence saved successfully"}

@app.get("/sentences")
async def get_sentences():
    sentences = []
    for document in collection.find():
        sentences.append(document["sentence"])
    return {"sentences": sentences}
