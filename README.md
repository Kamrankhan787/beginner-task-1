# Beginner-Friendly Tool-Calling AI Agent

This is a terminal-based AI agent built using Python and the OpenAI SDK. It demonstrates how to give an AI the ability to call custom Python functions (tools) to extend its capabilities.

## Setup Instructions

1.  **Install Dependencies:**
    Make sure you have Python installed. Then run:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Environment Variables:**
    Open the `.env` file and replace `your_openai_api_key_here` with your actual OpenAI API key. You can get one from [platform.openai.com](https://platform.openai.com/).

3.  **Run the Agent:**
    Execute the main script:
    ```bash
    python main.py
    ```

## Educational Concepts

### How Function Calling Works
Function calling (or Tool Calling) allows an LLM (Large Language Model) to connect to external tools. Instead of just replying with text, the model is provided with a list of available tools and their descriptions. 
When the model realizes it needs a tool to answer your prompt (e.g., you ask "What's 15 * 4?"), it pauses its text generation and outputs a special JSON response requesting to call the "calculator" tool. Your Python code intercepts this request, runs the actual `calculator()` function, and sends the result back to the model. Finally, the model uses that result to construct its final answer to you.

### Why JSON Responses are Useful
JSON (JavaScript Object Notation) is a structured data format. When the model needs to call a tool, it outputs the arguments in JSON format. This is incredibly useful because our Python program can easily parse JSON into a Python dictionary. It provides a reliable, machine-readable way for the AI to "communicate" with our code, ensuring the AI provides the exact parameters our functions expect (like `{ "operation": "multiply", "a": 15, "b": 4 }`) rather than a messy paragraph of text.

### How Error Handling Improves Agents
When dealing with external APIs, network connections, or unpredictable AI outputs, things can go wrong. The model might hallucinate a tool that doesn't exist, or provide invalid arguments (like a string where a number was expected).
Proper error handling (using `try/except` blocks in Python) ensures that instead of the entire program crashing abruptly, the agent can gracefully handle the error. We can catch the error, inform the user, or even send the error message back to the AI model so it can try to correct its mistake on its own!
