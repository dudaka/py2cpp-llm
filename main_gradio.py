import os
from dotenv import load_dotenv

from openai import OpenAI 
from anthropic import Anthropic

try:
    import gradio as gr
    GRADIO_AVAILABLE = True
except ImportError:
    GRADIO_AVAILABLE = False
    print("Error: Gradio is not installed. Install it with: pip install gradio")
    exit(1)

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

# Initialize clients
openai_client, claude_client = initialize_clients()

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

def optimize_for_gradio(python_code, model_name):
    """Optimize function for Gradio UI - returns the complete C++ code"""
    try:
        if not python_code.strip():
            return "Please enter some Python code to convert."
        
        model = model_name.lower()
        
        if model == "gpt":
            # For GPT, we need to collect the streaming response
            stream = openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=message_for(python_code),
                stream=True
            )
            reply = ""
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    reply += chunk.choices[0].delta.content
            
        elif model == "claude":
            result = claude_client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=2000,
                system=system_message,
                messages=[
                    {"role": "user", "content": user_prompt_for(python_code)}
                ]
            )
            reply = result.content[0].text
        else:
            return "Error: Model must be 'GPT' or 'Claude'"
        
        # Clean the code response
        cpp_code = reply.replace("```cpp", "").replace("```", "").strip()
        return cpp_code
        
    except Exception as e:
        return f"Error during conversion: {str(e)}"

def load_program_files():
    """Load all Python programs from the programs directory"""
    programs = {}
    programs_dir = "programs"
    
    # Program descriptions for better UI
    descriptions = {
        "pi": "🥧 Pi Calculation - High-performance numerical computation using series approximation",
        "hard": "🔢 Complex Algorithm - Maximum subarray sum with random number generation using LCG"
    }
    
    if os.path.exists(programs_dir):
        for filename in os.listdir(programs_dir):
            if filename.endswith('.py'):
                filepath = os.path.join(programs_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                        # Use filename without extension as the key
                        base_name = filename[:-3]
                        program_name = descriptions.get(base_name, f"📄 {base_name.replace('_', ' ').title()}")
                        programs[program_name] = content
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
    
    # Fallback example if no programs directory or files
    if not programs:
        programs["📄 Fibonacci Example"] = """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
for i in range(10):
    print(f"fibonacci({i}) = {fibonacci(i)}")"""
    
    return programs

def create_gradio_ui():
    """Create and return the Gradio interface"""
    
    # Load programs from directory
    programs = load_program_files()
    
    # Use the first program as the default sample
    python_sample = list(programs.values())[0] if programs else ""
    
    with gr.Blocks(title="Python to C++ Converter", theme=gr.themes.Soft()) as ui:
        gr.Markdown("# 🚀 Python to C++ Converter")
        gr.Markdown("Convert Python code to optimized C++ using AI models (GPT-4 or Claude)")
        
        with gr.Row():
            with gr.Column():
                python = gr.Textbox(
                    label="📝 Python Code", 
                    lines=20, 
                    value=python_sample,
                    placeholder="Enter your Python code here...",
                    info="Paste or type your Python code that you want to convert to C++"
                )
                
                with gr.Row():
                    model = gr.Dropdown(
                        ["GPT", "Claude"], 
                        label="🤖 Select AI Model", 
                        value="GPT",
                        info="Choose which AI model to use for conversion"
                    )
                    convert = gr.Button("🔄 Convert to C++", variant="primary", size="lg")
            
            with gr.Column():
                cpp = gr.Textbox(
                    label="⚡ Generated C++ Code", 
                    lines=20,
                    placeholder="Generated C++ code will appear here...",
                    info="Optimized C++ code will be generated here"
                )
        
        with gr.Accordion("📋 Compilation Instructions", open=False):
            gr.Markdown("""
            ### For M4 Mac (Apple Silicon):
            ```bash
            # Save the C++ code to a file (e.g., optimized.cpp)
            clang++ -O3 -std=c++17 -march=armv8.3-a -o optimized optimized.cpp
            ./optimized
            ```
            
            ### For other systems:
            ```bash
            # General compilation
            g++ -O3 -std=c++17 -o optimized optimized.cpp
            ./optimized
            ```
            
            ### Compilation flags explained:
            - `-O3`: Maximum optimization for performance
            - `-std=c++17`: Use C++17 standard
            - `-march=armv8.3-a`: Optimize for Apple Silicon M4 (Mac only)
            """)

        convert.click(
            optimize_for_gradio, 
            inputs=[python, model], 
            outputs=[cpp],
            api_name="convert"
        )
        
        # Add example programs from the programs directory
        with gr.Accordion("💡 Example Python Programs", open=False):
            gr.Markdown("Click any button below to load example programs from the `programs/` directory:")
            
            # Create buttons for each program
            for program_name, program_code in programs.items():
                def create_load_function(code):
                    return lambda: code
                
                with gr.Row():
                    gr.Button(
                        program_name,
                        size="sm",
                        variant="secondary"
                    ).click(
                        create_load_function(program_code),
                        outputs=python
                    )
    
    return ui

def main():
    """Main function to launch the Gradio UI"""
    print("Starting Python to C++ Converter UI...")
    
    ui = create_gradio_ui()
    
    print("Launching Gradio interface...")
    print("The interface will open in your default web browser.")
    print("Press Ctrl+C to stop the server.")
    
    ui.launch(
        inbrowser=True,
        server_name="127.0.0.1",
        server_port=7860,
        share=False  # Set to True if you want to create a public link
    )

if __name__ == "__main__":
    main()