import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

supabase: Client = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)




def create_user(email: str, password_hash: str) -> dict:
    result = supabase.table("users").insert({
        "email": email,
        "password_hash": password_hash
    }).execute()
    return result.data[0] if result.data else {}


def get_user_by_email(email: str) -> dict | None:
    result = supabase.table("users").select("*").eq("email", email).execute()
    return result.data[0] if result.data else None




def create_conversation(user_email: str) -> dict:
    result = supabase.table("conversations").insert({
        "user_email": user_email
    }).execute()
    return result.data[0] if result.data else {}


def get_conversations(user_email: str) -> list:
    result = (
        supabase.table("conversations")
        .select("*")
        .eq("user_email", user_email)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []




def save_message(
    conversation_id: int,
    role: str,
    content: str = "",
    message_type: str = "text",
    image_data: str = "",     
    image_name: str = ""     
) -> dict:
    result = supabase.table("messages").insert({
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "message_type": message_type,
        "image_data": image_data or None,
        "image_name": image_name or None,
    }).execute()
    return result.data[0] if result.data else {}


def get_messages(conversation_id: int) -> list:
    result = (
        supabase.table("messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .order("created_at", desc=False)
        .execute()
    )
    return result.data or []
