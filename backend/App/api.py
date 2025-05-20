# api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.Conversations.chat import chat_with_tourism_assistant
from backend.App.models import ChatRequest, ChatResponse

app = FastAPI(title="TravelMate AI", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update in production with actual frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "🌍 Welcome to the TravelMate AI API!"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    assistant_answer, _ = chat_with_tourism_assistant(
        user_id=request.user_id,
        user_query=request.user_query,
        messages=[]
    )
    return {
        "summary": assistant_answer.get("summary", ""),
        "table": assistant_answer.get("table", ""),
    }
