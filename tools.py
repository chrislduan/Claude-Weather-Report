# Date and time tools and schemas
from datetime import datetime, timedelta
from anthropic.types import ToolParam
import os
import requests
import requests_cache
from retry_requests import retry
import openmeteo_requests
import json

# Open Weather API
WEATHER_API = "https://api.openweathermap.org/data/2.5/weather"
GEO_API = "https://api.openweathermap.org/geo/1.0/direct"
METEO_API = "https://api.open-meteo.com/v1/forecast"
METEO_GEO_API = "https://geocoding-api.open-meteo.com/v1/search"


# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)



# tool schema to run multiple tools simultaneously
batch_tool_schema = {
    "name": "batch_tool",
    "description": "Invoke multiple other tool calls simultaneously",
    "input_schema": {
        "type": "object",
        "properties": {
            "invocations": {
                "type": "array",
                "description": "The tool calls to invoke",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the tool to invoke",
                        },
                        "arguments": {
                            "type": "string",
                            "description": "The arguments to the tool, encoded as a JSON string",
                        },
                    },
                    "required": ["name", "arguments"],
                },
            }
        },
        "required": ["invocations"],
    },
}


# function to run multiple tools
def run_batch(invokations={}):
    batch_output = []

    for invokation in invokations:
        name = invokation["name"]
        args = json.loads(invokation["arguments"])

        tool_output = run_tool(name, args)

        batch_output.append({"tool_name": name, "output": tool_output})

    return batch_output

# function to run single tool
def run_tool(tool_name, tool_input):
    if tool_name == "get_current_datetime":
        return get_current_datetime(**tool_input)
    elif tool_name == "add_duration_to_datetime":
        return add_duration_to_datetime(**tool_input)
    elif tool_name == "meteo_get_city_geocode":
        return meteo_get_city_geocode(**tool_input)
    elif tool_name == "get_geocode_weather":
        return get_geocode_weather(**tool_input)
    elif tool_name == "get_daily_forecast":
        return get_daily_forecast(**tool_input)
    elif tool_name == "batch_tool":
        return run_batch(**tool_input)
    
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



# Open weather Geocoding tool schema
city_geocode_tool_schema = {
    "name": "get_city_geocode",
    "description": "Get geocode for a city",
    "input_schema":{
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The city, e.g. San Francisco"
            },
            "state": {
                "type": "string",
                "description": "The state, e.g. CA or California"
            },
            "country": {
                "type": "string",
                "description": "The coutnry, e.g. Mexico"
            }
        },
        "required": ["city"]
    }
}

# code to receive city and convert to geo code on open weather API
def get_city_geocode(city, country):
    params = {
        "q": f"{city},{country}",
        "appid": os.environ["OPENWEATHER_KEY"],
        "limit": 1,
    }
    response = requests.get(GEO_API, params)
    response.raise_for_status()

    data = response.json()
    return {"lat": data[0]["lat"], "lon": data[0]["lon"]}

# Meteo Geocoding tool schema
meteo_city_geocode_tool_schema = {
    "name": "meteo_get_city_geocode",
    "description": "Get geocode for a city",
    "input_schema":{
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The name of the location, e.g. San Francisco, CA"
            }
        },
        "required": ["name"]
    }
}

# code to receive city and convert to geo code on meteo API
def meteo_get_city_geocode(city, country):
    params = {
        "q": f"{city},{country}",
        "appid": os.environ["OPENWEATHER_KEY"],
        "limit": 1,
    }
    response = requests.get(GEO_API, params)
    response.raise_for_status()

    data = response.json()
    return {"lat": data[0]["lat"], "lon": data[0]["lon"]}


# Location Weather tool schema
geocode_weather_tool_schema = {
    "name": "get_geocode_weather",
    "description": "Get current weather for a geocode (latitude and longitude)",
    "input_schema": {
        "type": "object",
        "properties": {
            "lat": {
                "type": "number",
                "description": "The latitude"
            },
            "lon": {
                "type": "number",
                "description": "The longitude"
            },
            "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "The unit of temperature, either 'celsius' or 'fahrenheit'"
            }
        },
        "required": ["lat", "lon"]
    },
}

# get weather from location call
def get_geocode_weather(lat, lon, unit="celcius"):
    params = {
        "lat": lat,
        "lon": lon,
        "appid": os.environ["OPENWEATHER_KEY"],
        "unit": unit
    }
    response = requests.get(WEATHER_API, params=params)
    response.raise_for_status()
    return response.json()


# Get current date and time to be used in the future when asking for current weather
def get_current_datetime(date_format="%Y-%m-%d %H:%M:%S"):
    if not date_format:
        raise ValueError("date_format cannot be empty")
    return datetime.now().strftime(date_format)


get_current_datetime_schema = ToolParam(
    {
        "name": "get_current_datetime",
        "description": "Returns the current date and time formatted according to the specified format string. This tool provides the current system time formatted as a string. Use this tool when you need to know the current date and time, such as for timestamping records, calculating time differences, or displaying the current time to users. The default format returns the date and time in ISO-like format (YYYY-MM-DD HH:MM:SS).",
        "input_schema": {
            "type": "object",
            "properties": {
                "date_format": {
                    "type": "string",
                    "description": "A string specifying the format of the returned datetime. Uses Python's strftime format codes. For example, '%Y-%m-%d' returns just the date in YYYY-MM-DD format, '%H:%M:%S' returns just the time in HH:MM:SS format, '%B %d, %Y' returns a date like 'May 07, 2025'. The default is '%Y-%m-%d %H:%M:%S' which returns a complete timestamp like '2025-05-07 14:32:15'.",
                    "default": "%Y-%m-%d %H:%M:%S",
                }
            },
            "required": [],
        },
    }
)


# Add duration to use when asking for weather certain days away from current date
def add_duration_to_datetime(
    datetime_str, duration=0, unit="days", input_format="%Y-%m-%d"
):
    date = datetime.strptime(datetime_str, input_format)

    if unit == "seconds":
        new_date = date + timedelta(seconds=duration)
    elif unit == "minutes":
        new_date = date + timedelta(minutes=duration)
    elif unit == "hours":
        new_date = date + timedelta(hours=duration)
    elif unit == "days":
        new_date = date + timedelta(days=duration)
    elif unit == "weeks":
        new_date = date + timedelta(weeks=duration)
    elif unit == "months":
        month = date.month + duration
        year = date.year + month // 12
        month = month % 12
        if month == 0:
            month = 12
            year -= 1
        day = min(
            date.day,
            [
                31,
                29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                31,
                30,
                31,
                30,
                31,
                31,
                30,
                31,
                30,
                31,
            ][month - 1],
        )
        new_date = date.replace(year=year, month=month, day=day)
    elif unit == "years":
        new_date = date.replace(year=date.year + duration)
    else:
        raise ValueError(f"Unsupported time unit: {unit}")

    return new_date.strftime("%A, %B %d, %Y %I:%M:%S %p")


add_duration_to_datetime_schema = {
    "name": "add_duration_to_datetime",
    "description": "Adds a specified duration to a datetime string and returns the resulting datetime in a detailed format. This tool converts an input datetime string to a Python datetime object, adds the specified duration in the requested unit, and returns a formatted string of the resulting datetime. It handles various time units including seconds, minutes, hours, days, weeks, months, and years, with special handling for month and year calculations to account for varying month lengths and leap years. The output is always returned in a detailed format that includes the day of the week, month name, day, year, and time with AM/PM indicator (e.g., 'Thursday, April 03, 2025 10:30:00 AM').",
    "input_schema": {
        "type": "object",
        "properties": {
            "datetime_str": {
                "type": "string",
                "description": "The input datetime string to which the duration will be added. This should be formatted according to the input_format parameter.",
            },
            "duration": {
                "type": "number",
                "description": "The amount of time to add to the datetime. Can be positive (for future dates) or negative (for past dates). Defaults to 0.",
            },
            "unit": {
                "type": "string",
                "description": "The unit of time for the duration. Must be one of: 'seconds', 'minutes', 'hours', 'days', 'weeks', 'months', or 'years'. Defaults to 'days'.",
            },
            "input_format": {
                "type": "string",
                "description": "The format string for parsing the input datetime_str, using Python's strptime format codes. For example, '%Y-%m-%d' for ISO format dates like '2025-04-03'. Defaults to '%Y-%m-%d'.",
            },
        },
        "required": ["datetime_str"],
    },
}

daily_forecast_schema = {
    "name": "get_daily_forecast",
    "description": "Get daily forecast for a geocode (latitude and longitude)",
    "input_schema": {
        "type": "object",
        "properties": {
            "lat": {
                "type": "number",
                "description": "The latitude"
            },
            "lon": {
                "type": "number",
                "description": "The longitude"
            }
        },
        "required": ["lat", "lon"]
    },
}

def get_daily_forecast(lat, lon):
    params = {
        "lat": lat,
        "lon": lon,
        "appid": os.environ["OPENWEATHER_KEY"],
    }
    response = requests.get(DAILY_FORECAST_API, params=params)
    response.raise_for_status()
    return response.json()

