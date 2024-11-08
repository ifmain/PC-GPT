## PC Remote

PC Remote is a Python-based tool that allows automated interaction with Windows software programs. The project integrates the OpenAI API and various system libraries to search for, run, install, and uninstall programs on Windows, as well as capture system information and screenshots. PC Remote is licensed under the Apache License 2.0.

---

### Table of Contents

- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [APIs and Modules](#apis-and-modules)
- [License](#license)

---

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/username/PC_remote.git
   cd PC_remote
   ```

2. **Install Dependencies:**
   The project depends on external libraries such as `pydantic`, `openai`, `scikit-learn`, and `Pillow`. Install dependencies via:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up OpenAI API Key:**
   Replace the `api_key` in `tools/api_key_file.py` with your OpenAI API key:
   ```python
   api_key = "your-api-key-here"
   ```

4. **Run the Application:**
   Execute the `main.py` file:
   ```bash
   python main.py
   ```

### Project Structure

The project structure is organized into several directories and modules:

```
PC_remote/
├── main.py               # Entry point to interact with OpenAI and execute commands
├── tools/
│   ├── api_key_file.py   # Contains API keys and model settings
│   ├── getSystemInfo.py  # Collects system information
│   ├── parse_lib.py      # Extracts and executes Python code
│   ├── prog_lib.py       # Manages installed programs and runs semantic searches
│   ├── screen_lib.py     # Captures and encodes screenshots
│   └── system_prompt.py  # Defines prompts and descriptions for OpenAI
```

### Usage

The application performs tasks based on user commands and integrates with OpenAI's language model to generate, parse, and execute relevant code to automate system operations.

#### Examples of Commands

1. **Launch a Program**  
   To open an installed program, enter a command like `Launch Chrome` in the command prompt.

2. **Uninstall a Program**  
   To uninstall a program, enter `Uninstall Chrome`. The tool will:
   - Search for the program in the Windows registry.
   - Execute the uninstallation command if available.
   
3. **Install a Program**  
   To install a program from an installer path, enter `Install path/to/installer.exe`.

4. **Capture a Screenshot**  
   To capture a screenshot of the desktop, the tool uses `screen_lib.py` to generate a base64-encoded PNG image.

### APIs and Modules

The functionality of each module is as follows:

1. **api_key_file.py**  
   Stores OpenAI API configuration.

2. **getSystemInfo.py**  
   Collects OS details such as system type, version, and architecture.

3. **parse_lib.py**  
   - `extract_python_code`: Extracts Python code snippets from AI-generated text.
   - `execute_generated_code`: Executes the extracted code in a safe environment.

4. **prog_lib.py**  
   - Manages installed programs, loading from or saving to `programs_db.json`.
   - Includes functions to run, install, and uninstall programs.

5. **screen_lib.py**  
   Captures screenshots and encodes them as base64 for display and analysis.

6. **system_prompt.py**  
   Provides system prompt settings for interacting with the OpenAI API.

### License

This project is licensed under the Apache License 2.0. See the `LICENSE` file for details.
