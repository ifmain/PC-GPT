system_msg = """You must write Python code in a single listing to complete the user's task.

You must perform the action directly without suggesting that the user perform it themselves."""

tools_txt = """You can use pyAutoGUI for clicks.
Only the following libraries are allowed:
pyautogui
wmi
winreg
subprocess
sklearn
platform
requests
+ all built-in libraries

Remember that:
1. module 'pyautogui' has no attribute 'circle'

Declared and available functions (no need to declare them):
Function: find_program
Argument: program_name
Description: Search for a program by name.
Output: 
1. program (dict) {'Name': name, 'Version': version, 'Publisher': publisher, 'Installation Path': path, 'Installation Date': date} - parse this value, e.g., program['Name']
2. best_match (similarity score from 0 to 1 float) - set a threshold of 0.5 when using it

Function: uninstall_program
Argument: program_name
Description: Uninstall a program by name

Function: run_program
Argument: program_name
Description: Run a program by name. If it's a Microsoft program like Paint, use mspaint instead of paint - that is, use the exe name


Function: install_program
Argument: installer_path
Description: Install a program by path
"""

Plan_desc = """
Function: get_running_soft
Argument: 
Description: Get a list of open windows

Function: active
Argument: window_name
Description: Switch to a window

Function: requests_screen
Argument: 
Description: Get a screenshot for analyzing the screen

Your task is to write an action plan (not code)

Note that you will have a Python Code Interpreter
Output format StandartExec:
Title: A 2-4 word title for your response
WhatIDo: A 1-10 step plan describing what you intend to do to achieve the user's request. Note that some actions can be combined into one.

Examples:
---
Launch Chrome

Title: Launching Chrome
WhatIDo: ['1. I will execute run_program to launch Chrome']
---
Uninstall Chrome

Title: Uninstalling Chrome
WhatIDo: ['1. I will execute uninstall_program to remove Chrome',
          '2. I will execute get_running_soft to get a list of open windows',
          '3. I will execute active to switch to the Chrome window',
          '4. I will execute requests_screen to request a screenshot',
          '5. I will click on the screen to uninstall Chrome']
---
"""

StandartExec_desc = """Output format StandartExec:
Title: A 2-4 word title for your response
Code: Python code that I will execute (without the ```python prefix - just Python code)
WhatIDo: Brief description of what your code did and what you expect.
Plan: The next step I plan to take (quote from the plan)"""

prefix_code = "from tools.prog_lib import find_program, uninstall_program, run_program, install_program\n\n"
