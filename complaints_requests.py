from fastapi import APIRouter, Depends, HTTPException
from models import ComplaintRequest
from database import complaints_collection
from auth import get_current_user
from bson import ObjectId

router = APIRouter()

# Serializer for Mongo ObjectId
def serialize_item(item):
    return {
        "_id": str(item["_id"]),
        "register_number": item["register_number"],
        "name": item["name"],
        "category": item["category"],
        "text": item["text"]
    }

@router.get("/")
def get_items(user: dict = Depends(get_current_user)):
    items = list(complaints_collection.find({"register_number": user["register_number"]}))
    return [serialize_item(item) for item in items]

@router.post("/")
def add_item(item: ComplaintRequest, user: dict = Depends(get_current_user)):
    complaints_collection.insert_one(item.dict())
    return {"message": f"{item.category} added successfully"}

@router.delete("/{item_id}")
def delete_item(item_id: str, user: dict = Depends(get_current_user)):
    result = complaints_collection.delete_one({
        "_id": ObjectId(item_id),
        "register_number": user["register_number"]
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found or unauthorized")
    return {"message": "Deleted successfully"}
