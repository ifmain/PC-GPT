import re
import ast
import io
import sys

def extract_python_code(generated_text):
    # Extracting Python code from generated text...
    code_match = re.search(r"```python\n(.*?)```", generated_text, re.DOTALL)
    if code_match:
        # Python code successfully extracted.
        return code_match.group(1)
    print("Markdown-formatted code not found, returning original text.")
    return generated_text

def execute_generated_code(generated_code):
    # Creating an object to capture output
    output = io.StringIO()
    # Saving current stdout
    old_stdout = sys.stdout
    sys.stdout = output

    try:
        # Syntax check
        code = ast.parse(generated_code)
        # Code execution
        exec(generated_code, globals())
    except SyntaxError as e:
        print(f"Syntax error in generated code: {e}")
    except Exception as e:
        print(f"Error executing generated code: {e}")
    finally:
        # Restoring stdout
        sys.stdout = old_stdout

    # Getting execution result
    return output.getvalue()
