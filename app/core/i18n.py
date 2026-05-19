import json
from pathlib import Path

LOCALES_DIR = Path(__file__).parent.parent / "locales"

_translations = {}

def load_translations():
    global _translations
    if not LOCALES_DIR.exists():
        return
    
    for file in LOCALES_DIR.glob("*.json"):
        lang = file.stem
        with open(file, "r", encoding="utf-8") as f:
            _translations[lang] = json.load(f)

def get_translator(lang: str):
    if not _translations:
        load_translations()
        
    translations = _translations.get(lang, {})
    
    def translate(text: str) -> str:
        return translations.get(text, text)
        
    return translate
