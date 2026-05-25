import json

def print_agent_message(content: str):
    """Prints standard text responses from the agent in a nice color."""
    print(f"\n🤖 Agent: {content}")

def print_tool_call(tool_name: str, arguments: str):
    """
    Prints the structured JSON response when the agent decides to use a tool.
    This helps beginners see the raw JSON data the model outputted.
    """
    print(f"\n🛠️  Agent wants to use the '{tool_name}' tool.")
    try:
        # We parse the JSON string back into a Python dictionary,
        # then re-dump it with an indent to format it neatly.
        parsed_args = json.loads(arguments)
        formatted_json = json.dumps(parsed_args, indent=2)
        print("📥 Structured JSON arguments provided by the model:")
        print(formatted_json)
    except json.JSONDecodeError:
        print("📥 Arguments (Raw String):")
        print(arguments)

def print_tool_result(tool_name: str, result: str):
    """Prints the result returned by our local Python function."""
    print(f"\n✅ Result from '{tool_name}' tool:")
    print(result)

def print_error(error_message: str):
    """Prints errors in red text."""
    print(f"\n❌ Error: {error_message}")
