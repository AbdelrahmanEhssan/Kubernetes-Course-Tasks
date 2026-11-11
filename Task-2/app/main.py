import os
import time
from contextlib import asynccontextmanager

import pymysql
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


def connect():
    return pymysql.connect(
        host=os.environ["MYSQL_HOST"],
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.environ["MYSQL_DATABASE"],
        port=3306,
        connect_timeout=5,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def initialize_database():
    for attempt in range(60):
        try:
            with connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "CREATE TABLE IF NOT EXISTS messages ("
                        "id INT AUTO_INCREMENT PRIMARY KEY, "
                        "message VARCHAR(500) NOT NULL, "
                        "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
                    )
            return
        except pymysql.MySQLError:
            if attempt == 59:
                raise
            time.sleep(2)


@asynccontextmanager
async def lifespan(application):
    initialize_database()
    yield


app = FastAPI(title=os.environ.get("APP_TITLE", "MLOps MENA Guestbook"), lifespan=lifespan)


class MessageCreate(BaseModel):
    message: str = Field(min_length=1, max_length=500)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    try:
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        return {"status": "ready"}
    except pymysql.MySQLError:
        raise HTTPException(status_code=503, detail="Database unavailable")


@app.get("/api/info")
def info():
    return {
        "app_title": os.environ.get("APP_TITLE", "MLOps MENA Guestbook"),
        "mysql_host": os.environ["MYSQL_HOST"],
    }


@app.get("/api/messages")
def get_messages():
    try:
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, message, created_at FROM messages ORDER BY id")
                messages = cursor.fetchall()
        return {"messages": messages}
    except pymysql.MySQLError:
        raise HTTPException(status_code=503, detail="Database unavailable")


@app.post("/api/messages", status_code=201)
def post_message(item: MessageCreate):
    try:
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO messages (message) VALUES (%s)", (item.message,))
                message_id = cursor.lastrowid
        return {"id": message_id, "message": item.message}
    except pymysql.MySQLError:
        raise HTTPException(status_code=503, detail="Database unavailable")
