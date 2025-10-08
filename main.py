import os
import argparse
from dotenv import load_dotenv

from openai import OpenAI 
from anthropic import Anthropic

load_dotenv()

OPENAI_MODEL = "gpt-4.1"
ANTHROPIC_MODEL = "claude-sonnet-4-5-20250929"

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

output_filename = "optimized.cpp"  # Global variable for output filename

def write_output(cpp_code, model_name=""):
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Generate filename with model name
    if model_name:
        filename = f"optimized_{model_name}.cpp"
    else:
        filename = "optimized.cpp"
    
    filepath = os.path.join("output", filename)
    
    code = cpp_code.replace("```cpp", "").replace("```", "").strip()
    with open(filepath, 'w') as f:
        f.write(code)
    
    return filepath

def optimize_gpt(python_code):
    stream = openai.chat.completions.create(
        model=OPENAI_MODEL,
        messages=message_for(python_code),
        stream=True
    )
    reply = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            fragment = chunk.choices[0].delta.content
            reply += fragment
            print(fragment, end="", flush=True)
    filepath = write_output(reply, "gpt")
    return filepath

def optimize_claude(python_code, max_tokens=2000):
    result = claude.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=max_tokens,
        system=system_message,
        messages=[
            {"role": "user", "content": user_prompt_for(python_code)}
        ]
    )
    reply = result.content[0].text
    print(reply, end="", flush=True)
    filepath = write_output(reply, "claude")
    return filepath

def main():
    parser = argparse.ArgumentParser(
        description="Convert Python code to optimized C++ using AI models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --file input.py --model gpt
  python main.py --code "print('Hello')" --model claude
  python main.py --file script.py --model both
        """
    )
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--file", "-f",
        type=str,
        help="Path to Python file to convert"
    )
    input_group.add_argument(
        "--code", "-c",
        type=str,
        help="Python code string to convert"
    )
    
    # Model selection
    parser.add_argument(
        "--model", "-m",
        choices=["gpt", "claude", "both"],
        default="gpt",
        help="AI model to use for conversion (default: gpt)"
    )
    
    # Max tokens for Claude
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=2000,
        help="Maximum tokens for Claude model (default: 2000)"
    )
    
    # Verbose output
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Get Python code from file or direct input
    if args.file:
        try:
            with open(args.file, 'r') as f:
                python_code = f.read()
            if args.verbose:
                print(f"Loaded Python code from: {args.file}")
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.")
            return 1
        except Exception as e:
            print(f"Error reading file '{args.file}': {e}")
            return 1
    else:
        python_code = args.code
        if args.verbose:
            print("Using provided Python code string")
    
    if args.verbose:
        print(f"Using model: {args.model}")
        print("Output directory: output/")
        print("-" * 50)
    
    try:
        if args.model == "gpt":
            if args.verbose:
                print("Converting with GPT-4...")
            output_file = optimize_gpt(python_code)
            print(f"\nGenerated file: {output_file}")
        elif args.model == "claude":
            if args.verbose:
                print("Converting with Claude...")
            output_file = optimize_claude(python_code, args.max_tokens)
            print(f"\nGenerated file: {output_file}")
        elif args.model == "both":
            if args.verbose:
                print("Converting with both models...")
            print("\n=== GPT-4 Output ===")
            gpt_output = optimize_gpt(python_code)
            
            print(f"\n\n=== Claude Output ===")
            claude_output = optimize_claude(python_code, args.max_tokens)
            
            print(f"\nGenerated files:")
            print(f"  GPT-4: {gpt_output}")
            print(f"  Claude: {claude_output}")
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"Error during conversion: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())