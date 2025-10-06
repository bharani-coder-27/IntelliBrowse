import json, csv, os

def save_json(data, filename="data/results.json"):
    os.makedirs("data", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_csv(data, filename="data/results.csv"):
    if not data:
        return

    os.makedirs("data", exist_ok=True)

    # Dynamically pick all keys from the first result
    fieldnames = list(data[0].keys())

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
