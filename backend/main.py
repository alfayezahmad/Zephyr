import os
import json
import logging
import paho.mqtt.publish as mqtt_publish
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from live_ingestion import fetch_live_node_data, assign_grap_stage
from ml_engine import ZephyrMLEngine
from vrp_optimizer import calculate_optimal_dispatch
from aws_agent import ZephyrDiagnosticAgent
from aws_audit import AWSServiceBridge

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Zephyr.API")

app = FastAPI(
    title="Zephyr Cyber-Physical Air Quality Engine",
    description="AWS-Native Digital Twin for Spatio-Temporal PM2.5 Forecasting and GRAP Statutory Mitigation",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ml_engine = ZephyrMLEngine()
diagnostic_agent = ZephyrDiagnosticAgent()
aws_bridge = AWSServiceBridge()

HUB_COORDS = [26.8467, 80.9462] # Central Municipal Hub (Lucknow)
SIMULATE_SPIKE_ACTIVE = False
MQTT_HOST = os.environ.get("MQTT_BROKER_HOST", "localhost")
MQTT_PORT = int(os.environ.get("MQTT_BROKER_PORT", 1883))
MQTT_TOPIC = os.environ.get("MQTT_TOPIC_SUB", "zephyr/commands/dispatch")

@app.get("/api/aws/status")
def get_aws_status():
    """Returns real-time AWS Cloud & LocalStack infrastructure status."""
    return aws_bridge.get_service_status()

@app.post("/api/simulate_spike")
def trigger_spike_simulation():
    global SIMULATE_SPIKE_ACTIVE
    SIMULATE_SPIKE_ACTIVE = True
    
    # 1. Fire off immediate MQTT command for the edge actuator (AWS IoT Core / Mosquitto)
    payload = {
        "grap_stage": "Stage III",
        "action": "PRIORITY_1_MIST_CANNON_DISPATCH",
        "authority": "CAQM_STATUTORY_RULEBOOK",
        "aws_source": "Zephyr_Emergency_Dispatcher"
    }
    try:
        mqtt_publish.single(
            MQTT_TOPIC,
            payload=json.dumps(payload),
            hostname=MQTT_HOST,
            port=MQTT_PORT
        )
        logger.info(f"Published downlink command to MQTT at {MQTT_HOST}:{MQTT_PORT}")
    except Exception as e:
        logger.warning(f"MQTT publish skipped (host={MQTT_HOST}): {e}")
        
    # 2. Trigger Amazon SNS emergency dispatch broadcast
    aws_bridge.publish_emergency_sns(
        stage="Stage III (Severe)",
        worst_station="Talkatora Industrial Area",
        pm25=345.0,
        action="PRIORITY_1_MIST_CANNON_DISPATCH"
    )

    # 3. Log to Amazon DynamoDB audit trail
    aws_bridge.log_statutory_action(
        node_station="Talkatora Industrial Area",
        pm25=345.0,
        grap_stage="Stage III",
        action="PRIORITY_1_MIST_CANNON_DISPATCH"
    )
        
    return {
        "status": "success",
        "message": "Simulated atmospheric PM2.5 spike engaged. Hardware actuation and AWS SNS emergency dispatched.",
        "aws_services_notified": ["AWS IoT Core / MQTT", "Amazon SNS", "Amazon DynamoDB"]
    }

@app.post("/api/reset_spike")
def reset_spike_simulation():
    global SIMULATE_SPIKE_ACTIVE
    SIMULATE_SPIKE_ACTIVE = False
    return {
        "status": "success",
        "message": "Atmospheric spike cleared. Restored live sensor telemetry."
    }

@app.get("/api/forecast")
def get_spatial_forecast():
    # 1. Fetch Live Telemetry Data
    nodes = fetch_live_node_data()
    
    global SIMULATE_SPIKE_ACTIVE
    if SIMULATE_SPIKE_ACTIVE:
        for node in nodes:
            node["pm25"] = 345.0 # Spike to trigger Stage III/IV
    
    # 2. PyTorch ST-GNN Inference & XAI for the full spatio-temporal graph
    ml_result = ml_engine.predict_with_xai(nodes)
    predictions = ml_result["predictions"]
    worst_node_shap = ml_result["xai_attributions"]
    
    processed_nodes = []
    critical_nodes = []
    
    # 3. Zip predictions back into the payload
    for idx, node in enumerate(nodes):
        predicted_pm25 = float(predictions[idx])
        node["pm25"] = round(predicted_pm25, 1)
        
        # Statutory GRAP assignment
        grap_stage, action = assign_grap_stage(predicted_pm25)
        node["grap_stage"] = grap_stage
        node["prescribed_action"] = action
        
        # Filter Nodes for VRP Fleet Dispatch (CAQM Stage I/II/III/IV: > 60 µg/m³)
        if predicted_pm25 > 60.0:
            node["needs_dispatch"] = True
            critical_nodes.append(node)
            # Log statutory dispatch event to DynamoDB
            aws_bridge.log_statutory_action(
                node_station=node["station"],
                pm25=predicted_pm25,
                grap_stage=grap_stage,
                action=action
            )
        else:
            node["needs_dispatch"] = False
            
        processed_nodes.append(node)

    avg_pm25 = round(sum(n["pm25"] for n in processed_nodes) / len(processed_nodes), 1)

    # 4. OR-Tools Constrained VRP Optimization
    # Route all active statutory nodes; if all pristine, route top-2 for routine depot patrol
    routed_nodes = critical_nodes if len(critical_nodes) > 0 else sorted(processed_nodes, key=lambda n: n["pm25"], reverse=True)[:2]
    routes = calculate_optimal_dispatch(HUB_COORDS, routed_nodes)

    result_payload = {
        "city": "Lucknow",
        "timestamp_horizon": "Real-Time / Next 24 Hours",
        "city_mean_pm25": avg_pm25,
        "nodes": processed_nodes,
        "routes": routes,
        "shap_attributions": worst_node_shap,
        "dispatch_hub": {
            "lat": HUB_COORDS[0],
            "lon": HUB_COORDS[1],
            "name": "Central Municipal Depot",
        },
        "aws_infrastructure": aws_bridge.get_service_status()
    }

    # 5. Archive snapshot to Amazon S3 data lake asynchronously
    aws_bridge.archive_telemetry_snapshot(result_payload)

    return result_payload

@app.get("/api/agent_briefing")
def get_agent_briefing():
    """
    Invokes the Amazon Bedrock Diagnostic Agent to synthesize the ST-GNN matrix
    into an executive briefing for the Municipal Commissioner.
    """
    try:
        forecast_data = get_spatial_forecast()
        nodes = forecast_data["nodes"]
        city_mean = forecast_data["city_mean_pm25"]
    except Exception as e:
        return {
            "briefing": f"Agent error fetching telemetry: {str(e)}",
            "provider": "Error Handler",
            "status": "error"
        }

    return diagnostic_agent.generate_briefing(nodes, city_mean)
