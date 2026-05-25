def greeting(name: str, language: str = "english") -> str:
    """
    A simple greeting tool that returns a personalized greeting in the requested language.
    """
    lang = language.lower()
    
    if lang == "spanish":
        return f"¡Hola, {name}! ¡Espero que tengas un gran día!"
    elif lang == "french":
        return f"Bonjour, {name}! J'espère que vous passez une bonne journée!"
    elif lang == "japanese":
        return f"こんにちは、{name}さん！良い一日を！"
    else:
        # Default to English
        return f"Hello, {name}! I hope you're having a great day!"

# The schema describes the tool to the AI model
greeting_schema = {
    "type": "function",
    "function": {
        "name": "greeting",
        "description": "Generate a friendly, personalized greeting in the specified language.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the person to greet."
                },
                "language": {
                    "type": "string",
                    "enum": ["english", "spanish", "french", "japanese"],
                    "description": "The language for the greeting. Defaults to english."
                }
            },
            "required": ["name"]
        }
    }
}
