# 🏆 Bharat Builds Tour: Environmental Hacks — Project Submission Form

**Event**: Bharat Builds Tour (Event 02: Environmental Hacks)  
**Organizers**: AWS & WeMakeDevs  
**Submission Portal**: [wemakedevs.org/aws/env/submit](https://www.wemakedevs.org/aws/env/submit)  

---

## 1. Basic Information

* **Project Name**:  
  `Zephyr: Cyber-Physical Air Quality Twin`

* **Tagline / Short Pitch (under 140 chars)**:  
  `Predictive Spatio-Temporal Air Quality Twin closing the loop between Amazon Bedrock, ST-GNNs, and physical municipal mist-cannon actuators.`

* **Track Selected**:  
  `Track 01: Air` *(Pollution, exposure, and the days the AQI goes off the chart)*

* **Project Links**:
  * **GitHub Repository**: `https://github.com/alfayezahmad/Zephyr`
  * **Live Interactive Demo**: `https://zephyr-air.streamlit.app` *(or your Streamlit Community Cloud deployment URL)*
  * **AWS Builder Center Blog**: *(Paste your published blog link from builder.aws.com, based on `docs/AWS_BUILDER_CENTER_BLOG.md`)*
  * **Demo Video URL**: *(Paste your YouTube / Loom / Google Drive link, recorded using `docs/DEMO_VIDEO_SCRIPT.md`)*

---

## 2. Problem & Inspiration

### What problem does your project solve?
Every winter across northern India (Delhi, Lucknow, Kanpur), severe atmospheric inversions trap PM2.5 particulate matter at toxic levels exceeding 300–450 µg/m³. The central government enforces the Graded Response Action Plan (GRAP)—a statutory rulebook mandating mechanized road sweeping (Stage I), water sprinklers (Stage II), anti-smog mist cannon trucks (Stage III), and emergency industrial/vehicular shutdowns (Stage IV).

However, municipal response today suffers from a **delayed response gap**:
1. Static monitoring stations observe pollution spikes after they occur.
2. The data sits on passive administrative dashboards.
3. Bureaucratic reviews take hours to authorize mitigation vehicle dispatches.
4. **By the time mist cannons arrive, the pollution plume has already advected (drifted) downwind into neighboring residential wards and schools.**

We built **Zephyr** to transform urban air quality management from a passive, retrospective dashboard into an active, autonomous **Cyber-Physical Digital Twin** that anticipates pollution drift 24 hours ahead and autonomously actuates physical mitigation assets in the real world.

---

## 3. What It Does

Zephyr operates as an autonomous closed loop:
1. **Live Atmospheric Ingestion**: Continuously polls Open-Meteo REST APIs for live PM2.5, Carbon Monoxide, Temperature, and Wind Vectors across Lucknow's municipal CAAQMS stations (Talkatora, Lalbagh, Gomti Nagar, Alambagh, Kalyanpur), factoring in microclimate urban typologies.
2. **Spatio-Temporal GNN Forecasting**: A custom PyTorch Geometric Graph Neural Network (`WindAdvectionGNN`) models wind speed and direction as dynamic edge attributes to forecast downwind particulate advection over the next 24 hours.
3. **Explainable AI (XAI)**: Integrated Gradients via PyTorch Captum provides mathematically defensible feature attributions (PM2.5 lag, thermal inversion, wind advection) to ensure municipal interventions are legally compliant.
4. **Autonomous Bedrock Briefing**: An Amazon Bedrock Diagnostic Agent (Claude 3.5 Sonnet) synthesizes high-dimensional spatial tensors into concise, authoritative executive briefings for the Municipal Commissioner.
5. **Constrained VRP Fleet Routing**: Google OR-Tools solves a Vehicle Routing Problem with capacity and depot constraints, plotting optimal parabolic dispatch paths for mist cannons to intercept downwind plumes.
6. **Hardware Downlink Actuation**: Dispatches encrypted commands via AWS IoT Core / MQTT to ESP32 microcontrollers, actuating servo-controlled mist cannons and water valves.
7. **Statutory Audit Ledger**: Every statutory GRAP intervention is immutably recorded into Amazon DynamoDB and archived to an Amazon S3 Data Lake.

---

## 4. How We Built It (Architecture & AWS Services)

### Architecture Stack:
* **Machine Learning**: PyTorch Geometric (ST-GNN message passing), PyTorch Captum (Integrated Gradients XAI), Scikit-Learn.
* **Operations Research**: Google OR-Tools (Capacitated Vehicle Routing Problem).
* **Frontend / Visualization**: Streamlit, PyDeck (3D WebGL cartographic twins, needle columns, parabolic dispatch arcs), Plotly (24h multi-sensor timelines).
* **Backend Microservices**: FastAPI (asynchronous REST API), Uvicorn, Docker, Docker Compose.
* **Edge / Hardware**: Python/MicroPython MQTT daemon, ESP32 dual PWM channels controlling oscillating anti-smog mist cannons.

### AWS Cloud & Open Source Integration:
* **Amazon Bedrock (Claude 3.5 Sonnet)**: Synthesizes ST-GNN prediction tensors into actionable executive briefings with a zero-crash autonomous fallback engine.
* **LocalStack (AWS Open Source)**: Emulates Amazon S3, DynamoDB, and SNS locally for zero-cloud-bill municipal prototyping.
* **Amazon DynamoDB**: Immutably logs all statutory CAQM GRAP intervention orders in the audit ledger (`Zephyr_AuditLogs`).
* **Amazon S3**: Ingests continuous spatio-temporal telemetry snapshots into a data lake (`s3://zephyr-telemetry-lake`).
* **Amazon SNS & AWS IoT Core**: Sends emergency broadcast alerts and MQTT downlink payloads to edge actuators.
* **AWS App Runner & AWS SAM**: Configured for 1-click cloud container deployment and serverless orchestration (`infra/apprunner.yaml`, `infra/template.yaml`).

---

## 5. Technical Challenges & What Fought Back

1. **Calculating Gradients on Dynamic Graph Message-Passing Layers**:
   PyTorch Captum's `IntegratedGradients` requires continuous input tensors. Calculating gradients across graph structures with dynamic edge attributes (wind vectors) caused tensor mismatch during baseline interpolation.  
   *Solution*: We isolated the node feature tensor as the target baseline while preserving the normalized adjacency structure, enabling exact input-level SHAP attributions without destabilizing the graph topology.

2. **Operations Research vs. Real-Time Latency**:
   Solving the Vehicle Routing Problem (VRP) using integer programming can incur high latency if distance matrices are computed synchronously per request.  
   *Solution*: We pre-cached Haversine distance matrices of municipal corridors and applied dynamic candidate pruning (`PM2.5 > 120 µg/m³`), dropping routing calculation time to under 15ms.

3. **Edge Fail-Safe Under Network Partitions**:
   In municipal environments, wireless links can drop during heavy smog or weather. If an edge node loses its MQTT uplink while spraying water, it could cause flooding.  
   *Solution*: We engineered local heartbeat verification into the edge daemon: if the broker connection drops for >5 seconds, the node immediately enters a fail-safe `STANDBY` state, closing the valves.

---

## 6. Accomplishments That We're Proud Of

* **Closed the Full Cyber-Physical Loop**: Transitioned from purely software analytics to real-time physical actuation over hardware mist cannons.
* **Sub-60ms Inference Latency**: Full 5-node spatio-temporal graph neural network forward pass runs in under 60ms.
* **Zero-Bill Municipal Prototyping**: Complete AWS service integration running locally with LocalStack, ready for instant cloud deployment.
* **True Explainable AI**: No black boxes—every GRAP mitigation order is mathematically justified with PyTorch Captum attributions.

---

## 7. What We Learned

* How to combine Graph Neural Networks with physical atmospheric advection physics using wind-modulated edge attributes.
* Building resilient AWS architectures with Amazon Bedrock, DynamoDB audit trails, and LocalStack emulation.
* Translating environmental legal frameworks (CAQM GRAP Stage I–IV) into deterministic automated execution pipelines.

---

## 8. What's Next for Zephyr

* **Scaling to 100+ CAAQMS Stations**: Expanding the graph neural network across the entire Indo-Gangetic Plain.
* **Satellite Telemetry Fusion**: Integrating ISRO/NASA INSAT-3D and Sentinel-5P aerosol optical depth (AOD) feeds.
* **Fleet Telematics Integration**: Directly interfacing with municipal electric vehicle (EV) fleet APIs for dynamic en-route navigation.
