import os
import base64
import json
from openai import OpenAI
from database import save_message

SYSTEM_PROMPT = (
    "You are a helpful AI assistant that can answer questions, generate images, "
    "and caption uploaded photos. "
    "When the user asks to create, generate, draw or make an image, use the generate_image tool. "
    "When the user uploads a photo and wants it described or captioned, use the caption_image tool. "
    "For everything else, just answer conversationally and helpfully."
)

TOOLS = [
    {
        "type": "function",
        "name": "generate_image",
        "description": (
            "Generate an image from a text prompt. Use this when the user asks "
            "to create, generate, draw, or make an image."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The image description to generate"
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "type": "function",
        "name": "caption_image",
        "description": (
            "Caption or describe an uploaded image. Use this when the user has "
            "uploaded a photo and wants it described, analyzed, or captioned."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "instruction": {
                    "type": "string",
                    "description": "What to do with the image"
                }
            },
            "required": []
        }
    }
]




def _do_generate_image(prompt: str) -> str:
    """Call gpt-image-1 and return base64 image string."""
    client = OpenAI()
    response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        n=1,
    )
    return response.data[0].b64_json


def _do_caption_image(image_b64: str, instruction: str) -> str:
    """Send image to gpt-4.1 vision and return caption text."""
    client = OpenAI()
    text_prompt = instruction if instruction else "Describe this image in one or two sentences."

    response = client.responses.create(
        model="gpt-4.1",
        input=[{
            "role": "user",
            "content": [
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{image_b64}"
                },
                {
                    "type": "input_text",
                    "text": text_prompt
                }
            ]
        }]
    )
    return response.output_text




def run_agent(
    conversation_id: int,
    user_message: str,
    message_history: list,
    image_b64: str = "",
    image_name: str = ""
) -> dict:
    """
    Main agent loop.

    - GPT-5.5 makes the main decision (answer / generate / caption)
    - GPT-4.1 handles the followup response after a tool runs
      (avoids the reasoning block issue with GPT-5.5)
    """
    client = OpenAI()

    
    save_message(
        conversation_id=conversation_id,
        role="user",
        content=user_message,
        message_type="image" if image_b64 else "text",
        image_data=image_b64,
        image_name=image_name,
    )

    
    input_messages = []

    for msg in message_history:
        if msg.get("content"):
            input_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

    if image_b64:
        input_messages.append({
            "role": "user",
            "content": [
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{image_b64}"
                },
                {
                    "type": "input_text",
                    "text": user_message or "Describe this image."
                }
            ]
        })
    else:
        input_messages.append({
            "role": "user",
            "content": user_message
        })

    # ── GPT-5.5 decides what to do ────────────────────────────────────────────
    response = client.responses.create(
        model="gpt-5.5",
        instructions=SYSTEM_PROMPT,
        input=input_messages,
        tools=TOOLS,
    )

    # ── Handle tool calls ─────────────────────────────────────────────────────
    for block in response.output:

        if block.type == "function_call":
            tool_name = block.name
            tool_args = json.loads(block.arguments)

            # ── Generate image ────────────────────────────────────────────────
            if tool_name == "generate_image":
                prompt = tool_args["prompt"]
                image_b64_result = _do_generate_image(prompt)

                # GPT-4.1 for the followup — no reasoning block issues
                followup = client.responses.create(
                    model="gpt-4.1",
                    instructions=SYSTEM_PROMPT,
                    input=input_messages + [
                        {
                            "role": "assistant",
                            "content": f"I used the generate_image tool with prompt: {prompt}"
                        },
                        {
                            "role": "user",
                            "content": "The image was generated successfully. Give a short friendly response confirming this."
                        }
                    ],
                )
                assistant_text = followup.output_text

                save_message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=assistant_text,
                    message_type="image",
                    image_data=image_b64_result,
                    image_name=f"{prompt[:40]}.png",
                )

                return {
                    "type": "image",
                    "content": assistant_text,
                    "image_data": image_b64_result,
                }

            # ── Caption image ─────────────────────────────────────────────────
            elif tool_name == "caption_image":
                if not image_b64:
                    return {"type": "text", "content": "Please upload an image first."}

                instruction = tool_args.get("instruction", "")
                caption = _do_caption_image(image_b64, instruction)

                
                followup = client.responses.create(
                    model="gpt-4.1",
                    instructions=SYSTEM_PROMPT,
                    input=input_messages + [
                        {
                            "role": "assistant",
                            "content": f"I captioned the image. The caption is: {caption}"
                        },
                        {
                            "role": "user",
                            "content": "Present the caption nicely to the user."
                        }
                    ],
                )
                assistant_text = followup.output_text

                save_message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=assistant_text,
                    message_type="caption",
                    image_data=image_b64,
                    image_name=image_name,
                )

                return {
                    "type": "caption",
                    "content": assistant_text,
                    "caption": caption,
                    "image_data": image_b64,
                }

    assistant_text = response.output_text

    save_message(
        conversation_id=conversation_id,
        role="assistant",
        content=assistant_text,
        message_type="text",
    )

    return {
        "type": "text",
        "content": assistant_text,
    }