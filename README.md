# Py2Cpp LLM

A command-line tool that converts Python code to high-performance C++ using AI models (OpenAI GPT-4 and Anthropic Claude). The tool is specifically optimized for M4 Mac architecture and focuses on generating the fastest possible C++ implementation that produces identical output to the original Python code.

## Features

- **Dual AI Support**: Choose between GPT-4 or Claude, or use both for comparison
- **Optimized for M4 Mac**: Generated C++ code is optimized for Apple Silicon architecture
- **Multiple Input Methods**: Convert from Python files or direct code strings
- **Automatic Output Management**: Generated C++ files are organized in an `output/` directory
- **Clean C++ Code**: Minimal comments, focused on performance and correctness

## Requirements

- Python 3.7+
- OpenAI API key (for GPT-4)
- Anthropic API key (for Claude)
- clang++ compiler (for compiling generated C++ code)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/dudaka/py2cpp-llm.git
cd py2cpp-llm
```

2. Install dependencies:

```bash
pip install openai anthropic python-dotenv
```

3. Set up environment variables in `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## Usage

### Basic Usage

Convert a Python file using GPT-4:

```bash
python main.py --file your_script.py --model gpt
```

Convert a Python code string using Claude:

```bash
python main.py --code "print('Hello World')" --model claude
```

Use both models for comparison:

```bash
python main.py --file your_script.py --model both
```

### Command Line Options

- `--file, -f`: Path to Python file to convert
- `--code, -c`: Python code string to convert directly
- `--model, -m`: AI model to use (`gpt`, `claude`, or `both`)
- `--max-tokens`: Maximum tokens for Claude model (default: 2000)
- `--verbose, -v`: Enable detailed output messages
- `--help, -h`: Show help message

### Examples

```bash
# Convert a Python file with GPT-4
python main.py --file programs/fibonacci.py --model gpt

# Convert inline code with Claude
python main.py --code "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)" --model claude

# Compare both models with verbose output
python main.py --file programs/pi.py --model both --verbose
```

## Output Files

Generated C++ files are saved in the `output/` directory with the following naming convention:

- GPT-4 output: `output/optimized_gpt.cpp`
- Claude output: `output/optimized_claude.cpp`

## Compiling Generated C++ Code

To compile and run the generated C++ programs on M4 Mac:

```bash
# Compile with optimizations for M4 Mac
clang++ -O3 -std=c++17 -march=armv8.3-a -o optimized output/optimized_gpt.cpp

# Run the compiled program
./optimized
```

### Compilation Options Explained

- `-O3`: Maximum optimization level for performance
- `-std=c++17`: Use C++17 standard
- `-march=armv8.3-a`: Optimize for Apple Silicon M4 architecture
- `-o optimized`: Output executable name

You can also compile Claude's output:

```bash
clang++ -O3 -std=c++17 -march=armv8.3-a -o optimized_claude output/optimized_claude.cpp
./optimized_claude
```

## Project Structure

```
py2cpp-llm/
├── main.py              # Main application
├── .env                 # Environment variables (API keys)
├── .gitignore          # Git ignore rules
├── README.md           # This file
├── output/             # Generated C++ files (created automatically)
│   ├── optimized_gpt.cpp
│   └── optimized_claude.cpp
└── programs/           # Example Python programs (optional)
```

## How It Works

1. **Input Processing**: The tool accepts Python code from files or direct input
2. **AI Conversion**: Uses OpenAI GPT-4 or Anthropic Claude to convert Python to C++
3. **Optimization Focus**: AI models are prompted to generate high-performance C++ code
4. **Output Generation**: Clean C++ code is saved to the `output/` directory
5. **Compilation Ready**: Generated code includes necessary headers and is ready to compile

## Tips for Best Results

- **Simple algorithms work best**: Focus on computational tasks rather than complex I/O operations
- **Clear Python code**: Well-structured Python code produces better C++ translations
- **Compare models**: Use `--model both` to compare GPT-4 and Claude outputs
- **Test thoroughly**: Always verify that C++ output produces identical results to Python

## License

This project is open source. Please check the repository for license details.
