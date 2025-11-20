import json
import requests



weather_tool_schema = {
    "name": "get_weather",
    "description": "Get current weather for a location",
    "input_schema": {
        "type": "object",
        "properties": {
            "latitude": {
                "type": "number",
            },
            "longitude": {
                "type": "number",
            }
        },
        "required": ["latitude", "longitude"]
    },
}

def run_tool(tool_name, tool_input):
    if tool_name == "get_weather":
        return get_weather(**tool_input)
    

# function to run multiple tools
def run_tools(message):
    tool_requests = [block for block in message.content if block.type == "tool_use"]
    tool_result_blocks = []

    for tool_request in tool_requests:
        try:
            tool_output = run_tool(tool_request.name, tool_request.input)
            tool_result_block = {
                "type": "tool_result",
                "tool_use_id": tool_request.id,
                "content": json.dumps(tool_output),
                "is_error": False,
            }
        except Exception as e:
            tool_result_block = {
                "type": "tool_result",
                "tool_use_id": tool_request.id,
                "content": f"Error: {e}",
                "is_error": True,
            }

        tool_result_blocks.append(tool_result_block)

    return tool_result_blocks



def get_weather(latitude, longitude):
    # Call Weather API
    url = (f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m&temperature_unit=fahrenheit")
    response = requests.get(url)
    data = response.json()

    return data

def get_forecast(latitude, longitude):
    return

