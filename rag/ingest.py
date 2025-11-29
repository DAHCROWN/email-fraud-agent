# rag/ingest.py

import csv
import uuid
from pathlib import Path
from typing import List, Dict, Any

from google.cloud import aiplatform
from google.cloud.aiplatform.vector_matching import Vector
from google.cloud.aiplatform_v1.types import (
    IndexDatapoint,
)

from embeddings import EmbeddingEngine
from models.datasets import NigerianFraudDataset, SpamAssasinDataset, LingDataset, EmailRecord


# -----------------------------
# CONFIG
# -----------------------------
DATASET_DIR = "datasets/"

# TODO: fill these with your values
VERTEX_INDEX_ID = "YOUR_INDEX_ID"
VERTEX_INDEX_ENDPOINT_ID = "YOUR_INDEX_ENDPOINT_ID"
VERTEX_REGION = "us-central1"
PROJECT_ID = "YOUR_PROJECT_ID"


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
# Build Vertex Datapoints
# -----------------------------
def build_vertex_datapoints(records: List[Any], embeddings: List[List[float]]):
    datapoints = []

    for record, vector in zip(records, embeddings):
        datapoints.append(
            IndexDatapoint(
                datapoint_id=str(uuid.uuid4()),
                feature_vector=vector,
                restricts=[],  # Add filters later if needed
                attributes={
                    "sender": record.sender,
                    "receiver": record.receiver,
                    "subject": record.subject,
                    "body": record.body,
                    "urls": str(record.urls),
                    "label": record.label or "",
                }
            )
        )
    return datapoints


# -----------------------------
# Upload to Vertex Vector Store
# -----------------------------
def upload_to_vertex(datapoints: List[IndexDatapoint]):
    print("[VERTEX] Uploading vectors...")

    index = aiplatform.MatchingEngineIndex(index_name=VERTEX_INDEX_ID)
    index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
        index_endpoint_name=VERTEX_INDEX_ENDPOINT_ID
    )

    # Upsert datapoints
    index.upsert_datapoints(datapoints)
    print("[VERTEX] Upload successful.")


# -----------------------------
# Main Ingest Function
# -----------------------------
def ingest():
    print("[INGEST] Starting...")

    # Init Vertex
    aiplatform.init(project=PROJECT_ID, location=VERTEX_REGION)

    # Step 1 — Load + validate CSV
    records = load_csv_records()

    # Step 2 — Embed bodies
    embedder = EmbeddingEngine()
    print("[INGEST] Generating embeddings...")
    embeddings = embedder.embed([record.body for record in records])

    # Step 3 — Build datapoints
    datapoints = build_vertex_datapoints(records, embeddings)

    # Step 4 — Upload to Vertex Vector Store
    upload_to_vertex(datapoints)

    print("[INGEST] Done!")


if __name__ == "__main__":
    ingest()