def calculator(operation: str, a: float, b: float) -> str:
    """
    A simple calculator that performs basic arithmetic operations.
    """
    try:
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                return "Error: Cannot divide by zero."
            result = a / b
        else:
            return f"Error: Unknown operation '{operation}'."
        
        return f"The result of {a} {operation} {b} is {result}"
    except Exception as e:
        return f"Error executing calculator: {str(e)}"

# The schema describes the tool to the AI model
calculator_schema = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Perform basic arithmetic operations like addition, subtraction, multiplication, and division.",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "The arithmetic operation to perform."
                },
                "a": {
                    "type": "number",
                    "description": "The first number."
                },
                "b": {
                    "type": "number",
                    "description": "The second number."
                }
            },
            "required": ["operation", "a", "b"]
        }
    }
}
