from datetime import datetime
from utils.utils import log
import json
import requests

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_city_weather(city: str | None = None):
    res = requests.get(f"https://wttr.in/{city if city else ""}?format=%C+%t+%w")
    res.raise_for_status()
    return res.text.strip()

def get_user_city():
    return "Varanasi"

def run_tool(tool_call):
    func_name = tool_call.function.name
    
    try:
        args = json.loads(tool_call.function.arguments)
        log(f"🔧 {func_name}({args})")
        function = FUNCTION_NAME_TO_FUNCTION_MAP[func_name]
        output = function(**args)
    except Exception as e:
        output = f"Error while running {func_name}: {e}"
    
    log(f"  ➡️ {output}")
    return output
    
TOOLS = [
    {
        "type": "function",
        "function": {
            "name":"get_current_time",
            "description":"Returns the current date and time as a formatted String.",
            "parameters":{
                "type":"object",
                "properties":{}
            }
        }
    },
        {
        "type": "function",
        "function": {
            "name":"get_city_weather",
            "description":"Returns the current weather of the provided city, by default returns the current location weather.",
            "parameters":{
                "type":"object",
                "properties":{
                    "city":{
                        "type": "string",
                        "description": "Name of the city, e.g. Mumbai, Kochi"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name":"get_user_city",
            "description":"Returns the city where the user lives. Use this when the user says 'my city', 'my location', 'where i live' or any answer which depends on city but not provided",
            "parameters":{
                "type":"object",
                "properties":{}
            }
        }
    }
]

FUNCTION_NAME_TO_FUNCTION_MAP = {
    "get_current_time": get_current_time,
    "get_city_weather": get_city_weather,
    "get_user_city": get_user_city
}