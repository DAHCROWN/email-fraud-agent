import csv
import os
import uuid
from pathlib import Path
from typing import List, Dict, Any

from pinecone import Pinecone

from rag.embeddings import PineconeEmbeddingEngine as EmbeddingEngine
from models.datasets import NigerianFraudDataset, SpamAssasinDataset, LingDataset, EmailRecord


# -----------------------------
# CONFIG
# -----------------------------
DATASET_DIR = "../datasets/"

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = "fraud-email-index"


# -----------------------------
# DATASET REGISTRY
# -----------------------------
DATASET_REGISTRY = {
    "nigerian_fraud": {
        "model": NigerianFraudDataset,
        "path": "datasets/nigerian_fraud.csv",
    },
    "spam_assassin": {
        "model": SpamAssasinDataset,
        "path": "datasets/spam_assassin.csv",
    },
    "ling_spam": {
        "model": LingDataset,
        "path": "datasets/ling_spam.csv",
    },
    # Generic fallback dataset
    "generic": {
        "model": EmailRecord,
        "path": None,  # When loading automatically from folder
    }
}


# -----------------------------
# Load + Validate CSV Records
# -----------------------------
def load_csv_records() -> List[Any]:
    dataset_path = Path(DATASET_DIR)
    validated = []

    # Load datasets explicitly defined in registry
    for name, cfg in DATASET_REGISTRY.items():
        model = cfg["model"]
        file_path = cfg["path"]

        if file_path:
            fp = Path(file_path)
            if fp.exists():
                print(f"[INGEST] Loading dataset '{name}' from {fp}...")
                with open(fp, newline='', encoding="utf-8", errors="ignore") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            validated.append(model(**row))
                        except Exception as e:
                            print(f"[WARN] Skipping invalid row in {name}: {e}")

    # Auto‑load any other CSV in datasets folder using the generic EmailRecord schema
    for file in dataset_path.glob("*.csv"):
        # skip files already identified in registry
        if any(cfg["path"] == str(file) for cfg in DATASET_REGISTRY.values()):
            continue

        print(f"[INGEST] Auto-loading generic CSV: {file}")
        with open(file, newline='', encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    validated.append(EmailRecord(**row))
                except Exception as e:
                    print(f"[WARN] Skipping invalid generic row: {e}")

    print(f"[INGEST] Loaded {len(validated)} validated rows from all datasets.")
    return validated


# -----------------------------
# Build Pinecone Datapoints
# -----------------------------
def build_pinecone_datapoints(records: List[Any], embeddings: List[List[float]]):
    datapoints = []

    for record, vector in zip(records, embeddings):
        datapoints.append({
            "id": str(uuid.uuid4()),
            "values": vector,
            "metadata": {
                "sender": record.sender,
                "receiver": record.receiver,
                "subject": record.subject,
                "body": record.body,
                "urls": record.urls,
                "label": record.label or "",
            }
        })

    return datapoints


# -----------------------------
# Upload to Pinecone Vector Store
# -----------------------------
def upload_to_pinecone(datapoints: List[Dict[str, Any]]):
    print("[PINECONE] Uploading vectors...")

    pc = Pinecone(api_key=PINECONE_API_KEY)

    if not pc.has_index(PINECONE_INDEX_NAME):
        print("[PINECONE] Index does not exist, creating...")
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=len(datapoints[0]["values"]),
            metric="cosine",
            spec={"serverless": {"cloud": "aws", "region": "us-east-1"}}
        )

    index = pc.Index(PINECONE_INDEX_NAME)
    index.upsert(vectors=datapoints)

    print("[PINECONE] Upload successful.")


# -----------------------------
# Main Ingest Function
# -----------------------------
def ingest():
    print("[INGEST] Starting...")

    # Step 1 — Load + validate CSV
    records = load_csv_records()

    # Step 2 — Embed bodies
    embedder = EmbeddingEngine()
    print("[INGEST] Generating embeddings...")
    embeddings = embedder.embed([record.body for record in records])

    # Step 3 — Build datapoints
    datapoints = build_pinecone_datapoints(records, embeddings)

    # Step 4 — Upload to Pinecone Vector Store
    upload_to_pinecone(datapoints)

    print("[INGEST] Done!")


if __name__ == "__main__":
    ingest()