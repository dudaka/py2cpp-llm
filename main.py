import os
from dotenv import load_dotenv

from openai import OpenAI 
from anthropic import Anthropic

load_dotenv()

OPENAI_MODEL = "gpt-4o"
ANTHROPIC_MODEL = "claude-3-5-sonnet-20240620"

system_message = """
You are a helpful assistant that implements Python code in high performance C++ for a M4 Mac.
Respond only with the C++ code; use comments sparingly and do not provide any explanations other than occasional comments.
The C++ response needs to produce an identical output in the fastest possible time.
"""

def initialize_clients():
    """Initialize OpenAI and Anthropic clients using API keys from environment variables."""
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Check if API keys are available
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        if not anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        openai_client = OpenAI(api_key=openai_api_key)
        anthropic_client = Anthropic(api_key=anthropic_api_key)
        
        print("OpenAI and Anthropic clients initialized successfully.")
        return openai_client, anthropic_client
        
    except ValueError as ve:
        print(f"Configuration error: {ve}")
        raise
    except Exception as e:
        print(f"Error initializing clients: {e}")
        raise

openai, claude = initialize_clients()
    
def user_prompt_for(python_code):
    user_prompt = f"""
    Rewrite this Python code in C++ with the fastest possible implementation that produces identical output in the least time.
    Respond only with the C++ code; do not explain your work other than a few comments.
    Pay attention to number types to ensure no int overflows. Remember to #include all necessary C++ packages such as iomanip.


    {python_code}
    """
    return user_prompt

def message_for(python_code):
    return [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_prompt_for(python_code)}
    ]

def write_output(cpp_code):
    code = cpp_code.replace("```cpp", "").replace("```", "").strip()
    with open('optimized.cpp', 'w') as f:
        f.write(code)

def optimize_gpt(python_code):
    stream = openai.chat.completions.create(
        model=OPENAI_MODEL,
        messages=message_for(python_code),
        temperature=0,
        stream=True
    )
    reply = ""
    for chunk in stream:
        fragment = chunk.choices[0].delta.get("content", "")
        reply += fragment
        print(fragment, end="", flush=True)
    write_output(reply)

def optimize_claude(python_code):
    result = claude.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=2000,
        system=system_message,
        messages=[
            {"role": "user", "content": user_prompt_for(python_code)}
        ]
    )
    reply = ''
    with result as stream:
        for text in stream:
            reply += text
            print(text, end="", flush=True)
    write_output(reply)

if __name__ == "__main__":
    pass