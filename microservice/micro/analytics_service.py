"""Analytics service that computes totals and score ranges for each student."""
from __future__ import annotations

import os
from statistics import mean
from typing import Dict, List

import requests
from flask import Flask, jsonify
from requests import RequestException

app = Flask(__name__)
DATA_SERVICE_URL = os.getenv("DATA_SERVICE_URL", "http://localhost:5001")


def fetch_grades() -> List[Dict]:
    try:
        response = requests.get(f"{DATA_SERVICE_URL}/grades", timeout=5)
        response.raise_for_status()
        return response.json()
    except RequestException as exc:  # noqa: BLE001
        raise RuntimeError("Data service unavailable") from exc


def calculate_metrics(records: List[Dict]) -> List[Dict]:
    metrics: List[Dict] = []
    for record in records:
        numeric_scores = list(record["scores"].values())
        total = sum(numeric_scores)
        score_range = max(numeric_scores) - min(numeric_scores) if numeric_scores else 0
        metrics.append(
            {
                "student": record["student"],
                "total": total,
                "max_score_difference": score_range,
            }
        )
    return metrics


def summarize_metrics(metrics: List[Dict]) -> Dict:
    totals = [entry["total"] for entry in metrics]
    score_ranges = [entry["max_score_difference"] for entry in metrics]

    return {
        "total": {
            "average": mean(totals),
            "highest": max(totals),
            "lowest": min(totals),
        },
        "max_score_difference": {
            "average": mean(score_ranges),
            "highest": max(score_ranges),
            "lowest": min(score_ranges),
        },
    }


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "service": "analytics_service"}), 200


@app.route("/metrics", methods=["GET"])
def get_metrics():
    try:
        records = fetch_grades()
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 503

    metrics = calculate_metrics(records)
    return jsonify(metrics), 200


@app.route("/metrics/summary", methods=["GET"])
def get_summary():
    try:
        records = fetch_grades()
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 503

    metrics = calculate_metrics(records)
    return jsonify(summarize_metrics(metrics)), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5002)
