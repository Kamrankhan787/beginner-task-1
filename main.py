import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from utils.helpers import print_agent_message, print_tool_call, print_tool_result, print_error
from tools import available_tools, tool_schemas

# 1. Setup Phase: Load API Keys
# This reads the .env file and sets the variables in the environment.
load_dotenv()

# Check if the API key is present
api_key = os.getenv("OPENAI_API_KEY")
if not api_key or api_key == "your_openai_api_key_here":
    print_error("OpenAI API key missing or invalid. Please update the .env file.")
    exit(1)

# Initialize the OpenAI Client
client = OpenAI(api_key=api_key)

def main():
    print("==================================================")
    print("Welcome to the Beginner-Friendly Tool-Calling Agent!")
    print("Type 'exit' or 'quit' to end the conversation.")
    print("==================================================")
    
    # We maintain a list of messages. This is our conversation history.
    # It starts with a system prompt telling the AI how to behave.
    messages = [
        {"role": "system", "content": "You are a helpful, friendly AI assistant. Use the tools provided to answer the user's questions."}
    ]
    
    while True:
        try:
            user_input = input("\n👤 You: ")
            
            if user_input.lower() in ['exit', 'quit']:
                print("\nGoodbye!")
                break
            if not user_input.strip():
                continue
            
            # Add the user's message to our conversation history
            messages.append({"role": "user", "content": user_input})
            
            # 2. API Call Phase: Send the conversation and available tools to the AI
            response = client.chat.completions.create(
                model="gpt-3.5-turbo", # You can also use gpt-4 or gpt-4o
                messages=messages,
                tools=tool_schemas,
                tool_choice="auto" # The AI decides if it needs to use a tool or not
            )
            
            # Extract the AI's response message
            response_message = response.choices[0].message
            
            # Add the AI's response to the conversation history
            messages.append(response_message)
            
            # 3. Handling Tool Calls
            # Check if the AI decided to call any tools
            if response_message.tool_calls:
                # The AI might decide to call multiple tools in parallel
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args_str = tool_call.function.arguments
                    
                    # Print the raw JSON tool request to the terminal
                    print_tool_call(function_name, function_args_str)
                    
                    # Ensure the tool exists in our local dictionary
                    if function_name in available_tools:
                        function_to_call = available_tools[function_name]
                        
                        try:
                            # Parse the JSON string into a Python dictionary of arguments
                            function_args = json.loads(function_args_str)
                            
                            # Execute our local Python function with the provided arguments
                            # Example: calculator(**{"operation":"add", "a":1, "b":2})
                            function_response = function_to_call(**function_args)
                            
                            # Print the result to the terminal
                            print_tool_result(function_name, str(function_response))
                            
                        except json.JSONDecodeError:
                            function_response = "Error: Invalid JSON arguments provided by the model."
                            print_error(function_response)
                        except TypeError as e:
                            function_response = f"Error: Model provided incorrect arguments for {function_name}. {str(e)}"
                            print_error(function_response)
                        except Exception as e:
                            function_response = f"Error executing {function_name}: {str(e)}"
                            print_error(function_response)
                    else:
                        function_response = f"Error: Tool '{function_name}' is not defined locally."
                        print_error(function_response)
                    
                    # 4. Feedback Loop: Send the tool's result back to the AI
                    # We append a special "tool" message to the history. 
                    # This tells the AI what happened when we ran the function it requested.
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_response),
                    })
                
                # Now that the AI has the tool results, we call the API *again*.
                # The AI will read the results and formulate its final answer to the user.
                second_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )
                
                final_answer = second_response.choices[0].message.content
                print_agent_message(final_answer)
                
                # Add the final answer to history
                messages.append({"role": "assistant", "content": final_answer})
                
            else:
                # If no tool calls were requested, the AI just answered normally
                if response_message.content:
                    print_agent_message(response_message.content)
                    
        # Graceful error handling for API issues, network issues, or keyboard interrupts
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print_error(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
