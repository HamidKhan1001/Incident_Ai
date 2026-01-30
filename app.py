from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)

# -----------------------
# Enterprise Incident Data
# -----------------------

INCIDENTS = [
    {
        "incident_id": "INC-9001",
        "system": "Payments API",
        "description": "High latency and increased 5xx errors",
        "business_impact": "Customer checkout failures",
        "signals": ["latency_spike", "error_rate_high"]
    },
    {
        "incident_id": "INC-9002",
        "system": "Order Processing Service",
        "description": "Database connection pool exhausted",
        "business_impact": "Orders intermittently failing",
        "signals": ["db_timeout", "pool_exhausted"]
    }
]

OWNERS = {
    "Low": "Application Support Team",
    "Medium": "Backend Engineering Team",
    "High": "SRE On-Call Team",
    "Critical": "Incident Response Commander"
}

# -----------------------
# Simulated historical stats (30-day window)
# This is what makes it feel enterprise + data-informed
# -----------------------

SYSTEM_HISTORY = {
    "Payments API": {
        "past_30_days_incidents": 7,
        "critical_incident_rate": 0.42,
        "avg_resolution_time_minutes": 38,
        "top_causes": ["Traffic spikes", "Downstream dependency errors", "Cache saturation"],
        "peak_risk_hours": ["11:00-14:00", "18:00-21:00"]
    },
    "Order Processing Service": {
        "past_30_days_incidents": 4,
        "critical_incident_rate": 0.25,
        "avg_resolution_time_minutes": 44,
        "top_causes": ["DB pool exhaustion", "Slow queries", "Lock contention"],
        "peak_risk_hours": ["09:00-11:00", "16:00-19:00"]
    }
}

# -----------------------
# Utility: risk scoring (simple but strong for hackathon)
# -----------------------

def compute_escalation_probability(incident, stats):
    """
    Rule + stats based probability.
    This is 'proper' for hackathon: explainable, deterministic, believable.
    """
    prob = 0.15

    # Stats influence
    prob += min(stats.get("critical_incident_rate", 0.2), 0.7) * 0.55
    prob += min(stats.get("past_30_days_incidents", 0) / 10.0, 0.5) * 0.25

    # Signals influence
    signals = set(incident.get("signals", []))
    if "error_rate_high" in signals:
        prob += 0.25
    if "latency_spike" in signals:
        prob += 0.15
    if "db_timeout" in signals or "pool_exhausted" in signals:
        prob += 0.20

    # Business impact keywords
    impact = (incident.get("business_impact") or "").lower()
    if "checkout" in impact or "customer" in impact:
        prob += 0.15
    if "intermittently" in impact:
        prob += 0.05

    # clamp
    prob = max(0.0, min(prob, 0.99))
    return prob


def probability_to_risk(prob):
    if prob >= 0.80:
        return "Critical"
    if prob >= 0.60:
        return "High"
    if prob >= 0.35:
        return "Medium"
    return "Low"


def estimate_time_to_failure_minutes(prob):
    """
    Lower time as probability rises (simple, believable).
    """
    if prob >= 0.80:
        return 10
    if prob >= 0.60:
        return 20
    if prob >= 0.35:
        return 45
    return 120


# -----------------------
# API Endpoints (existing + new)
# -----------------------

@app.route("/", methods=["GET"])
def home():
    return {
        "service": "Enterprise AI Incident Commander",
        "status": "running"
    }


@app.route("/incident", methods=["GET"])
def get_incident():
    incident = random.choice(INCIDENTS)
    incident["timestamp"] = datetime.utcnow().isoformat()
    return jsonify(incident)


@app.route("/assign-owner", methods=["POST"])
def assign_owner():
    data = request.json
    severity = data.get("severity", "Medium")
    incident_id = data.get("incident_id")

    owner = OWNERS.get(severity, "Backend Engineering Team")

    return jsonify({
        "incident_id": incident_id,
        "severity": severity,
        "assigned_owner": owner,
        "assigned_at": datetime.utcnow().isoformat()
    })


@app.route("/notify", methods=["POST"])
def notify_stakeholders():
    data = request.json
    message = data.get("message")

    return jsonify({
        "status": "notification_sent",
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}


# -----------------------
# NEW: Stats endpoint (historical intelligence)
# -----------------------
@app.route("/system-stats", methods=["GET"])
def system_stats():
    system = request.args.get("system", "")
    stats = SYSTEM_HISTORY.get(system)

    if not stats:
        # Return a safe default if unknown system
        stats = {
            "past_30_days_incidents": 2,
            "critical_incident_rate": 0.20,
            "avg_resolution_time_minutes": 40,
            "top_causes": ["Unknown"],
            "peak_risk_hours": ["Unknown"]
        }

    return jsonify({
        "system": system,
        "window_days": 30,
        **stats
    })


# -----------------------
# NEW: Risk prediction endpoint (future breaking prediction)
# -----------------------
@app.route("/predict-risk", methods=["POST"])
def predict_risk():
    data = request.json or {}
    incident = data.get("incident", {})
    stats = data.get("stats", {})

    prob = compute_escalation_probability(incident, stats)
    risk = probability_to_risk(prob)
    eta = estimate_time_to_failure_minutes(prob)

    recommendation = "Monitor and re-check in 30 minutes"
    if risk == "Medium":
        recommendation = "Assign to engineering and begin diagnostics"
    elif risk == "High":
        recommendation = "Escalate to SRE on-call and prepare incident channel"
    elif risk == "Critical":
        recommendation = "Page Incident Commander and notify leadership immediately"

    return jsonify({
        "predicted_risk": risk,
        "escalation_probability": round(prob, 2),
        "expected_time_to_failure_minutes": eta,
        "recommended_action": recommendation,
        "explainability": {
            "based_on": [
                "historical critical incident rate",
                "incident frequency",
                "signals and business impact"
            ]
        },
        "generated_at": datetime.utcnow().isoformat()
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
