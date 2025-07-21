from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "dynamic-hackathon"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
messages_collection = db["messages"]

app = FastAPI()

# Message schema
class Message(BaseModel):
    sender_id: str
    receiver_id: str
    message: str

@app.post("/send_message/")
def send_message(msg: Message):
    """Send a message from one crane to another."""
    new_message = {
        "sender_id": msg.sender_id,
        "receiver_id": msg.receiver_id,
        "message": msg.message,
        "timestamp": datetime.utcnow(),
        "status": "unread"
    }
    result = messages_collection.insert_one(new_message)
    return {"message": "Message sent", "message_id": str(result.inserted_id)}

@app.get("/messages/{crane_id}")
def get_messages(crane_id: str):
    """Retrieve messages for a specific crane."""
    messages = list(messages_collection.find({"receiver_id": crane_id}))
    for msg in messages:
        msg["_id"] = str(msg["_id"])  # Convert ObjectId to string
    return {"messages": messages}

@app.put("/mark_as_read/{message_id}")
def mark_as_read(message_id: str):
    """Mark a message as read."""
    result = messages_collection.update_one(
        {"_id": ObjectId(message_id)},
        {"$set": {"status": "read"}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"message": "Message marked as read"}
