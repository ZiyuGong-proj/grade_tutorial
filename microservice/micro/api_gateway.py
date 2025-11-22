"""API gateway that coordinates the grade microservices."""
from __future__ import annotations

import os

import requests
from flask import Flask, jsonify
from requests import RequestException

app = Flask(__name__)

DATA_SERVICE_URL = os.getenv("DATA_SERVICE_URL", "http://localhost:5001")
ANALYTICS_SERVICE_URL = os.getenv("ANALYTICS_SERVICE_URL", "http://localhost:5002")


def safe_proxy(url: str):
    try:
        response = requests.get(url, timeout=5)
        return jsonify(response.json()), response.status_code
    except RequestException as exc:  # noqa: BLE001
        return jsonify({"error": str(exc)}), 503


@app.route("/health", methods=["GET"])
def health_check():
    health_status = {}
    for name, url in {
        "data_service": DATA_SERVICE_URL,
        "analytics_service": ANALYTICS_SERVICE_URL,
    }.items():
        try:
            response = requests.get(f"{url}/health", timeout=3)
            health_status[name] = response.json()
        except Exception as exc:  # noqa: BLE001
            health_status[name] = {"status": "unhealthy", "error": str(exc)}
    return jsonify(health_status), 200


@app.route("/grades", methods=["GET"])
def grades():
    return safe_proxy(f"{DATA_SERVICE_URL}/grades")


@app.route("/metrics", methods=["GET"])
def metrics():
    return safe_proxy(f"{ANALYTICS_SERVICE_URL}/metrics")


@app.route("/metrics/summary", methods=["GET"])
def metrics_summary():
    return safe_proxy(f"{ANALYTICS_SERVICE_URL}/metrics/summary")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
