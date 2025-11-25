# Claude-Weather-Report

Simple AI using Claude API to report the Weather

## Set up
<!-- To use this code, you'll need a Claude API key. If you don't have one yet, you can sign up for free at console.anthropic.com.
    1. Go to console.anthropic.com and create an account
    2. On the left-hand menu scroll down and click **Manage API Keys**
    3. On the top-right of the page click **Create Key** and name your key and click **Add**
    4. Copy the key and save it somewhere safe.


1. Clone the repository:
```
git clone https://github.com/chrislduan/Claude-Weather-Report.git
cd Claude-Weather-Report
```

2. Install all necessary packages to run claude and other os packages using the following commands in terminal:
```bash
pip install -r requirements.txt
```
3. Create a ```.env local``` file in the root directory
This code requires API keys to use Claude API. You can get free keys from the following:
* Claude: https://console.anthropic.com/

In .env file add your Claude API Key
```python
ANTHROPIC_API_KEY="Your Claude Anthropic API Key here"
``` -->
To use this code, you can run it on GitHub via Codespace:
1. In the code section of this Github repo, click the green "Code" button
2. Then click "Codespace" and either click the "+" button or an available codespace if there is one.
3. This will take you to a VS Code interface with an open terminal window on the bottom.
4. Install all necessary packages to run claude and other os packages using the following commands in terminal:
```bash
pip install -r requirements.txt
```


## Running the Code
To run the basic code, in a terminal run this line:
```bash
python test.py
```
The code will prompt you and ask if you would like the current weather or the forecast.
The code will then prompt you for a city name.
After filling both prompts, the code will will display the information you requested.

You may exit the code by simply typing "exit"

Plans to advance the code:
* Be able to retrieve historic weather data.

