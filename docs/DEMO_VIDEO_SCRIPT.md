# Zephyr: 3-Minute Demo Video Script
**Event**: Bharat Builds Tour - Environmental Hacks (Event 02)  
**Track**: Track 01 - Air (Pollution Exposure & Municipal GRAP Automation)  
**Target Audience**: AWS Judging Panel & Amazon University Talent Acquisition Team  
**Target Duration**: 2 minutes 50 seconds  

---

### [0:00 - 0:35] The Hook: The Delayed Response Gap
* **Visual**: Screen recording showing severe smog in North Indian cities (Delhi/Lucknow), transitioning to the Zephyr 3D Command Center.
* **Speaker**:
  > *"Every winter across North India, millions breathe toxic air with PM2.5 levels soaring past 300 µg/m³. Today, municipal mitigation under the government's Graded Response Action Plan (GRAP) is fundamentally reactive. By the time authorities manually review static sensor dashboards and dispatch mist-cannon trucks, the pollution cloud has already advected across neighborhoods, exposing schools and commuters.*
  >
  > *Meet **Zephyr**: an AWS-powered Cyber-Physical Digital Twin that predicts pollution drift before it happens and autonomously closes the loop between cloud intelligence and physical mitigation hardware."*

---

### [0:35 - 1:20] The Core Innovation: ST-GNN + Explainable AI (XAI)
* **Visual**: Camera zooms into the 3D PyDeck spatial map in Lucknow. The cyan message-passing topology lines pulse, and the 3D needles indicate real-time PM2.5.
* **Speaker**:
  > *"Zephyr doesn't just read sensors. It ingests live atmospheric telemetry from 5 municipal stations via Open-Meteo REST APIs into a **PyTorch Geometric Spatio-Temporal Graph Neural Network (ST-GNN)**.
  >
  > By modeling wind vectors as dynamic graph edge attributes, our ST-GNN forecasts downwind particulate advection 24 hours into the future.
  >
  > Even better, high-stakes municipal interventions must be legally defensible. We integrated **PyTorch Captum** to calculate real-time Integrated Gradients feature attributions. Municipal commissioners can mathematically verify whether a spike was driven by temperature inversion, carbon monoxide, or wind advection."*

---

### [1:20 - 2:05] Where AWS Fits: Amazon Bedrock, IoT Core & LocalStack
* **Visual**: Show the "Autonomous Agent Briefing" card on the tactical rail and the AWS status banner. Trigger the "⚡ Spike PM2.5 Simulator".
* **Speaker**:
  > *"Here is where AWS completes the cyber-physical loop:
  >
  > 1. **Amazon Bedrock Agent**: An autonomous environmental agent running on Amazon Bedrock (Claude 3.5 Sonnet) synthesizes the complex GNN prediction matrix into fluid, actionable executive briefings for the Municipal Commissioner.
  > 2. **Operations Research Fleet Routing**: Google OR-Tools solves a Constrained Vehicle Routing Problem (VRP) to calculate the exact optimal GPS routes for anti-smog mist cannon trucks to intercept the critical nodes.
  > 3. **AWS IoT Core & Edge Actuation**: When a statutory Stage III or IV threshold is triggered, Zephyr dispatches an encrypted downlink over AWS IoT Core / MQTT to local ESP32 microcontrollers, which physically actuate servo valves and oscillate mist cannons.
  > 4. **Statutory Audit Trail**: Every mitigation order is immutably logged into **Amazon DynamoDB**, while 24-hour telemetry snapshots are archived to an **Amazon S3** Data Lake."*

---

### [2:05 - 2:40] "Build It" with Open Source & "Ship It" on AWS Cloud
* **Visual**: Show terminal with `docker compose up` showing LocalStack initializing S3, DynamoDB, and Mosquitto, and the AWS App Runner configuration.
* **Speaker**:
  > *"We architected Zephyr for both modes of the Bharat Builds Tour:
  >
  > - **Build It (Open Source)**: Utilizing **LocalStack**—AWS's open-source local cloud emulator—and containerized microservices, any municipality can run Zephyr 100% locally with zero cloud bills.
  > - **Ship It (AWS Cloud)**: It seamlessly deploys to **AWS App Runner** and **AWS SAM**, scaling automatically during peak pollution crises."*

---

### [2:40 - 3:00] Conclusion & Impact
* **Visual**: Overview of the full SCADA command center with all stations green and orange, the mist cannon sweeping, and the GitHub repo.
* **Speaker**:
  > *"Zephyr transforms urban air quality management from reactive paperwork to proactive, cyber-physical interception. By combining deep learning, operations research, and AWS cloud-native resilience, we are helping cities protect citizens before the bad air arrives.
  >
  > Thank you!"*
