def get_weather(location: str) -> str:
    """
    A mock weather tool that returns hardcoded weather for specific locations.
    """
    # Convert location to lowercase for simple matching
    loc = location.lower()
    
    if "tokyo" in loc:
        return "The current weather in Tokyo is 22°C and sunny."
    elif "london" in loc:
        return "The current weather in London is 15°C and rainy."
    elif "new york" in loc:
        return "The current weather in New York is 18°C and cloudy."
    else:
        return f"I'm sorry, I don't have real-time weather data for '{location}'. Try Tokyo, London, or New York."

# The schema describes the tool to the AI model
weather_schema = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a given location. (Mock data for Tokyo, London, New York)",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city name to check the weather for, e.g., 'Tokyo' or 'London'."
                }
            },
            "required": ["location"]
        }
    }
}
