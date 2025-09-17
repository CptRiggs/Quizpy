import asyncio
import json

from pathlib import Path
from quart import Quart, render_template, websocket
from quizr.broker import Broker

broker = Broker()
app = Quart(__name__)

quiz_questions = json.load(open(Path(app.root_path) / "quiz.json"))
print(quiz_questions)

def run() -> None:
    app.run()

@app.get("/")
async def index():
    return await render_template("index.html", questions=quiz_questions)

@app.get("/admin")
async def admin():
    return await render_template("admin.html", questions=quiz_questions)

async def _receive() -> None:
    while True:
        message = await websocket.receive()
        await broker.publish(message)

@app.websocket("/ws")
async def ws() -> None:
    try:
        task = asyncio.ensure_future(_receive())
        async for message in broker.subscribe():
            await websocket.send(message)
    finally:
        task.cancel()
        await task
