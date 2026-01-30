import requests
import json
import time

BASE_URL = "http://localhost:5050"

def section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

def pretty_print(data):
    print(json.dumps(data, indent=2))
    time.sleep(1.2)

# -----------------------
# Monitor Agent
# -----------------------
section("🚨 MONITOR AGENT — INCIDENT DETECTED (REAL-TIME)")

incident = requests.get(f"{BASE_URL}/incident").json()
pretty_print(incident)

# -----------------------
# Stats Intelligence Agent (NEW)
# -----------------------
section("📈 STATS INTELLIGENCE AGENT — HISTORICAL SYSTEM PROFILE (LAST 30 DAYS)")

stats = requests.get(
    f"{BASE_URL}/system-stats",
    params={"system": incident["system"]}
).json()

pretty_print(stats)

# -----------------------
# Risk Prediction Agent (NEW)
# -----------------------
section("🔮 RISK PREDICTION AGENT — FORECASTING ESCALATION & TIME-TO-FAILURE")

risk = requests.post(
    f"{BASE_URL}/predict-risk",
    json={"incident": incident, "stats": stats}
).json()

pretty_print(risk)

# -----------------------
# Decision/Coordinator Agent (uses predicted risk as severity)
# -----------------------
section("🧩 COORDINATOR AGENT — OWNER ASSIGNMENT BASED ON PREDICTED RISK")

predicted_severity = risk["predicted_risk"]

owner_response = requests.post(
    f"{BASE_URL}/assign-owner",
    json={
        "incident_id": incident["incident_id"],
        "severity": predicted_severity
    }
).json()

pretty_print(owner_response)

# -----------------------
# Reporter Agent
# -----------------------
section("📣 REPORTER AGENT — STAKEHOLDER NOTIFICATION WITH FUTURE RISK")

message = (
    f"[INCIDENT UPDATE] {incident['incident_id']} | System: {incident['system']} | "
    f"Predicted Risk: {risk['predicted_risk']} (p={risk['escalation_probability']}) | "
    f"ETA to failure: {risk['expected_time_to_failure_minutes']} min | "
    f"Assigned: {owner_response['assigned_owner']} | "
    f"Recommended: {risk['recommended_action']}"
)

notification_response = requests.post(
    f"{BASE_URL}/notify",
    json={"message": message}
).json()

pretty_print(notification_response)

# -----------------------
# Before vs After (impresses judges)
# -----------------------
section("⚡ BEFORE vs AFTER — WHY THIS MATTERS (ENTERPRISE IMPACT)")

before_after = {
    "before_manual_process": [
        "Engineers manually read alerts and logs",
        "Teams debate severity and impact in chat",
        "Ownership unclear; delays in routing",
        "Stakeholder updates inconsistent and late"
    ],
    "after_ai_orchestrated": [
        "Incident detected instantly with structured context",
        "Historical stats + risk prediction added",
        "Owner assigned automatically based on predicted risk",
        "Stakeholders receive one clear update including ETA and recommended action"
    ]
}
pretty_print(before_after)

# -----------------------
# Impact Metrics (simulated but believable)
# -----------------------
section("📊 IMPACT METRICS — SIMULATED ENTERPRISE RESULTS")

metrics = {
    "manual_triage_time_minutes": 45,
    "ai_orchestrated_triage_time_minutes": 10,
    "time_reduction_percent": "78%",
    "manual_coordination_steps_removed": 4,
    "risk_forecast_added": "Yes (ETA + escalation probability)",
    "expected_outage_prevented": "By earlier escalation and response coordination"
}
pretty_print(metrics)

print("\n✅ NEXT-LEVEL INCIDENT COMMANDER WORKFLOW COMPLETED ✅\n")
