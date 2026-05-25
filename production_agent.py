import os
import json
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import openai

# ==========================================
# 1. SETUP LOGGING (PRODUCTION LEVEL)
# ==========================================
# We use the built-in logging module instead of just 'print'.
# This allows us to write errors to a file (agent.log) while also 
# printing user-friendly messages to the terminal.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("agent.log"), # Save detailed logs to a file
        logging.StreamHandler()           # Also output to the console
    ]
)
logger = logging.getLogger(__name__)

# ==========================================
# 2. CONFIGURATION & CLIENT INIT
# ==========================================
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    logger.error("CRITICAL: OPENROUTER_API_KEY is missing from environment variables.")
    print("❌ Configuration Error: Please set your OPENROUTER_API_KEY in the .env file.")
    exit(1)

# We set a custom timeout and change the base_url to OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key, 
    timeout=10.0
)

# ==========================================
# 3. DEFINE LOCAL FUNCTIONS (TOOLS)
# ==========================================
def add_numbers(a: float, b: float) -> str:
    return str(a + b)

def get_weather(city: str) -> str:
    city = city.lower()
    if "tokyo" in city: return "The weather in Tokyo is sunny."
    elif "london" in city: return "The weather in London is rainy."
    return f"Weather data not found for {city}."

def get_current_time() -> str:
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

available_tools = {
    "add_numbers": add_numbers,
    "get_weather": get_weather,
    "get_current_time": get_current_time,
}

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
                    "city": {"type": "string", "description": "The name of the city"}
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
                "properties": {},
                "required": []
            }
        }
    }
]

# ==========================================
# 4. API CALL WITH RETRY MECHANISM
# ==========================================
def call_openai_with_retry(messages, tools=None, retries=3, delay=2):
    """
    A helper function that attempts to call the OpenAI API.
    If a temporary network or rate-limit error occurs, it waits and retries.
    """
    for attempt in range(retries):
        try:
            logger.info(f"Attempting OpenAI API call (Attempt {attempt + 1}/{retries})")
            
            kwargs = {
                "model": "openai/gpt-3.5-turbo", # OpenRouter uses publisher/model format
                "messages": messages
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"
                
            response = client.chat.completions.create(**kwargs)
            logger.info("OpenAI API call successful.")
            return response
            
        except openai.RateLimitError as e:
            logger.warning(f"Rate limit hit: {e}. Retrying in {delay} seconds...")
            print("⏳ The AI service is currently busy. Retrying...")
            time.sleep(delay)
            delay *= 2 # Exponential backoff (wait longer each time)
            
        except openai.APITimeoutError as e:
            logger.warning(f"API Timeout: {e}. Retrying in {delay} seconds...")
            print("⏳ The connection timed out. Retrying...")
            time.sleep(delay)
            
        except openai.APIConnectionError as e:
            logger.error(f"Network Connection Error: {e}.")
            print("❌ Network error: Could not connect to the AI service. Please check your internet.")
            return None # Don't retry a hard network failure
            
        except openai.APIError as e:
            logger.error(f"OpenAI API Error: {e}.")
            print("❌ An internal AI service error occurred. Please try again later.")
            return None
            
        except Exception as e:
            logger.exception("An unexpected critical error occurred during API call.")
            print("❌ An unexpected error occurred.")
            return None
            
    logger.error("Max retries exceeded. API call failed.")
    print("❌ Failed to reach the AI service after multiple attempts.")
    return None

# ==========================================
# 5. MAIN AGENT LOOP
# ==========================================
def run_agent():
    print("\n🚀 Production Agent online! Type your message (or 'exit' to quit).")
    messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
    
    while True:
        try:
            # INVALID INPUT HANDLING
            user_input = input("\n👤 You: ")
            if not user_input or not user_input.strip():
                print("⚠️ Please enter a valid message.")
                continue
                
            if user_input.lower() in ["exit", "quit"]:
                logger.info("User initiated shutdown.")
                break
                
            messages.append({"role": "user", "content": user_input})
            
            # 1st API Call
            response = call_openai_with_retry(messages, tools=tool_schemas)
            
            # If the API call failed entirely (e.g. max retries exceeded), recover gracefully
            if not response:
                messages.pop() # Remove the user's failed message so they can try again
                continue
            
            response_message = response.choices[0].message
            messages.append(response_message)
            
            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    func_name = tool_call.function.name
                    func_args_json = tool_call.function.arguments
                    logger.info(f"AI requested tool: {func_name} with args: {func_args_json}")
                    
                    try:
                        # JSON PARSING VALIDATION
                        func_args = json.loads(func_args_json)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON arguments from AI: {e}")
                        result = "Error: Invalid JSON parameters provided by AI."
                    else:
                        # SAFE TOOL EXECUTION
                        if func_name in available_tools:
                            try:
                                function_to_call = available_tools[func_name]
                                result = function_to_call(**func_args)
                                logger.info(f"Tool {func_name} executed successfully. Result: {result}")
                            except TypeError as e:
                                logger.error(f"Type Error executing {func_name} (Wrong arguments provided): {e}")
                                result = f"Error: Incorrect arguments provided for {func_name}."
                            except Exception as e:
                                logger.exception(f"Unexpected error executing {func_name}.")
                                result = f"Error: An unexpected failure occurred in {func_name}."
                        else:
                            logger.error(f"AI requested non-existent tool: {func_name}")
                            result = f"Error: Tool {func_name} does not exist."
                    
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": str(result),
                    })
                
                # 2nd API Call (to get final answer)
                second_response = call_openai_with_retry(messages)
                if second_response:
                    final_answer = second_response.choices[0].message.content
                    print(f"\n🤖 AI: {final_answer}")
                    messages.append({"role": "assistant", "content": final_answer})
                else:
                    print("\n🤖 AI: I encountered an error processing the tool results. Please try again.")
                    
            else:
                print(f"\n🤖 AI: {response_message.content}")
                
        # GLOBAL CRASH PREVENTION
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            logger.exception("A catastrophic error occurred in the main loop.")
            print("\n❌ A critical error occurred, but the agent recovered. You can continue chatting.")

if __name__ == "__main__":
    run_agent()
