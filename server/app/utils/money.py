import re

def parse_price_to_int(price_text: str):
    if not price_text:
        return None
    try:
        clean = re.sub(r"[^\d]", "", price_text)
        return int(clean) if clean else None
    except Exception:
        return None
