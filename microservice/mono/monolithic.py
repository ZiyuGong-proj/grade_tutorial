"""Monolithic grade processing service.

This service loads a grade table, computes per-student totals and score
ranges, and exposes the results via a simple Flask API. It implements the
"single-container" deployment path required by the assignment.
"""
from __future__ import annotations

import csv
from pathlib import Path
from statistics import mean
from typing import Dict, List

from flask import Flask, jsonify

app = Flask(__name__)


BASE_DIR = Path(__file__).resolve().parent


def resolve_data_path() -> Path:
    """Locate the grade CSV regardless of whether the file is run in-place or inside a container."""
    candidate = BASE_DIR / "data" / "Grade Table.csv"
    if candidate.exists():
        return candidate
    return BASE_DIR.parent / "data" / "Grade Table.csv"


def load_grades() -> List[Dict]:
    """Load the grade table from CSV into a structured list.

    Returns a list of entries with a student name and a mapping of their
    scores. Numeric values are parsed as floats so that later calculations are
    straightforward.
    """
    records: List[Dict] = []
    data_path = resolve_data_path()
    with data_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            student_key = next((key for key in row if key.lower() in {"student", "name"}), "student")
            scores = {
                key: float(value)
                for key, value in row.items()
                if key != student_key and value not in {None, ""}
            }
            records.append({"student": row[student_key], "scores": scores})
    return records


def calculate_metrics(records: List[Dict]) -> List[Dict]:
    """Compute total and score-range metrics for each student."""
    results: List[Dict] = []
    for record in records:
        numeric_scores = list(record["scores"].values())
        total = sum(numeric_scores)
        score_range = max(numeric_scores) - min(numeric_scores) if numeric_scores else 0
        results.append(
            {
                "student": record["student"],
                "total": total,
                "max_score_difference": score_range,
            }
        )
    return results


def summarize_metrics(metrics: List[Dict]) -> Dict:
    """Aggregate the computed metrics into a compact statistics table."""
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
    return jsonify({"status": "healthy", "service": "monolithic"}), 200


@app.route("/grades", methods=["GET"])
def get_grades():
    return jsonify(load_grades()), 200


@app.route("/metrics", methods=["GET"])
def get_metrics():
    records = load_grades()
    metrics = calculate_metrics(records)
    return jsonify(metrics), 200


@app.route("/metrics/summary", methods=["GET"])
def get_summary():
    records = load_grades()
    metrics = calculate_metrics(records)
    return jsonify(summarize_metrics(metrics)), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
