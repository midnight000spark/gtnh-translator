import json
import hashlib
from pathlib import Path
from difflib import SequenceMatcher

class TranslationDictionary:
    def __init__(self, path):
        self.path = Path(path)
        self.data = self._load()
        self.hash_cache = {}
    
    def _load(self):
        if self.path.exists():
            try:
                with open(self.path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2, sort_keys=True)
    
    def _get_hash(self, text):
        if text not in self.hash_cache:
            self.hash_cache[text] = hashlib.md5(text.encode()).hexdigest()
        return self.hash_cache[text]
    
    def has_translation(self, key):
        key_hash = self._get_hash(key)
        return key_hash in self.data or key in self.data
    
    def get_translation(self, key):
        key_hash = self._get_hash(key)
        return self.data.get(key_hash) or self.data.get(key)
    
    def add_translation(self, key, value):
        key_hash = self._get_hash(key)
        self.data[key_hash] = value
        self.data[key] = value
    
    def find_similar(self, text, threshold=0.8):
        similar = []
        for original_text, translation in self.data.items():
            if isinstance(original_text, str) and not original_text.startswith('§'):
                similarity = SequenceMatcher(None, text.lower(), original_text.lower()).ratio()
                if similarity >= threshold:
                    similar.append((original_text, translation, similarity))
        return sorted(similar, key=lambda x: x[2], reverse=True)[:5]