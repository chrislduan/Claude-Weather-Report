# Load env variables
from dotenv import load_dotenv
load_dotenv()  # Load variables from .env file

# Create API client
import anthropic

client = anthropic.Anthropic()
model = "claude-sonnet-4"

# imports
import json
from anthropic.types import Message
import chat
from .tools import base, date_tools, file_tools, weather_tools

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


def run_conversation(messages):
    while True:
        response = chat(
            messages,
            tools=[
                date_tools.get_current_datetime_schema,
                date_tools.add_duration_to_datetime_schema,
                date_tools.set_reminder_schema,
                base.batch_tool_schema
            ],
        )

        chat.add_assistant_message(messages, response)
        print(chat.text_from_message(response))

        if response.stop_reason != "tool_use":
            break

        tool_results = base.run_tools(response)
        chat.add_user_message(messages, tool_results)

    return messages


if __name__ == "__main__":
    run_conversation()