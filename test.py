# Load env variables and create client
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()
model = "claude-haiku-4-5"



# Helper functions
from anthropic.types import Message
import tools


def add_user_message(messages, message):
    user_message = {
        "role": "user",
        "content": message.content if isinstance(message, Message) else message,
    }
    messages.append(user_message)


def add_assistant_message(messages, message):
    assistant_message = {
        "role": "assistant",
        "content": message.content if isinstance(message, Message) else message,
    }
    messages.append(assistant_message)


def chat(messages, system=None, temperature=1.0, stop_sequences=[], tools=None):
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences,
    }

    if tools:
        params["tools"] = tools

    if system:
        params["system"] = system

    message = client.messages.create(**params)
    return message


def text_from_message(message):
    return "\n".join([block.text for block in message.content if block.type == "text"])

def run_conversation(messages):
    while True:
        response = chat(
            messages,
            tools=[
                tools.get_current_datetime_schema,
                tools.add_duration_to_datetime_schema,
                tools.set_reminder_schema,
                tools.batch_tool_schema,
                tools.weather_tool_schema
            ],
        )

        add_assistant_message(messages, response)
        print(text_from_message(response))

        if response.stop_reason != "tool_use":
            break

        tool_results = tools.run_tools(response)
        add_user_message(messages, tool_results)

    return messages

if __name__ == "__main__":
    messages = []
    add_user_message(
        messages,
        "What is the weather like in Houston",
    )
    print(run_conversation(messages))