import os, json, csv, time
from typing import List, Dict

def normalize_title(title: str) -> str:
    if not title:
        return ""
    return " ".join(title.lower().split())

def dedupe(items: List[Dict]) -> List[Dict]:
    seen = set()
    out: List[Dict] = []
    for x in items:
        key = normalize_title(x.get("title","")) or x.get("link","")
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(x)
    return out

def sort_by_price(items: List[Dict]) -> List[Dict]:
    return sorted(items, key=lambda r: (r.get("price_value") or 10**9, r.get("title","").lower()))

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def timestamp() -> str:
    return time.strftime("%Y%m%d_%H%M%S")

def save_json(items: List[Dict], out_dir: str, name_prefix: str) -> str:
    ensure_dir(out_dir)
    path = os.path.join(out_dir, f"{name_prefix}_{timestamp()}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    return path

def save_csv(items: List[Dict], out_dir: str, name_prefix: str) -> str:
    ensure_dir(out_dir)
    path = os.path.join(out_dir, f"{name_prefix}_{timestamp()}.csv")
    if not items:
        # create empty file with headers
        headers = ["title","price","price_value","rating","link","site"]
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
        return path
    # include 'site' if present; else compute
    headers = sorted({k for x in items for k in x.keys()})
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in items:
            writer.writerow(row)
    return path
