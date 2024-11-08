import os 
import platform

# Get the operating system with more detailed information
os_name = platform.system()
os_version = platform.release()
os_architecture = platform.architecture()[0]  # x64 or x32
user_name = os.getlogin()

# Check if the OS is Windows
if os_name == "Windows":
    full_os_name = f"{os_name} {os_version} {os_architecture}"
else:
    full_os_name = f"{os_name} {os_architecture}"

full_info_os = f"My operating system: {full_os_name}. My username: {user_name}"
