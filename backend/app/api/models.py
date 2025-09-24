from pydantic import BaseModel
from typing import Optional, Dict, Any

class TranslationRequest(BaseModel):
    text: str
    context: Optional[str] = None

class TranslationResponse(BaseModel):
    original: str
    translated: str
    source: str  # "dictionary", "llm", "cache"

class ConfigUpdateRequest(BaseModel):
    max_workers: Optional[int] = None
    temperature: Optional[float] = None
    model: Optional[str] = None

class ProgressUpdate(BaseModel):
    completed: int
    total: int
    current_key: str
    current_translation: str
    status: str  # "success", "failed", "skipped"

class StartTranslationRequest(BaseModel):
    input_file: str = "data/en_us.json"
    output_file: str = "data/ru_ru.json"
    dry_run: bool = False