
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import base64
import os

load_dotenv()

import auth
import agent
from database import (
    create_conversation,
    get_conversations,
    get_messages,
)

app = FastAPI(title="Image Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")




class AuthRequest(BaseModel):
    email: str
    password: str




@app.post("/signup")
async def signup(body: AuthRequest):
    result = auth.signup(body.email, body.password)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.post("/login")
async def login(body: AuthRequest):
    result = auth.login(body.email, body.password)
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    return result




@app.post("/conversations")
async def new_conversation(email: str):
    convo = create_conversation(email)
    return convo


@app.get("/conversations")
async def list_conversations(email: str):
    convos = get_conversations(email)
    return {"conversations": convos}


@app.get("/conversations/{conversation_id}/messages")
async def list_messages(conversation_id: int):
    msgs = get_messages(conversation_id)
    return {"messages": msgs}




@app.post("/chat")
async def chat(
    email: str = Form(...),
    conversation_id: int = Form(...),
    message: str = Form(default=""),
    file: UploadFile = File(default=None),
):
    
    image_b64 = ""
    image_name = ""

    if file and file.filename:
        image_bytes = await file.read()
        image_b64 = base64.standard_b64encode(image_bytes).decode()
        image_name = file.filename

    
    previous = get_messages(conversation_id)
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in previous
        if m.get("content")
    ]

    try:
        result = agent.run_agent(
            conversation_id=conversation_id,
            user_message=message,
            message_history=history,
            image_b64=image_b64,
            image_name=image_name,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
