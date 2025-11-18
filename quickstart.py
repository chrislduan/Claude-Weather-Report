# Load env variables
from dotenv import load_dotenv
load_dotenv()  # Load variables from .env file

# Create API client
import anthropic

client = anthropic.Anthropic()
model = "claude-haiku-4-5"

# imports
import json
from anthropic.types import Message
from chat_functions import add_assistant_message, add_user_message, chat
import tools

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
            # tools=[
            #     date_tools.get_current_datetime_schema,
            #     date_tools.add_duration_to_datetime_schema,
            #     date_tools.set_reminder_schema,
            #     base.batch_tool_schema
            # ],
        )

        add_assistant_message(messages, response)
        print(chat.text_from_message(response))

        if response.stop_reason != "tool_use":
            break

        # tool_results = base.run_tools(response)
        # chat.add_user_message(messages, tool_results)
        add_user_message(messages)

    return messages


if __name__ == "__main__":
    messages = []
    # add_user_message(
    #     messages,
    #     """Set two reminders for Jan 1, 2050 at 8 am:
    #             * I have a doctors appointment
    #             * Taxes are due
    #     """,
    # )
    add_user_message(
        messages,
        message
    )
    run_conversation(messages)