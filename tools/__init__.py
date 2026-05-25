from .calculator import calculator, calculator_schema
from .weather import get_weather, weather_schema
from .greeting import greeting, greeting_schema

# We create a mapping of function names to actual python functions.
# When the AI requests to call a function by name, we use this dictionary to find it.
available_tools = {
    "calculator": calculator,
    "get_weather": get_weather,
    "greeting": greeting,
}

# This is the list of schemas we will send to the OpenAI API so it knows what tools exist.
tool_schemas = [
    calculator_schema,
    weather_schema,
    greeting_schema
]
