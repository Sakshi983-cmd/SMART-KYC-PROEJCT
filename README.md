# 💡 SMART-KYC-AI Platform

![SmartKYC Logo](asset/ChatGPT Image Sep 26, 2025, 08_23_58 PM.png)  

**GrackerKYC AI v3.0** — A privacy-first, AI-powered KYC verification system built with FastAPI, SQLite, and blockchain simulation. Designed for financial compliance, fraud detection, and ethical identity verification.

---

## 🧠 Features

- ✅ **AI-Powered Document Analysis** using regex and NLP  
- 🔐 **Blockchain Audit Trail** for tamper-proof verification logs  
- 📊 **Risk Scoring Engine** with confidence levels and fraud indicators  
- 🧾 **Smart Extraction** of Name, DOB, Document Number, Expiry  
- 🧠 **No Ollama Required** — lightweight, local AI logic  
- 🗃️ **SQLite Storage** for fast, secure data handling  
- 🌐 **FastAPI Backend** with CORS-enabled endpoints  
- 📈 **Dashboard-ready APIs** for frontend integration  

---

## 📂 Project Structure

```bash
├── backend.py          # FastAPI server with AI + Blockchain logic
├── frontend.py         # Optional UI integration (React/Streamlit)
├── gracker_kyc.db      # SQLite database for KYC records
├── requirements.txt    # Python dependencies
├── assets/             # Logo, screenshots, and demo images
└── README.md           # You're reading it!
```


## DEMO  
 
 ![GrackerKYC AI Screenshot](assets/SMART KYC DEMO.jpg)
---

## 🔧 Installation

```bash
# Clone the repo
git clone https://github.com/Sakshi983-cmd/SMART-KYC-AI.git
cd SMART-KYC-AI

# Install dependencies
pip install -r requirements.txt

# Run the backend
uvicorn backend:app --reload
```

---

## 📡 API Endpoints

| Method | Endpoint                  | Description                          |
|--------|---------------------------|--------------------------------------|
| GET    | `/`                       | Health check                         |
| POST   | `/api/v1/verify`          | Submit KYC document for analysis     |
| GET    | `/api/v1/blockchain`      | View blockchain audit trail          |
| GET    | `/api/v1/verifications`   | Fetch recent KYC verification logs   |

---

## 🧪 Sample Request

```json
POST /api/v1/verify
{
  "name": "Test User",
  "email": "test.user@example.com",
  "document_text": "Name: Test User\nDOB: 01/01/1990\nNumber: 123456789012",
  "document_type": "Aadhaar Card"
}
```

---

## 🛡️ Risk Scoring Logic

- **Low Risk** → Confidence ≥ 80 + Valid expiry + Name match  
- **Medium Risk** → Confidence ≥ 60 + Minor issues  
- **High Risk** → Missing fields or mismatched data  

---

## 🧘 Vision

This project is part of a larger mission to build ethical, privacy-safe AI systems for financial inclusion and karmic justice. Built by **Sakshi Tiwari** — a resilient engineer blending tech, empathy, and spiritual wisdom.

---

## 📬 Contact

For collaboration, feedback, or demo requests:  
**Email**: sakshi983.cmd@gmail.com  
**GitHub**: [Sakshi983-cmd](https://github.com/Sakshi983-cmd)

