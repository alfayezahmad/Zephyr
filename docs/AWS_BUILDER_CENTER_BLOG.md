# Building Zephyr: How We Closed the Cyber-Physical Loop on Urban Air Quality with Amazon Bedrock, ST-GNNs, and LocalStack

*Published on AWS Builder Center as part of Bharat Builds Tour — Environmental Hacks (Event 02: Track 01 - Air)*

---

## 1. The Problem: The Delayed Air Quality Response Gap

Every October through February, northern Indian cities like Delhi, Lucknow, and Kanpur face atmospheric inversions that trap severe particulate matter (PM2.5) near the ground. The Indian central government instituted the **Graded Response Action Plan (GRAP)**—a statutory rulebook classifying pollution severity into four stages with mandated emergency interventions: from mechanized road sweeping (Stage I) to emergency anti-smog mist cannon deployment (Stage III) and diesel vehicle bans (Stage IV).

However, current municipal enforcement suffers from a fundamental **delayed response gap**:
1. Static air monitoring stations record high pollution.
2. The data sits on legacy administrative dashboards.
3. Bureaucratic reviews take hours to authorize mitigation vehicle dispatches.
4. **By the time the mist cannons reach the affected zone, the pollution plume has already advected (drifted) downwind into neighboring residential wards and schools.**

We built **Zephyr** to solve this. Instead of being a passive dashboard, Zephyr is a **Cyber-Physical Digital Twin** that models atmospheric pollution propagation in advance and autonomously actuates physical mitigation assets in the real world.

---

## 2. The Architecture: Where AWS Fits

Zephyr unifies deep learning, operations research, cloud infrastructure, and embedded hardware into a resilient closed-loop system:

```
                        [Open-Meteo REST APIs]
                                  │ (Live PM2.5, Wind, Temp, CO)
                                  ▼
[Captum XAI Engine] <── [PyTorch Geometric ST-GNN]
(Integrated Gradients)            │ (24h Spatial Prediction Matrix)
        ┌─────────────────────────┴────────────────────────┐
        ▼                                                  ▼
[Amazon Bedrock Agent]                           [Google OR-Tools VRP]
(Claude 3.5 Sonnet Diagnostics)                 (Constrained Fleet Routing)
        │                                                  │
        ├─────────────────────────┬────────────────────────┘
        ▼                         ▼
[Streamlit 3D Command Center]  [Statutory Dispatch Engine]
(PyDeck Digital Twin / SCADA)     │
                                  ├──> [Amazon DynamoDB] (Immutable GRAP Audit Trail)
                                  ├──> [Amazon S3] (Telemetry Snapshots Lake)
                                  ├──> [Amazon SNS] (Municipal Emergency Broadcasts)
                                  └──> [AWS IoT Core / MQTT] ──> [ESP32 Edge Actuators]
                                                                 (Relays & Mist Cannons)
```

### AWS Stack Overview
- **Amazon Bedrock (Claude 3.5 Sonnet)**: Analyzes the high-dimensional spatial prediction matrix to generate executive diagnostic briefings for the City Commissioner.
- **LocalStack (AWS Open Source)**: Emulates Amazon S3, DynamoDB, and SNS locally, enabling zero-cloud-bill testing during municipal prototyping.
- **Amazon DynamoDB**: Stores an auditable ledger of every automated GRAP intervention.
- **Amazon S3**: Ingests continuous spatio-temporal telemetry snapshots for historical re-training.
- **Amazon SNS & AWS IoT Core**: Dispatches real-time downlinks to edge microcontrollers (ESP32) commanding mist cannons and high-pressure water main valves.

---

## 3. The Core Machine Learning: Wind-Modulated Graph Neural Networks

Particulate pollution does not disperse uniformly; it advects along atmospheric wind corridors. We modeled the urban sensor topology of Lucknow (5 monitoring nodes: Talkatora, Lalbagh, Gomti Nagar, Alambagh, and Kalyanpur) as a directed graph **G = (V, E)**, where nodes **V** represent municipal monitoring stations and edges **E** represent atmospheric transport corridors.

Using **PyTorch Geometric**, we designed a custom `WindAdvectionGNN` where wind velocity vectors (speed and direction) dynamically modulate spatial message passing between monitoring nodes:

```python
# 1. Message Step: Aggregate features from upwind neighbors j, modulated by wind vector e_ji
message_ji = F.relu(linear_msg(torch.cat([h_j, linear_edge(e_ji)], dim=-1)))

# 2. Update Step: Update station i state by combining local features with advected plume
h_i_next = F.relu(linear_update(torch.cat([h_i, torch.sum(message_ji, dim=0)], dim=-1)))
```

### Explainable AI (XAI) with PyTorch Captum
Municipal orders that enforce vehicle bans or reroute public assets must be legally defensible. To eliminate the "black-box" dilemma, we integrated **PyTorch Captum** using `IntegratedGradients`. For every spike forecast, the system computes the exact percentage contribution of each feature (e.g., PM2.5 Lag, Temperature Inversion, Carbon Monoxide, Wind Shear).

---

## 4. What Fought Back: Technical Hurdles & Breakthroughs

Building a cyber-physical system under hackathon timeframes pushed us into several tough engineering battles:

### Challenge 1: Calculating Gradients on Dynamic Message-Passing Layers
Captum's `IntegratedGradients` expects continuous input tensors. When computing feature attributions across graph structures with dynamic edge attributes, computing gradients through PyG's `propagate()` function occasionally triggered shape mismatch errors during baseline interpolation.  
**Solution**: We isolated the node feature tensor as the target baseline while fixing the normalized adjacency matrix, allowing Captum to calculate exact input-level SHAP attributions without destabilizing the spatial graph topology.

### Challenge 2: Operations Research vs. Live Latency
Solving the Vehicle Routing Problem (VRP) using Google OR-Tools integer programming can become compute-intensive if the distance matrix is recalculated per request.  
**Solution**: We pre-cached the Haversine distance matrix of Lucknow's municipal corridors and dynamically pruned candidate destination nodes using a binary threshold filter (`PM2.5 > 120 µg/m³`), reducing VRP optimization time to under 15ms.

### Challenge 3: Edge Resilience Under Cloud Disconnect
In physical municipal deployments, Wi-Fi connectivity during severe weather can be intermittent. If an ESP32 drops its MQTT link while spraying high-pressure water, it could cause flooding.  
**Solution**: We built local state validation into the edge daemon. If the MQTT broker downlink is interrupted for more than 5 seconds, the ESP32 automatically transitions into a fail-safe `STANDBY` state, setting servo valves back to 0°.

---

## 5. The Cyber-Physical Result

When a PM2.5 spike is injected or detected:
1. The **ST-GNN** predicts the advection trajectory across the next 24 hours.
2. **Amazon Bedrock** alerts the commissioner: *"Severe particulate aggregation in Talkatora Industrial Area at 345 µg/m³. Enacting GRAP Stage III. Mist-cannon fleet dispatched."*
3. **Google OR-Tools** renders the optimal routing path on the 3D PyDeck digital twin map.
4. An encrypted payload over **AWS IoT Core** commands the **ESP32 Edge Gateway**, oscillating the servo-mounted mist cannon to begin active particulate interception.
5. Every action is recorded into **Amazon DynamoDB**.

---

## 6. What's Next

With AWS App Runner and AWS SAM, deploying Zephyr to any municipal corporation across India requires just a single configuration file. Our next milestone is integrating satellite aerosol optical depth (AOD) feeds from Sentinel-5P directly into an Amazon S3 data lake to scale Zephyr to over 100 Indian cities.
