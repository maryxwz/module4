from pathlib import Path


try:
    from better_profanity import profanity as _bp  # type: ignore
except Exception:
    _bp = None

HERE = Path(__file__).resolve().parent
BADWORDS_DIR = HERE / "badwords"

_loaded = False
_words = set()


def _load_words_once():
    global _loaded, _words
    if _loaded:
        return
    for p in BADWORDS_DIR.glob("*.txt"):
        try:
            with p.open("r", encoding="utf-8") as f:
                for line in f:
                    w = line.strip()
                    if not w or w.startswith("#"):
                        continue
                    _words.add(w.lower())
        except Exception:
            continue

    if _bp:
        try:
            _bp.load_censor_words()
            if _words:
                _bp.add_censor_words(list(_words))
        except Exception:
            pass

    _loaded = True


def contains_profanity(text: str) -> bool:
    if not text:
        return False
    _load_words_once()
    if _bp:
        try:
            return bool(_bp.contains_profanity(text))
        except Exception:
            pass
    t = (text or "").lower()
    return any(w in t for w in _words)
