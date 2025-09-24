import json
import time
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.core.dictionary import TranslationDictionary
from app.utils.config import load_json, save_json

class TranslationEngine:
    def __init__(self, config):
        self.config = config
        self.dictionary = TranslationDictionary(config['files']['dictionary'])
        
        # Пути к файлам
        self.input_path = Path(config['files']['input'])
        self.output_path = Path(config['files']['output'])
        
        # Настройки
        self.max_workers = config['processing']['max_workers']
        self.save_interval = config['processing']['save_interval']
        
        # Синхронизация
        self.file_lock = threading.Lock()
        self.data_lock = threading.Lock()
        self.progress_lock = threading.Lock()
        
        # Статистика
        self.completed_count = 0
        self.total_entries = 0
        
        # Импортируем LLM сервис
        from app.core.llm import TranslationLLM
        self.llm = TranslationLLM(config['api'])
    
    def translate_single(self, text):
        """Перевести одну строку"""
        if self.dictionary.has_translation(text):
            return self.dictionary.get_translation(text)
        
        translation = self.llm.translate(text)
        if translation:
            self.dictionary.add_translation(text, translation)
        return translation
    
    def translate_batch(self, data, output_file, dry_run=False):
        """Перевести пакет строк"""
        self.total_entries = len(data)
        existing_translations = load_json(self.output_path) if self.output_path.exists() else {}
        
        translated_data = existing_translations.copy()
        entries_to_process = [(k, v) for k, v in data.items() if k not in existing_translations]
        
        tasks = [(k, v, translated_data, existing_translations) for k, v in entries_to_process]
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self._process_entry, *task) for task in tasks]
            
            for future in as_completed(futures):
                future.result()
                self._maybe_save_snapshot(translated_data, dry_run)
    
    def _process_entry(self, key, value, translated_data, existing_translations):
        # Проверяем словарь
        if self.dictionary.has_translation(value):
            translation = self.dictionary.get_translation(value)
            with self.data_lock:
                translated_data[key] = translation
            self._update_progress(key, translation, "из словаря")
            return key, translation
            
        # Запрашиваем перевод у LLM
        translation = self.llm.translate(value)
        
        if translation:
            # Сохраняем в словарь
            self.dictionary.add_translation(value, translation)
            with self.data_lock:
                translated_data[key] = translation
            self._update_progress(key, translation, "новый")
            return key, translation
        else:
            # Оставляем оригинал
            with self.data_lock:
                translated_data[key] = value
            self._update_progress(key, value, "неудача", failed=True)
            return key, value
    
    def _update_progress(self, key, translation, status, failed=False):
        with self.progress_lock:
            self.completed_count += 1
            # Здесь можно отправить обновление через WebSocket
    
    def _maybe_save_snapshot(self, data, dry_run):
        with self.progress_lock:
            current = self.completed_count
        if current % self.save_interval == 0 or current == self.total_entries:
            if not dry_run:
                with self.data_lock:
                    snapshot = data.copy()
                save_json(snapshot, self.output_path)
                self.dictionary.save()