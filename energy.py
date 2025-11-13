from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

app = FastAPI(title="📈 Pakistan Energy API")

@app.get("/")
def home():
    return {"message": "📈 Pakistan Energy API is running!", "docs": "/docs"}

records = {}
next_id = 1

class RecordCreate(BaseModel):
    date: date
    demand_gwh: float

class Record(RecordCreate):
    id: int

@app.post("/records", response_model=Record, status_code=201)
def add_record(record: RecordCreate):
    global next_id
    new_record = {**record.dict(), "id": next_id}
    records[next_id] = new_record
    next_id += 1
    return new_record

@app.get("/records", response_model=List[Record])
def get_all_records():
    return list(records.values())

@app.get("/records/{record_id}", response_model=Record)
def get_record(record_id: int):
    if record_id not in records:
        raise HTTPException(status_code=404, detail="Record not found")
    return records[record_id]

@app.put("/records/{record_id}", response_model=Record)
def update_record(record_id: int, record: RecordCreate):
    if record_id not in records:
        raise HTTPException(status_code=404, detail="Record not found")
    records[record_id] = {**record.dict(), "id": record_id}
    return records[record_id]

@app.patch("/records/{record_id}", response_model=Record)
def partial_update_record(record_id: int, demand_gwh: Optional[float] = None):
    if record_id not in records:
        raise HTTPException(status_code=404, detail="Record not found")
    if demand_gwh is not None:
        records[record_id]["demand_gwh"] = demand_gwh
    return records[record_id]

@app.delete("/records/{record_id}", status_code=204)
def delete_record(record_id: int):
    if record_id not in records:
        raise HTTPException(status_code=404, detail="Record not found")
    del records[record_id]
    return

@app.get("/forecast")
def forecast(years: int = 1):
    if years < 0 or years > 5:
        raise HTTPException(status_code=400, detail="Years must be between 0 and 5")
    latest = max(records.values(), key=lambda x: x["date"]) if records else {"demand_gwh": 500}
    base = latest["demand_gwh"]
    return [
        {"year": date.today().year + i, "forecast_gwh": round(base * (1.05 ** i), 1)}
        for i in range(1, years + 1)
    ]