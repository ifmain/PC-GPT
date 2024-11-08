import os
import json
import subprocess
import numpy as np
import wmi
import winreg
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import shlex
import logging

# Function to load the program database
def load_program_database():
    print("Loading the program database...")
    if os.path.exists("programs_db.json"):
        with open("programs_db.json", "r", encoding="utf-8") as f:
            return json.load(f)
    print("Program database not found. Returning an empty database.")
    return {}

# Function to save the program database with UTF-8 support
def save_program_database(programs_db):
    print("Saving the program database...")
    with open("programs_db.json", "w", encoding="utf-8") as f:
        json.dump(programs_db, f, ensure_ascii=False, indent=4)
    print("Program database saved.")

# Function to get a list of installed programs
def get_installed_programs():
    programs = []
    registry_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]
    
    for root_key in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
        for path in registry_paths:
            try:
                with winreg.OpenKey(root_key, path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            sub_key_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, sub_key_name) as sub_key:
                                try:
                                    display_name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                                except FileNotFoundError:
                                    display_name = None
                                
                                try:
                                    version = winreg.QueryValueEx(sub_key, "DisplayVersion")[0]
                                except FileNotFoundError:
                                    version = None
                                
                                try:
                                    publisher = winreg.QueryValueEx(sub_key, "Publisher")[0]
                                except FileNotFoundError:
                                    publisher = None
                                
                                try:
                                    install_location = winreg.QueryValueEx(sub_key, "InstallLocation")[0]
                                except FileNotFoundError:
                                    install_location = None
                                
                                try:
                                    install_date = winreg.QueryValueEx(sub_key, "InstallDate")[0]
                                except FileNotFoundError:
                                    install_date = None

                                if display_name:
                                    program_info = {
                                        "Name": display_name,
                                        "Version": version,
                                        "Publisher": publisher,
                                        "Installation Path": install_location,
                                        "Installation Date": install_date
                                    }
                                    programs.append(program_info)
                        except OSError:
                            continue
            except FileNotFoundError:
                continue

    return programs


def add_programs_from_paths(programs_db, search_paths):
    print("Scanning specified paths to find additional programs...")
    existing_programs = {prog["Name"].lower() for prog in programs_db}
    for search_path in search_paths:
        if not os.path.exists(search_path):
            continue
        for root, dirs, files in os.walk(search_path):
            for file in files:
                if file.lower().endswith(".exe"):
                    program_name = os.path.splitext(file)[0].lower()
                    if program_name not in existing_programs:
                        program_info = {
                            "Name": os.path.splitext(file)[0],
                            "Version": None,
                            "Publisher": None,
                            "Installation Path": os.path.join(root, file),
                            "Installation Date": None
                        }
                        programs_db.append(program_info)
                        existing_programs.add(program_name)
    return programs_db

def initialize_program_database(aggressive=False):
    print("Initializing the program database...")
    
    if aggressive:
        print("Forcing the initialization of the program database. Please wait...")
        programs_db = get_installed_programs()
    else:
        programs_db = load_program_database()
        if programs_db:
            print("Program database is already initialized.")
            return
        print("Initializing the program database. Please wait...")
        programs_db = get_installed_programs()
    
    # Scanning additional paths for .exe files
    search_paths = [
        "C:\\Program Files",
        "C:\\Program Files (x86)",
        "C:\\Users\\",
        "C:\\Windows\\system32"
    ]
    programs_db = add_programs_from_paths(programs_db, search_paths)
    
    save_program_database(programs_db)
    print("Initialization completed.")

# Optimized function for semantic search
def semantic_search(input_array, target_string, n=3):
    input_array = [str(item) if item is not None else "" for item in input_array]
    vectorizer = TfidfVectorizer()
    input_embeddings = vectorizer.fit_transform(input_array)
    target_embedding = vectorizer.transform([target_string])
    cos_scores = cosine_similarity(target_embedding, input_embeddings).flatten()
    top_results = np.argsort(cos_scores)[::-1][:n]
    results = [{"text": input_array[idx], "score": float(cos_scores[idx])} for idx in top_results]
    return results

# Function to find a program by name
def find_program(program_name):
    print(f"Searching for program '{program_name}'...")
    programs_db = load_program_database()
    program_names = [program['Name'] for program in programs_db]
    results = semantic_search(program_names, program_name)
    if results:
        best_match = results[0]
        print(f"Program found: {best_match['text']} (Similarity: {best_match['score']:.2f})")
        for program in programs_db:
            if program["Name"] == best_match["text"]:
                return program, best_match['score']
    print("Program not found.")
    return None

# Function to search for a program's path or uninstall command
def find_program_path_or_uninstall_command(program_name, command_type="run"):
    registry_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]
    
    for root_key in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
        for path in registry_paths:
            try:
                with winreg.OpenKey(root_key, path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            sub_key_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, sub_key_name) as sub_key:
                                display_name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                                if display_name == program_name:
                                    if command_type == "run":
                                        display_icon = winreg.QueryValueEx(sub_key, "DisplayIcon")[0]
                                        return display_icon.split(',')[0].strip()
                                    elif command_type == "uninstall":
                                        uninstall_string = winreg.QueryValueEx(sub_key, "UninstallString")[0]
                                        return uninstall_string
                        except (OSError, FileNotFoundError):
                            continue
            except FileNotFoundError:
                continue

    return None

def find_uninstall_command(program_name):
    """
    Searches for the uninstall command for a program in the Windows registry.

    :param program_name: Name of the program to uninstall
    :return: Uninstall command string or None if not found
    """
    registry_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]

    for root_key in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
        for path in registry_paths:
            try:
                with winreg.OpenKey(root_key, path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            sub_key_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, sub_key_name) as sub_key:
                                display_name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                                if program_name.lower() in display_name.lower():
                                    uninstall_string = winreg.QueryValueEx(sub_key, "UninstallString")[0]
                                    return uninstall_string
                        except (OSError, FileNotFoundError, KeyError):
                            continue
            except FileNotFoundError:
                continue
    return None

def get_silent_flags(uninstall_command):
    """
    Returns flags for silent uninstallation depending on the installer type.

    :param uninstall_command: Uninstall command string
    :return: List of additional flags
    """
    lower_cmd = uninstall_command.lower()
    if 'msiexec' in lower_cmd:
        return ['/quiet', '/norestart']
    elif 'uninstall.exe' in lower_cmd or 'setup.exe' in lower_cmd:
        return ['/S']
    elif 'setup.msi' in lower_cmd:
        return ['/quiet']
    else:
        return ['/S']  # Standard flag, can be modified if needed

def get_silent_flags_install(installer_path):
    """
    Returns flags for silent installation depending on the installer type.

    :param installer_path: Path to the installer file (.exe or .msi)
    :return: List of additional flags
    """
    lower_path = installer_path.lower()
    if lower_path.endswith('.msi'):
        return ['/quiet', '/norestart']
    elif lower_path.endswith('.exe'):
        # Attempt to determine installer type by common flags
        # Note that different installers may use different flags
        # The most common ones are represented here
        # Can be extended if necessary
        return ['/S', '/silent', '/quiet']
    else:
        return []

def install_program(installer_path):
    """
    Performs a silent installation of the program from the specified installer.

    :param installer_path: Full path to the installer file (.exe or .msi)
    """
    if not os.path.isfile(installer_path):
        print(f"Installer file not found: {installer_path}")
        return

    silent_flags = get_silent_flags_install(installer_path)

    # Determine the installer type
    lower_path = installer_path.lower()
    if lower_path.endswith('.msi'):
        # Use msiexec for installing MSI packages
        args = ['msiexec', '/i', installer_path] + silent_flags
    elif lower_path.endswith('.exe'):
        # Use EXE installers with silent flags
        # Some installers require additional handling
        args = [installer_path] + silent_flags
    else:
        print("Unsupported installer type. Only .exe and .msi files are supported.")
        return

    print(f"Executing installation command: {' '.join(args)}")

    try:
        result = subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("Program successfully installed.")
        print(result.stdout)
        # You can call a function here to update the installed programs database
        initialize_program_database(aggressive=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to install the program. Return code: {e.returncode}")
        print(f"Error: {e.stderr}")
    except FileNotFoundError:
        print("Installer file not found or inaccessible for execution.")

def uninstall_program(program_name):
    """
    Performs a silent uninstallation of a program by its name.

    :param program_name: Name of the program to uninstall
    """
    uninstall_command = find_uninstall_command(program_name)
    if uninstall_command:
        print(f"Uninstall command found: {uninstall_command}")

        # Get silent uninstallation flags
        silent_flags = get_silent_flags(uninstall_command)

        # Form argument list for subprocess.run
        if 'msiexec' in uninstall_command.lower():
            args = [uninstall_command] + silent_flags
        else:
            # Remove quotes from uninstall_command if present
            if uninstall_command.startswith('"') and uninstall_command.endswith('"'):
                uninstall_command = uninstall_command[1:-1]
            args = [uninstall_command] + silent_flags

        print(f"Executing command: {' '.join(args)}")

        try:
            # Check if the uninstall_command file exists
            import os
            if not os.path.isfile(uninstall_command):
                print("Executable file for uninstallation not found.")
                return

            # Execute the uninstallation command
            result = subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print("Program successfully uninstalled.")
            # Update the installed programs database
            initialize_program_database(aggressive=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to uninstall the program. Return code: {e.returncode}")
            print(f"Error: {e.stderr}")
        except FileNotFoundError:
            print("Executable file for uninstallation not found.")
    else:
        print("Program for uninstallation not found.")

# Function to run a program by its name
def run_program(program_name):
    program, score = find_program(program_name)
    if not program:
        logging.error("Program not found to run.")
        return

    install_path = program.get("Installation Path")
    if not install_path:
        logging.error("Program installation path not found.")
        return

    if os.path.isfile(install_path):
        # Path points directly to the executable file
        exe_path = install_path
        program_dir = os.path.dirname(exe_path)
        logging.info(f"Running program '{program['Name']}' from file: {exe_path}")
        try:
            subprocess.Popen([exe_path], cwd=program_dir)
            logging.info("Program started.")
        except Exception as e:
            logging.error(f"Failed to start the program. Error: {e}")
    elif os.path.isdir(install_path):
        # Path points to the installation directory, searching for .exe file
        exe_path = find_executable(install_path, program['Name'])
        if exe_path and os.path.isfile(exe_path):
            program_dir = os.path.dirname(exe_path)
            logging.info(f"Running program '{program['Name']}' from directory: {exe_path}")
            try:
                subprocess.Popen([exe_path], cwd=program_dir)
                logging.info("Program started.")
            except Exception as e:
                logging.error(f"Failed to start the program. Error: {e}")
        else:
            logging.error("Executable file for the program not found in the installation directory.")
    else:
        logging.error("Program installation path is neither a file nor a directory.")

# Helper function to find the executable file in the installation directory
def find_executable(install_path, program_name):
    """
    Recursively searches for an .exe file in the installation directory.
    Prefers a file matching the program name.
    """
    preferred_exe = f"{os.path.splitext(program_name)[0]}.exe"
    for root, dirs, files in os.walk(install_path):
        # Search for the preferred .exe file first
        for file in files:
            if file.lower() == preferred_exe.lower():
                return os.path.join(root, file)
        
        # Search for any .exe file if the preferred one is not found
        exe_files = [f for f in files if f.lower().endswith(".exe")]
        if exe_files:
            return os.path.join(root, exe_files[0])
    
    return None
