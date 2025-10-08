import os

try:
    import gradio as gr
    GRADIO_AVAILABLE = True
except ImportError:
    GRADIO_AVAILABLE = False
    print("Error: Gradio is not installed. Install it with: pip install gradio")
    exit(1)

# Import functions from main.py to avoid code duplication
from main import optimize

def optimize_for_gradio_streaming(python_code, model_name):
    """Streaming version for real-time UI updates"""
    try:
        if not python_code.strip():
            yield "Please enter some Python code to convert."
            return
        
        # Use the optimize function from main.py which now yields cleaned, progressive results
        # Use the streaming optimize function for real-time results
        result_generator = optimize(python_code, model=model_name, max_tokens=2000)
        
        for chunk in result_generator:
            yield chunk
        
    except Exception as e:
        yield f"Error during conversion: {str(e)}"

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
            optimize, 
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