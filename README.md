# AI Multimodal Assistant

A full-stack multimodal AI assistant built with **FastAPI, OpenAI, and Supabase** that combines conversational AI, image generation, and image understanding in a single application.

The project uses the OpenAI Responses API with tool calling to allow the AI to decide when to generate images, analyze uploaded images, or respond conversationally.

---

## Features

### AI Chat
- Conversational AI assistant powered by OpenAI models
- Maintains conversation history
- Supports multi-turn interactions

### AI Image Generation
- Generate images from text prompts
- Uses OpenAI's image generation model
- Returns generated images directly to the user

### Image Understanding
- Upload images and receive AI-generated descriptions/captions
- Supports image analysis with vision models

### Authentication
- User signup and login system
- Secure password hashing using bcrypt
- User data stored with Supabase

### Conversation Management
- Create and manage conversations
- Store chat history permanently
- Retrieve previous messages

### AI Tool Calling
The assistant uses tool calling to decide when to:
- Generate an image
- Analyze an uploaded image
- Answer normally without using a tool

---

# Tech Stack

## Backend
- Python
- FastAPI
- Uvicorn

## AI
- OpenAI Responses API
- GPT-5.5
- GPT-4.1 Vision
- GPT-Image-1

## Database
- Supabase

## Authentication
- bcrypt password hashing

## Other
- REST API architecture
- Environment variable management with python-dotenv

---

# Project Architecture

```
                    User
                     |
                     |
              Frontend (HTML/CSS/JS)
                     |
                     |
                FastAPI Server
                     |
        --------------------------------
        |              |               |
        |              |               |
    Authentication   Database       AI Agent
        |              |               |
        |              |               |
     bcrypt        Supabase       OpenAI API
                                      |
                         ------------------------
                         |          |           |
                      GPT-5.5   GPT-4.1   GPT-Image-1
                         |
                    Tool Calling
                         |
             -------------------------
             |                       |
      Generate Image          Caption Image
```

---

## Project Structure

```text
AI-multimodal-assistant/
├── static/
│   └── index.html              # User interface
├── .env                        # Environment variables (not tracked)
├── .gitignore                  # Git ignore configuration
├── agent.py                    # Agent loop, tool calling, image generation & captioning
├── auth.py                     # Authentication using bcrypt
├── database.py                 # Supabase CRUD operations
├── main.py                     # FastAPI server and API endpoints
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

# Installation

## 1. Clone the Repository

```bash
git clone <repository-url>

cd AI-Multimodal-Assistant
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate it:

### Windows

```bash
venv\Scripts\activate
```

### macOS/Linux

```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key

SUPABASE_URL=your_supabase_url

SUPABASE_KEY=your_supabase_key
```

---

## 5. Run the Application

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The application will run at:

```
http://127.0.0.1:8000
```

---

# API Endpoints

## Authentication

### Signup

```
POST /signup
```

Creates a new user account.

Request:

```json
{
  "email": "user@example.com",
  "password": "password"
}
```

---

### Login

```
POST /login
```

Authenticates a user.

---

# Conversations

### Create Conversation

```
POST /conversations
```

Creates a new conversation for a user.

---

### Get Conversations

```
GET /conversations
```

Retrieves previous conversations.

---

### Get Messages

```
GET /conversations/{conversation_id}/messages
```

Returns messages from a conversation.

---

# AI Chat

### Send Message

```
POST /chat
```

Supports:

- Text messages
- Image uploads
- AI responses
- Image generation requests
- Image captioning

---

# How the AI Agent Works

The application implements an agent workflow using OpenAI tool calling.

Flow:

```
User Input

     ↓

GPT-5.5 decides the action

     ↓

Does it need a tool?

     ↓

----------------------
|                    |
Yes                  No
|                    |
Call Tool          Normal Response
|
Generate Image /
Caption Image

     ↓

Return Final Response
```

The agent can decide whether to:
- Generate an image
- Analyze an image
- Provide a normal conversational response

---

# Future Improvements

Planned improvements:

- Migrate to OpenAI Agents SDK
- Add streaming responses
- Add multi-agent architecture
- Implement RAG with document search
- Add file upload and document analysis
- Improve frontend UI/UX
- Add deployment using Docker
- Add automated testing
- Add better error handling and monitoring

---

# Learning Outcomes

Through this project, I explored:

- Building AI-powered backend applications
- OpenAI API integration
- LLM tool calling
- Multimodal AI workflows
- Authentication systems
- Database integration
- Managing conversational context
- Designing scalable API architectures

---

