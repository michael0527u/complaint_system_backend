from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router, get_current_user
from chatbot import router as chatbot_router
from database import complaints_collection
from models import ComplaintRequest
from bson import ObjectId

app = FastAPI(title="Complaint Request System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(chatbot_router, prefix="/api/chatbot", tags=["Chatbot"])

@app.get("/")
def root():
    return {"message": "Backend is running!"}

@app.get("/api/complaints_requests")
def get_items(user: dict = Depends(get_current_user)):
    items = list(complaints_collection.find({"register_number": user["register_number"]}))
    for item in items:
        item["_id"] = str(item["_id"])
    return items

@app.post("/api/complaints_requests")
def add_item(item: ComplaintRequest, user: dict = Depends(get_current_user)):
    complaints_collection.insert_one(item.dict())
    return {"message": f"{item.category} added successfully"}

@app.delete("/api/complaints_requests/{item_id}")
def delete_item(item_id: str, user: dict = Depends(get_current_user)):
    result = complaints_collection.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Deleted successfully"}
