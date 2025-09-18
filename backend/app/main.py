# backend/app/main.py
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from typing import Dict, Any
import asyncio

from app.api.routes import router
from app.core.translator import TranslationEngine

app = FastAPI(
    title="GTNH Translator API",
    description="Путь к просветлению через перевод",
    version="1.0.0"
)

# CORS для разработки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем API роуты
app.include_router(router, prefix="/api")

# WebSocket для реалтайм обновлений
active_connections: list[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        active_connections.remove(websocket)

async def broadcast_message(message: Dict[str, Any]):
    """Отправить сообщение всем подключенным клиентам"""
    for connection in active_connections[:]:
        try:
            await connection.send_text(json.dumps(message, ensure_ascii=False))
        except:
            active_connections.remove(connection)

# Делаем broadcast доступным для других модулей
app.state.broadcast = broadcast_message

# Статика для продакшена
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)