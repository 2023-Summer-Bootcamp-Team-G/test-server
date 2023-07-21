import uuid
import json
import logging
import asyncio

from bson.json_util import dumps  # , default
from datetime import datetime, timedelta

from enum import Enum
from pymongo import MongoClient
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from fastapi import FastAPI, BackgroundTasks, HTTPException, Response

# from fastapi.middleware.cors import CORSMiddleware

from api import create_image, generate_presigned_url

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# # CORS 허용 설정
# origins = [
#     "*",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# MongoDB 연결 설정
# collection = MongoClient("mongodb://localhost:27017/")["mydatabase"]["sentences"]
collection = MongoClient("mongodb://mongodb:27017/")["mydatabase"]["sentences"]


class SentenceInput(BaseModel):
    sentence: str


class TaskStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


tasks = dict()


@app.get("/")
async def get_index(response: Response):
    return FileResponse("static/index.html")


@app.get("/sentences")
async def get_sentences():
    logging.info("get_list")
    # sentences = list()
    # for document in collection.find():
    #     sentences.append(document["sentence"])
    # return {"sentences": sentences}

    # json_documents = [json.loads(json.dumps(doc)) for doc in collection.find()]

    # json_documents = dumps(collection.find(), default=default)

    projection = {
        "_id": False,
        "object_name": False,
        "expiration_time": False,
    }  # Exclude the "_id" field

    documents = collection.find({}, projection)

    # Convert BSON documents to JSON
    json_documents = json.loads(dumps(documents))

    return {"data": json_documents}


@app.post("/sentences")
async def save_sentence(
    sentence_input: SentenceInput, background_tasks: BackgroundTasks
):
    task_id = str(uuid.uuid4())
    logging.info(f"post_parm, add task with {task_id}")

    # 동기 함수 비동기식으로 실행
    tasks[task_id] = {"status": TaskStatus.RUNNING, "result": None}
    background_tasks.add_task(update_task_result, task_id, sentence_input.sentence)

    # 예상 대기시간 리턴 구현 필요 !!
    # 일단 간단하게 이전 대기 시간 으로 리턴

    return {
        "message": "Task added for execution",
        "task_id": task_id,
        "parm": sentence_input.sentence,
    }


@app.get("/sentences/{task_id}")
async def get_task_result(task_id: str):
    logging.info("get_check_task")

    # 비동기 작업 결과 확인 (롱 폴링)
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    iteration = 0
    while tasks[task_id]["status"] == TaskStatus.RUNNING and iteration < 5:
        await asyncio.sleep(0.2)
        iteration += 1

    if tasks[task_id]["status"] == TaskStatus.RUNNING:
        return Response(status_code=202)
    elif tasks[task_id]["status"] == TaskStatus.COMPLETED:
        result = tasks[task_id]["result"]
        processing_time = tasks[task_id]["processing_time"]
        return {"result": result, "processing_time": processing_time}
    else:
        raise HTTPException(status_code=500, detail=tasks[task_id]["error_message"])


def update_task_result(task_id: str, message: str):
    # 비동기 작업 결과 업데이트
    result, processing_time, expiration_time, error_message = create_image(
        task_id, message
    )

    if result:
        tasks[task_id]["status"] = TaskStatus.COMPLETED
        tasks[task_id]["result"] = result
        tasks[task_id]["processing_time"] = processing_time

        result = collection.insert_one(
            {
                "object_name": task_id,
                "result": result,
                "sentence": message,
                "processing_time": processing_time,
                "expiration_time": expiration_time,
            }
        )
    else:
        tasks[task_id]["status"] = TaskStatus.ERROR
        tasks[task_id]["error_message"] = error_message


# 정적 파일 서비스 설정
app.mount("/", StaticFiles(directory="static"), name="static")


# URL 일괄 갱신 작업
def renew_urls():
    current_time = datetime.utcnow()
    expiration_threshold = timedelta(hours=2)

    expired_urls = collection.find(
        {"expiration_time": {"$lt": current_time + expiration_threshold}}
    )

    for url_data in expired_urls:
        object_name = url_data["object_name"]

        url, expiration_time = generate_presigned_url(object_name)
        if url is not None:
            collection.update_one(
                {"object_name": object_name},
                {"$set": {"result": url, "expiration_time": expiration_time}},
            )
        else:
            logging.error("갱신된 사전 서명된 URL 생성 실패")


# 비동기 스케줄링 작업 실행
async def run_schedule():
    while True:
        renew_urls()
        await asyncio.sleep(3600)  # 1시간 대기


# 이벤트 루프 생성, 작업 등록
loop = asyncio.get_event_loop()
task = loop.create_task(run_schedule())
