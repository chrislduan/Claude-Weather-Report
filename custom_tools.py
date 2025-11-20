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

weather_forecast_schema = {
    "name": "get_forecast",
    "description": "Get 7 day weather forecast for a location",
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
    if tool_name == "get_forecast":
        return get_forecast(**tool_input)
    

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
    url = (f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m&temperature_unit=fahrenheit&timezone=auto")
    response = requests.get(url)
    data = response.json()

    return data

def get_forecast(latitude, longitude):
    url = ("https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        "&timezone=auto")
    response = requests.get(url)
    data = response.json()

    daily = data["daily"]

    forecast = []
    for day in range(len(daily["time"])):
        forecast.append({
            "date": daily["time"][day],
            "temp_max": daily["temperature_2m_max"][day],
            "temp_min": daily["temperature_2m_min"][day],
            "precipitation_sum": daily["precipitation_sum"][day]
        })
    return forecast

