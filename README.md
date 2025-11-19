# Claude-Weather-Report
Simple AI using Claude API to report the Weather

First install all necessary packages to run claude and other os packages using the following commands in terminal:
```bash
pip install anthropic python-dotenv
pip install -r requirements.txt
```

This code requires API keys to use Claude API and Open Weather API. You can get free keys from the following:
* Claude: https://console.anthropic.com/
* Open Weather: https://openweathermap.org/api

In .env file add both your Claude API Key and your Open Weather API Key.
```python
ANTHROPIC_API_KEY="Your Claude Anthropic API Key here"
OPENWEATHER_KEY="Your Open weater API Key here"
```

Currently this code is very simple and only runs basic questions and in an early phase of simply answering weather questions in a terminal. Right now I have it so that it only takes a single question hard written in the code to ask current weather of a city.

To run the basic testing code, in a terminal run this line:
```bash
python test.py
```

Plans to advance the code:
* Directly have the users talk with the weather agent in the terminal
* Create tools to use Open Weather's geocode API to get more precise weather information
* Be able to retrieve weather data from the past
* Retrieve weather predictions in the near future.

