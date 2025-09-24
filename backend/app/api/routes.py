from fastapi import APIRouter, Request
from typing import Dict, Any
import asyncio

from .models import *
from app.core.translator import TranslationEngine
from app.utils.config import load_config

router = APIRouter()

# Глобальный движок перевода
translation_engine = None

@router.on_event("startup")
async def startup_event():
    global translation_engine
    config = load_config("config.yaml")
    translation_engine = TranslationEngine(config)

@router.get("/health")
async def health_check():
    return {"status": "Путь к просветлению открыт"}

@router.get("/stats")
async def get_stats():
    if not translation_engine:
        return {"error": "Движок не инициализирован"}
    
    return {
        "total_entries": translation_engine.total_entries,
        "completed_count": translation_engine.completed_count,
        "dictionary_size": len(translation_engine.dictionary.data) if translation_engine.dictionary else 0
    }

@router.post("/translate")
async def translate_text(request: TranslationRequest):
    if not translation_engine:
        return {"error": "Движок не инициализирован"}
    
    translation = await asyncio.get_event_loop().run_in_executor(
        None, 
        translation_engine.translate_single, 
        request.text
    )
    
    return TranslationResponse(
        original=request.text,
        translated=translation or request.text,
        source="llm" if translation else "failed"
    )

@router.post("/start-translation")
async def start_translation(request: StartTranslationRequest, req: Request):
    if not translation_engine:
        return {"error": "Движок не инициализирован"}
    
    # Запускаем перевод в фоне
    asyncio.create_task(
        run_translation_task(
            translation_engine, 
            request.input_file,
            request.output_file,
            request.dry_run,
            req.app.state.broadcast
        )
    )
    
    return {"status": "Перевод начат"}

async def run_translation_task(engine, input_file, output_file, dry_run, broadcast_func):
    """Фоновая задача перевода с отправкой обновлений через WebSocket"""
    
    async def progress_callback(update_data):
        await broadcast_func({
            "type": "progress",
            "data": update_data
        })
    
    try:
        await broadcast_func({
            "type": "status",
            "data": {"message": "Начинаем путь к просветлению..."}
        })
        
        # Здесь будет логика перевода с коллбэками
        # Пока заглушка
        await asyncio.sleep(1)
        
        await broadcast_func({
            "type": "status",
            "data": {"message": "Путь завершён!"}
        })
        
    except Exception as e:
        await broadcast_func({
            "type": "error",
            "data": {"message": str(e)}
        })