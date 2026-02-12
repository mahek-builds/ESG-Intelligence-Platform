import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

app = FastAPI()

# Load API key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("WARNING: OPENAI_API_KEY not found in .env file")

client = OpenAI(api_key=api_key)

# Load ESG context
try:
    with open("esg_context.txt", "r", encoding="utf-8") as file:
        ESG_CONTEXT = file.read()
except FileNotFoundError:
    ESG_CONTEXT = "ESG context file not found."


# 🔹 Create request body model
class ChatRequest(BaseModel):
    prompt: str


@app.get("/")
def home():
    return {"message": "ESG AI Chatbot is running 🚀"}


# 🔹 Use POST instead of GET
@app.post("/chat")
def chat(request: ChatRequest):

    if not api_key:
        return {"response": "OpenAI API key not configured."}

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"""
You are an ESG AI assistant.
Answer ONLY using the provided context.
If answer is not found in context,
say: 'This information is not available in the ESG system.'

Context:
{ESG_CONTEXT}
"""
                },
                {"role": "user", "content": request.prompt}
            ]
        )

        return {"response": response.choices[0].message.content}

    except Exception as e:
        return {
            "response": "ESG Assistant is temporarily unavailable. Please check API key, billing, or internet connection."
        }
