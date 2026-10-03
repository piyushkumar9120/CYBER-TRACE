# 🛡️ CYBER-TRACE V4.0: Predictive Analytics Framework for Cybercrime Complaints

> **Forecasting Likely Cash Withdrawal Locations (ATMs/CSPs) in Real-Time for Pre-Emptive Law Enforcement & Bank Interception.**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/ML-DBSCAN-orange.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 Problem Overview
Every day, over 8,000+ complaints are filed on the **National Cybercrime Reporting Portal (1930 / CFCFRMS)**. A critical gap in cyber financial fraud is the **"Golden Hour"** (30–60 minutes post-fraud) where fraudsters physically withdraw extorted cash at local ATMs and Customer Service Points (CSPs). Once funds leave the ATM as physical currency, the recovery rate plummets to near 0%.

**CYBER-TRACE** is an AI-powered predictive spatial intelligence framework designed for Law Enforcement Agencies (LEAs) and Banks to forecast ATM cash-out hotspots **before** the withdrawal takes place.

---

## ⚡ Core Features

- **📍 Geospatial DBSCAN Clustering:** Automatically clusters incoming victim complaints using spherical Haversine distance ($\epsilon = 2.4\text{ km}$) to identify emerging cash-out corridors.
- **📊 4-Factor Dynamic Risk Scoring:**
  $$\text{Risk Index} = (0.30 \times \text{Volume}) + (0.30 \times \text{Value}) + (0.20 \times \text{ATM History}) + (0.20 \times \text{Velocity})$$
- **⏳ Proactive Lead-Time Prediction:** Calculates dynamic 20–45 minute intervention windows before cash-out occurs.
- **🚔 Automated Police Patrol (PCR) Dispatch:** Finds closest patrol units via Haversine geometry and computes real-time driving ETAs.
- **🛑 Instant Bank Freeze Webhook:** Simulates an automated hold via NPCI / Core Banking switches to freeze mule cards immediately.
- **⏱️ Decoy Delay Trap:** Throttles ATM cash dispensing latency by 90 seconds, enabling on-ground sting arrests.
- **📞 Automated Guard Voice AI (IVR):** Dials automated voice warnings to on-site ATM security guards and branch managers.
- **📹 Vestibule CCTV Anomaly Detection:** Flags multi-card hopping and masked suspects against cyber criminal databases.
- **⚖️ Section 65B Digital Evidence Dossier:** Generates tamper-proof, court-admissible forensic certificates (.txt/.pdf).

---

## 🛠️ Tech Stack

- **Frontend & Dashboard:** Streamlit, Folium, Leaflet.js
- **Machine Learning:** Scikit-Learn (DBSCAN), NumPy, Pandas
- **Geospatial Processing:** Haversine Spherical Distance Modeling
- **Target Production Architecture:** Apache Kafka, PostgreSQL + PostGIS, Neo4j Graph DB

---

## 🚀 Quickstart Guide

### 1. Clone the Repository
```bash
git clone https://github.com/piyushkumar9120/cyber-trace.git
cd cyber-trace