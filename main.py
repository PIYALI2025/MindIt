from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date
from typing import Optional
import uuid
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

MONGO_DETAILS ="mongodb://localhost:27017/MindIt"
client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.MindIt
subs_collection = database.get_collection("Subscriptions")


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class Subscription(BaseModel):
    id: Optional[str]=None
    name:str
    price:float
    category:str
    date: date
    is_trial:bool=False



@app.post("/add-bill")
def add_bill(sub:Subscription):
    if sub.price<0:
        return{"error":"Price cannot be negative.Try again..."}
    sub.id = str(uuid.uuid4())[:8]
    database.append(sub)
    return{"message":f"Successfuly added{sub.name} here with ID:{sub.id}","data":sub}


@app.get("/view-all")
def view_bill():
    return database

@app.get("/view-status")
def get_billing_status():
    report=[]

    for sub in database:
        today=date.today()
        days_left = (sub.date-today).days

        if days_left<0:
            status = "Overview"
            print("Reactivate")
        elif days_left ==0:
            status = "Due Today"
        elif days_left<=2:
            status = "2 days left"
        elif days_left<=5:
            status = "5 days left"
        else:
            status = "Upcoming"

        report.append({
            "name":sub.name,
            "days_remaining":days_left,
            "urgency":status,
            "amount_due":sub.price
        })
    return report


@app.get("/dashboard")
async def get_dashboard():
    cursor = subs_collection.find()
    subs = await cursor.to_list(length=100)
    conn = MONGO_DETAILS.connect("mindit.db")
    cursor = conn.cursor()
    cursor.execute("SELECT price,is_trial FROM subscriptions")
    rows = cursor.fetchall()
    conn.close()

    next_up="None"
    if database:
        sorted_bills = sorted(database,key=lambda x:x.date)
        next_up = sorted_bills[0].name
    if not rows:
        return{"monthly_exp": "0",
            "active_trials": 0,
            "next_payment_due": "None",
            "total_subs": 0}
    
    total_cost = sum(r[0] for r in rows)
    trial_count = sum(1 for r in rows if r[1] == 1)

    sorted_bills = sorted(database,key=lambda x:x.date)
    next_up = sorted_bills[0].name if sorted_bills else "None"

    return {
        "monthly_exp":f"{total_cost}",
        "activate_trials":trial_count,
        "next_payment_due":next_up,
        "total_subs":len(rows)
    }