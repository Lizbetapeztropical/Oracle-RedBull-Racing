import json

from pathlib import Path
from pymongo import MongoClient

# =========================
# CONFIG
# =========================

MONGO_URI = "mongodb://admin:oracle@localhost:27017/"

DB_NAME = "oracle_redbull_racing"

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_FOLDER = BASE_DIR / "DATA"

BATCH_SIZE = 10000

# =========================
# CONNECT
# =========================

client = MongoClient(MONGO_URI)

db = client[DB_NAME]

# =========================
# GET FILES
# =========================
print("SCRIPT LOCATION:")
print(Path(__file__).resolve())

print("\nBASE_DIR:")
print(BASE_DIR)

print("\nDATASET_FOLDER:")
print(DATASET_FOLDER)

print("\nDOES DATASET FOLDER EXIST?")
print(DATASET_FOLDER.exists())

json_files = list(DATASET_FOLDER.glob("*.json"))
ndjson_files = list(DATASET_FOLDER.glob("*.ndjson"))

all_files = json_files + ndjson_files

print(f"Found {len(all_files)} files")

# =========================
# PROCESS FILES
# =========================

for file in all_files:

    print("\n------------------------")
    print(f"Processing: {file.name}")

    # Collection name = filename without extension
    collection_name = file.stem

    collection = db[collection_name]

    # Optional: clear collection first
    collection.delete_many({})

    # =====================
    # JSON FILES
    # =====================

    if file.suffix == ".json":

        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # If JSON is a single object
        if isinstance(data, dict):
            data = [data]

        total_docs = len(data)

        print(f"Documents found: {total_docs}")

        # Insert in batches
        for start in range(0, total_docs, BATCH_SIZE):

            batch = data[start:start + BATCH_SIZE]

            collection.insert_many(batch)

            print(
                f"Inserted batch "
                f"{start} - {start + len(batch)}"
            )

    # =====================
    # NDJSON FILES
    # =====================

    elif file.suffix == ".ndjson":

        batch = []

        total_docs = 0

        with open(file, "r", encoding="utf-8") as f:

            for line in f:

                line = line.strip()

                if not line:
                    continue

                batch.append(json.loads(line))

                if len(batch) >= BATCH_SIZE:

                    collection.insert_many(batch)

                    total_docs += len(batch)

                    print(f"Inserted {total_docs} documents...")

                    batch = []

        # Insert remaining docs
        if batch:

            collection.insert_many(batch)

            total_docs += len(batch)

        print(f"Total inserted: {total_docs}")

    print(f"Finished collection: {collection_name}")

print("\nAll datasets uploaded successfully!")