"""Data service responsible for serving the grade table to other services."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List

from flask import Flask, jsonify

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent


def resolve_data_path() -> Path:
    candidate = BASE_DIR / "data" / "Grade Table.csv"
    if candidate.exists():
        return candidate
    return BASE_DIR.parent / "data" / "Grade Table.csv"


def load_grades() -> List[Dict]:
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


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "service": "data_service"}), 200


@app.route("/grades", methods=["GET"])
def list_grades():
    return jsonify(load_grades()), 200


@app.route("/grades/<student>", methods=["GET"])
def get_student(student: str):
    for record in load_grades():
        if record["student"].lower() == student.lower():
            return jsonify(record), 200
    return jsonify({"error": f"Student {student} not found"}), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
