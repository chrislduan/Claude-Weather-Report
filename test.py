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
                # tools.get_current_datetime_schema,
                # tools.add_duration_to_datetime_schema,
                # tools.batch_tool_schema,
                # tools.city_geocode_tool_schema,
                # tools.geocode_weather_tool_schema,
                # tools.daily_forecast_schema
                custom_tools.weather_tool_schema
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
    print("I am an assistant that can give you the current weather or the forecast of any given city.")
    # print("Please let me know if you would like the current or the forecast.")
    messages = []
    report_type = ""
    # request = input("Would you like to know current weather (W) or forecast (F)?\n")
    # if request == "exit": 
    #     pass
    # while request not in ["current weather", "weather", "W", "w", "forecast", "F", "f", "exit"]:
    #     input("Would you like to know current weather (W) or forecast (F)?\n")
    # if request == "exit": 
    #     pass
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
        add_user_message(
            messages,
            f"What is the weather like in {user_input}" if report_type=="weather" else "What is the tomorrow's weather forecast in {user_input}"
        )
        run_conversation(messages)
    print(messages)
        