import os
import sys
import io
import subprocess

try:
    import gradio as gr
    GRADIO_AVAILABLE = True
except ImportError:
    GRADIO_AVAILABLE = False
    print("Error: Gradio is not installed. Install it with: pip install gradio")
    exit(1)

# Import functions from main.py to avoid code duplication
from main import optimize, write_output

def execute_python(code):
    try:
        output = io.StringIO()
        sys.stdout = output
        
        # Create a proper execution namespace that includes built-ins
        namespace = {'__builtins__': __builtins__}
        
        # Execute the code in the namespace
        exec(code, namespace)
        
    except Exception as e:
        return f"Error executing Python code: {str(e)}"
    finally:
        sys.stdout = sys.__stdout__
    return output.getvalue()


def execute_cpp(code, model_name):
        write_output(code, model_name)
        try:
            program_file = os.path.join("output", f"optimized_{model_name.lower()}.cpp")
            compile_cmd = ["clang++", "-Ofast", "-std=c++17", "-march=armv8.5-a",
                           "-mtune=apple-m1", "-mcpu=apple-m1", "-o", "optimized", program_file]
            compile_result = subprocess.run(compile_cmd, check=True, text=True, capture_output=True)
            run_cmd = ["./optimized"]
            run_result = subprocess.run(run_cmd, check=True, text=True, capture_output=True)
            return run_result.stdout
        except subprocess.CalledProcessError as e:
            return f"An error occurred:\n{e.stderr}"

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
        gr.Markdown("## 🚀 Convert code from Python to C++")
        
        with gr.Row():
            python = gr.Textbox(
                label="Python code:", 
                value=python_sample, 
                lines=10,
                placeholder="Enter your Python code here..."
            )
            cpp = gr.Textbox(
                label="C++ code:", 
                lines=10,
                placeholder="Generated C++ code will appear here..."
            )
        
        with gr.Row():
            model = gr.Dropdown(
                ["GPT", "Claude"], 
                label="Select model", 
                value="GPT"
            )
        
        with gr.Row():
            convert = gr.Button("Convert code", variant="primary")
        
        with gr.Row():
            python_run = gr.Button("🐍 Run Python", variant="secondary")
            cpp_run = gr.Button("⚡ Run C++", variant="secondary")
        
        with gr.Row():
            python_out = gr.TextArea(
                label="Python result:", 
                lines=8,
                placeholder="Python execution output will appear here..."
            )
            cpp_out = gr.TextArea(
                label="C++ result:", 
                lines=8,
                placeholder="C++ execution output will appear here..."
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
        python_run.click(execute_python, inputs=[python], outputs=[python_out])
        cpp_run.click(execute_cpp, inputs=[cpp, model], outputs=[cpp_out])
        
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