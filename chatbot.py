from fastapi import APIRouter, Depends, HTTPException
from models import ComplaintRequest
from auth import get_current_user
import requests
import os
from dotenv import load_dotenv

router = APIRouter()

load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

@router.post("/")
def chatbot(item: ComplaintRequest, user: dict = Depends(get_current_user)):
    prompt = f"""
    Convert the following {item.category.lower()} into a formal letter:

    From: {item.name} ({item.register_number})

    {item.text}

    End with 'Thank you, Yours sincerely,' and the user's name.
    """
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "Complaint Request System"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        response.raise_for_status()
        data = response.json()
        return {"response": data["choices"][0]["message"]["content"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenRouter Error: {str(e)}")
