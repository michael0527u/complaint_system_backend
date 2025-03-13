from pydantic import BaseModel

class User(BaseModel):
    name: str
    register_number: str
    phone_number: str
    password: str

class UserLogin(BaseModel):
    register_number: str
    password: str

class ComplaintRequest(BaseModel):
    register_number: str
    name: str
    category: str  # Complaint or Request
    text: str
