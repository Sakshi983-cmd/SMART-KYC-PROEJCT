from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import hashlib
import json
from datetime import datetime
import uvicorn
import re

app = FastAPI(title="GrackerKYC AI", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Blockchain simulation
class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        return hashlib.sha256(
            f"{self.index}{self.timestamp}{json.dumps(self.data)}{self.previous_hash}".encode()
        ).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
    
    def create_genesis_block(self):
        return Block(0, datetime.now(), {"message": "Genesis Block"}, "0")
    
    def add_block(self, data):
        previous_block = self.chain[-1]
        new_block = Block(
            len(self.chain),
            datetime.now(),
            data,
            previous_block.hash
        )
        self.chain.append(new_block)
        return new_block.hash

blockchain = Blockchain()

def init_db():
    conn = sqlite3.connect('gracker_kyc.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS kyc_verifications
                 (id INTEGER PRIMARY KEY, user_id TEXT, name TEXT, email TEXT, 
                  doc_type TEXT, doc_data TEXT, blockchain_hash TEXT, 
                  timestamp TEXT, status TEXT, ai_confidence REAL, risk_level TEXT,
                  issues TEXT, suggestions TEXT)''')
    conn.commit()
    return conn

conn = init_db()

class KYCRequest(BaseModel):
    name: str
    email: str
    document_text: str
    document_type: str

class AIAnalysis:
    @staticmethod
    def analyze_document(document_text: str, user_name: str):
        """Smart document analysis without Ollama"""
        
        # Extract information using regex patterns
        extracted_name = re.search(r'Name[:\s]*([^\n]+)', document_text, re.IGNORECASE)
        dob = re.search(r'(DOB|Date of Birth)[:\s]*([^\n]+)', document_text, re.IGNORECASE)
        doc_number = re.search(r'(Number|No)[:\s]*([^\n]+)', document_text, re.IGNORECASE)
        expiry = re.search(r'(Expiry|Valid|Date)[:\s]*([^\n]+)', document_text, re.IGNORECASE)
        
        # Basic validation
        name_match = extracted_name and user_name.lower() in extracted_name.group(1).lower()
        is_valid = bool(extracted_name and doc_number)
        
        # Risk analysis
        issues = []
        if not name_match:
            issues.append("Name mismatch detected")
        if not dob:
            issues.append("Date of birth missing")
        if not expiry:
            issues.append("Expiry date missing")
            
        risk_level = "high" if len(issues) > 2 else "medium" if len(issues) > 0 else "low"
        confidence = 90 if is_valid and risk_level == "low" else 60 if is_valid else 30
        
        return {
            "extraction": {
                "full_name": extracted_name.group(1) if extracted_name else "Not found",
                "dob": dob.group(2) if dob else "Not found",
                "doc_number": doc_number.group(2) if doc_number else "Not found",
                "expiry_date": expiry.group(2) if expiry else "Not found",
                "doc_type": "Extracted",
                "nationality": "Indian"
            },
            "validation": {
                "is_valid": is_valid,
                "confidence": confidence,
                "name_match": name_match,
                "expiry_status": "valid" if expiry else "unknown"
            },
            "risk_analysis": {
                "risk_level": risk_level,
                "issues": issues,
                "fraud_indicators": []
            },
            "recommendations": {
                "suggestions": ["Document appears valid" if is_valid else "Please review document"],
                "next_steps": "approve" if is_valid and risk_level == "low" else "review"
            }
        }

@app.get("/")
def root():
    return {"message": "GrackerKYC AI Server 🚀", "status": "active", "version": "3.0"}

@app.post("/api/v1/verify")
async def verify_kyc(request: KYCRequest):
    try:
        # AI Analysis
        ai_result = AIAnalysis.analyze_document(request.document_text, request.name)
        
        # Blockchain Integration
        block_data = {
            "user": request.name,
            "email": request.email,
            "doc_type": request.document_type,
            "timestamp": datetime.now().isoformat(),
            "ai_confidence": ai_result.get('validation', {}).get('confidence', 0)
        }
        
        blockchain_hash = blockchain.add_block(block_data)
        
        # Determine Status
        validation = ai_result.get('validation', {})
        risk_analysis = ai_result.get('risk_analysis', {})
        
        confidence = validation.get('confidence', 0)
        risk_level = risk_analysis.get('risk_level', 'high')
        
        if confidence >= 80 and risk_level == 'low':
            status = "APPROVED"
        elif confidence >= 60:
            status = "UNDER_REVIEW"
        else:
            status = "REJECTED"
        
        # Store in Database
        timestamp = datetime.now().isoformat()
        c = conn.cursor()
        c.execute('''INSERT INTO kyc_verifications 
                    (user_id, name, email, doc_type, doc_data, blockchain_hash, 
                     timestamp, status, ai_confidence, risk_level, issues, suggestions) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (
                      hashlib.md5(request.email.encode()).hexdigest()[:8],
                      request.name,
                      request.email,
                      request.document_type,
                      json.dumps(ai_result),
                      blockchain_hash,
                      timestamp,
                      status,
                      confidence,
                      risk_level,
                      json.dumps(risk_analysis.get('issues', [])),
                      json.dumps(ai_result.get('recommendations', {}).get('suggestions', []))
                  ))
        conn.commit()
        
        return {
            "success": True,
            "verification_id": blockchain_hash[:16],
            "status": status,
            "confidence_score": confidence,
            "risk_level": risk_level,
            "blockchain_hash": blockchain_hash,
            "timestamp": timestamp,
            "ai_analysis": ai_result,
            "blockchain_index": len(blockchain.chain) - 1
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Verification failed due to server error"
        }

@app.get("/api/v1/blockchain")
def get_blockchain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append({
            "index": block.index,
            "timestamp": block.timestamp.isoformat(),
            "data": block.data,
            "hash": block.hash,
            "previous_hash": block.previous_hash
        })
    return {"blockchain": chain_data, "length": len(blockchain.chain)}

@app.get("/api/v1/verifications")
def get_verifications():
    c = conn.cursor()
    c.execute("SELECT * FROM kyc_verifications ORDER BY timestamp DESC LIMIT 50")
    records = c.fetchall()
    
    columns = [col[0] for col in c.description]
    result = []
    for row in records:
        record = dict(zip(columns, row))
        if record.get('doc_data'):
            record['doc_data'] = json.loads(record['doc_data'])
        if record.get('issues'):
            record['issues'] = json.loads(record['issues'])
        if record.get('suggestions'):
            record['suggestions'] = json.loads(record['suggestions'])
        result.append(record)
    
    return {"verifications": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)