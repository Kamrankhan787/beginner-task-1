import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================

# Load environment variables from the .env file (like your API key)
load_dotenv()

# Initialize the OpenAI client using the key from .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==========================================
# 2. DEFINE LOCAL FUNCTIONS (TOOLS)
# ==========================================

def add_numbers(a: float, b: float) -> str:
    """A simple tool that adds two numbers together."""
    return str(a + b)

def get_weather(city: str) -> str:
    """A mock weather tool that returns hardcoded weather."""
    city = city.lower()
    if "tokyo" in city:
        return "The weather in Tokyo is sunny."
    elif "london" in city:
        return "The weather in London is rainy."
    else:
        return f"Weather data not found for {city}."

def get_current_time() -> str:
    """A tool that returns the current time."""
    # Use Python's datetime library to get the real current time
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

# Map the function names (strings) to the actual Python functions
# This is how we register the functions to make them callable by our script
available_tools = {
    "add_numbers": add_numbers,
    "get_weather": get_weather,
    "get_current_time": get_current_time,
}

# ==========================================
# 3. DEFINE TOOL SCHEMAS
# ==========================================
# This schema is sent to OpenAI to explain *what* our tools do and *how* to use them.

tool_schemas = [
    {
        "type": "function",
        "function": {
            "name": "add_numbers",
            "description": "Add two numbers together.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "The first number"},
                    "b": {"type": "number", "description": "The second number"}
                },
                "required": ["a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a specific city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "The name of the city, e.g., 'Tokyo'"}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current date and time.",
            "parameters": {
                "type": "object",
                "properties": {}, # No arguments needed for this function
                "required": []
            }
        }
    }
]

# ==========================================
# 4. MAIN AGENT LOOP
# ==========================================

def run_agent():
    print("🤖 Agent online! Type your message (or 'exit' to quit).")
    
    # Store the conversation history so the AI remembers context
    messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
    
    while True:
        try:
            # 1. Get user input
            user_input = input("\n👤 You: ")
            if user_input.lower() in ["exit", "quit"]:
                break
                
            messages.append({"role": "user", "content": user_input})
            
            # 2. Send message to OpenAI, providing our tools
            # tool_choice="auto" means the AI automatically decides whether to call a tool or just talk
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                tools=tool_schemas,
                tool_choice="auto" 
            )
            
            response_message = response.choices[0].message
            messages.append(response_message) # Save the AI's response to history
            
            # 3. Check if the AI wants to use a tool
            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    # The AI returns the name of the function it wants to run
                    func_name = tool_call.function.name
                    # The AI returns the arguments it generated in JSON format
                    func_args_json = tool_call.function.arguments
                    
                    print(f"\n[SYSTEM] AI decided to use tool: {func_name}")
                    print(f"[SYSTEM] JSON arguments provided: {func_args_json}")
                    
                    # Convert the JSON string into a Python dictionary
                    func_args = json.loads(func_args_json)
                    
                    # Execute the actual Python function with the dictionary of arguments
                    function_to_call = available_tools[func_name]
                    result = function_to_call(**func_args)
                    
                    print(f"[SYSTEM] Result from execution: {result}")
                    
                    # 4. Send the tool's result back to the AI
                    # We format this specifically as a "tool" role message
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": result,
                    })
                
                # Make a second API call. The AI reads the tool result and formats a human-friendly final answer
                second_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )
                
                final_answer = second_response.choices[0].message.content
                print(f"\n🤖 AI: {final_answer}")
                messages.append({"role": "assistant", "content": final_answer})
                
            else:
                # The AI answered directly without using any tools
                print(f"\n🤖 AI: {response_message.content}")
                
        # 5. Try-Except Error Handling
        # This catches any errors (like network failures or bad JSON) so the script doesn't crash
        except Exception as e:
            print(f"\n❌ [ERROR] Something went wrong: {str(e)}")

if __name__ == "__main__":
    run_agent()
