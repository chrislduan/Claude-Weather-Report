# Load env variables and create client
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()
model = "claude-haiku-4-5"

# import custom tools
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
import asyncio

# Helper functions
from anthropic.types import Message
import tools
import custom_tools

custom_server = custom_tools.custom_server


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
                tools.batch_tool_schema,
                tools.city_geocode_tool_schema,
                tools.geocode_weather_tool_schema,
                # tools.daily_forecast_schema
                # custom_tools.weather_tool_schema
            ],
        )

        add_assistant_message(messages, response)
        print(text_from_message(response))

        if response.stop_reason != "tool_use":
            break

        tool_results = custom_tools.run_tools(response)
        add_user_message(messages, tool_results)

    return messages

if __name__ == "__main__":
    print("I am an assistant that can give you the current weather of any given city.")
    print("Please provide a city name below.")
    messages = []
    # city = "Houston"
    city = input("Enter city name: ")
    while city!="exit":
        add_user_message(
            messages,
            # f"What is the weather like in {city}",
            # f"What is the latitude and longitude of {city}",
            city
        )
        run_conversation(messages)
        city = input("\nPlease enter another city name if you would like to know its weather,\n"
        " or type 'exit' if you would like to leave:")
    print(messages)