# Load env variables
from dotenv import load_dotenv
load_dotenv()  # Load variables from .env file


import anthropic

client = anthropic.Anthropic()
model = "claude-sonnet-4"

message = client.messages.create(
    model = model,
    max_tokens = 1000,
    messages = [
        {
            "role": "user",
            "content": "What is a dictionary? Answer in one sentence."
        }
    ]
)