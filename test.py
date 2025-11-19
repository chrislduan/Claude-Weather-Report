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
    if isinstance(message, list):
        assistant_message = {
            "role": "assistant",
            "content": message
        }
    elif hasattr(message, "content"):
        content_list = []
        for block in message.content:
            if block.type == "text":
                content_list.append({"type": "text", "text": block.text})
            elif block.type == "tool_use":
                content_list.append({
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input
                })
            assistant_message = {
                "role": "assistant",
                "content": content_list
            }
    else:
        assistant_message = {
            "role": "assistant",
            "content": [{"type": "text", "text": message}],
        }
    messages.append(assistant_message)


# basic chat function
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

# stream chat function
def chat_stream(
    messages,
    system=None,
    temperature=1.0,
    stop_sequences=[],
    tools=None,
    #tool_choice=None,
    betas=[]
):
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences,
        "stream": True,
        "betas": betas,
    }

    if tools:
        params["tools"] = tools

    # if tool_choice:
    #     params["tool_choice"] = tool_choice

    if system:
        params["system"] = system

    if betas:
        params["betas"] = betas

    return client.beta.messages.stream(**params)



def text_from_message(message):
    return "\n".join([block.text for block in message.content if block.type == "text"])

def run_conversation(messages):
    while True:
        with chat_stream(
            messages,
            tools=[
                tools.get_current_datetime_schema,
                tools.add_duration_to_datetime_schema,
                tools.set_reminder_schema,
                tools.batch_tool_schema,
                tools.weather_tool_schema
            ],
            #tool_choice="auto",
        ) as stream:
            for chunk in stream:
                if chunk.type == "text":
                    print(chunk.text, end="", flush=True)
                
                if chunk.type == "content_block_start":
                    if chunk.block.type == "tool_use":
                        print(f"\n\n[Tool Use: {chunk.block.name}]\n", end="", flush=True)
                
                if chunk.type == "input_json" and chunk.partial_json:
                    print(chunk.partial_json, end="", flush=True)

                if chunk.type == "content_block_stop":
                    print("\n", end="", flush=True)

            response = stream.get_final_message()

        add_assistant_message(messages, response)

        if response.stop_reason != "tool_use":
            break

        tool_results = tools.run_tools(response)
        add_user_message(messages, tool_results)

    return messages

if __name__ == "__main__":
    messages = []
    #city = "Houston"
    city = input("Enter city name: ")
    add_user_message(
        messages,
        f"What is the weather like in {city}",
    )
    run_conversation(messages)