# app/utils/export_utils.py
import csv
import json
import io
from typing import List, Dict
from fastapi.responses import StreamingResponse

def export_to_json(data: List[Dict], filename: str):
    """Return a JSON file response directly from DB data."""
    buffer = io.BytesIO()
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    buffer.write(json_str.encode("utf-8"))
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/json", headers={
        "Content-Disposition": f"attachment; filename={filename}.json"
    })


def export_to_csv(data: List[Dict], filename: str):
    """Return a CSV file response directly from DB data."""
    if not data:
        data = [{}]  # empty CSV with header only
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    buffer.seek(0)
    return StreamingResponse(io.BytesIO(buffer.getvalue().encode()), media_type="text/csv", headers={
        "Content-Disposition": f"attachment; filename={filename}.csv"
    })
