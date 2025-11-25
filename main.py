# Load env variables and create client
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()
model = "claude-haiku-4-5"


# Helper functions
from anthropic.types import Message
import tools
import custom_tools



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
                custom_tools.weather_tool_schema,
                custom_tools.weather_forecast_schema
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
    print("I am an assistant that can give you the current weather or the forecast of any given city.\nYou may type 'exit' to leave at any time.")
    messages = []
    report_type = ""
    while True:
        user_input = input("Would you like to know current weather (W) or forecast (F)?\n")
        if user_input in ("exit", ""):
            break
        if user_input.lower() in ("current weather", "weather", "w", "forecast", "f"):
            if user_input.lower() in ("current weather", "weather", "w"):
                report_type = "weather"
            elif user_input.lower() in  ("forecast", "f"):
                report_type = "forecast"
            user_input = input("What city?\n")
            if user_input in ("exit", ""):
                break
        if report_type == "weather":
            input_string = f"Please give me a detailed report of the current weather in {user_input}"
        elif report_type == "forecast":
            input_string = f"Please give me a detailed 7 day weather forecast in {user_input}"
        add_user_message(
            messages,
            input_string
        )
        run_conversation(messages)
    # print(messages)
        
