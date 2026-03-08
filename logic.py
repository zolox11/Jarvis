import os
import re
import subprocess
import time
import requests
import getpass
from bs4 import BeautifulSoup
from ollama import Client

VISION_MODEL = "llava:7b"

client = Client()

SCREENSHOT_PATH = "/tmp/jarvis_screen.png"

BLOCKED_KEYWORDS = [
    "rm -rf /",
    "mkfs",
    ":(){:|:&};:",
    "shutdown",
    "reboot",
    "poweroff",
    "halt",
    "dd if=",
    "rm -rf ~",
    "mv ~",
    "mv /home",
    "chmod -R 777 /",
    "chown -R /",
]

# -------------------------
# SCREEN CAPTURE
# -------------------------
def capture_screen():
    """
    Capture the current screen using Wayland (grim) or X11 (import).
    """

    try:
        subprocess.run(
            ["grim", SCREENSHOT_PATH],
            check=True,
            capture_output=True,
        )
        return SCREENSHOT_PATH

    except Exception:
        try:
            subprocess.run(
                ["import", "-window", "root", SCREENSHOT_PATH],
                check=True,
                capture_output=True,
            )
            return SCREENSHOT_PATH
        except Exception:
            return None


# -------------------------
# WEB SCRAPER
# -------------------------
def fetch_web_content(url):
    """
    Fetch webpage content and clean it for LLM use.
    """

    try:

        if not url.startswith("http"):
            url = "https://" + url

        headers = {
            "User-Agent": "Jarvis-Agent/5.3"
        }

        r = requests.get(
            url,
            headers=headers,
            timeout=15,
        )

        r.raise_for_status()

        soup = BeautifulSoup(
            r.text,
            "html.parser",
        )

        for element in soup(
            ["script", "style", "nav", "footer", "header", "aside"]
        ):
            element.extract()

        text = soup.get_text(separator=" ")

        clean = re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

        return f"""
--- WEB DATA FROM {url} ---
{clean[:5000]}
"""

    except Exception as e:
        return f"Web Retrieval Error: {str(e)}"


# -------------------------
# FILE DOWNLOADER
# -------------------------
def download_resource(url, filename):
    """
    Download file safely into current working directory.
    """

    try:

        if not url.startswith("http"):
            url = "https://" + url

        r = requests.get(
            url,
            stream=True,
            timeout=30,
        )

        r.raise_for_status()

        path = os.path.join(
            os.getcwd(),
            filename,
        )

        with open(path, "wb") as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)

        return f"Downloaded to {path}"

    except Exception as e:
        return f"Download Failed: {str(e)}"


# -------------------------
# IMAGE ANALYSIS
# -------------------------
def analyze_image_with_vision(
    image_path,
    user_query="What is in this image?",
):
    """
    Use vision model to analyze an image.
    """

    path = os.path.expanduser(image_path)

    if not os.path.exists(path):
        return f"Image not found: {path}"

    try:

        resp = client.chat(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": user_query,
                    "images": [path],
                }
            ],
        )

        return resp.message.content

    except Exception as e:
        return f"Vision Error: {str(e)}"


# -------------------------
# SYSTEM CONTEXT
# -------------------------
def get_full_system_context():
    """
    Gather system information for the AI brain.
    """

    user = getpass.getuser()
    cwd = os.getcwd()
    home = os.path.expanduser("~")

    try:

        home_folders = [
            d
            for d in os.listdir(home)
            if os.path.isdir(os.path.join(home, d))
            and not d.startswith(".")
        ]

        cwd_contents = os.listdir(cwd)[:30]

        df = subprocess.getoutput(
            "df -h / | tail -1 | awk '{print $4\" available (\"$5\" used)\"}'"
        )

    except Exception:

        home_folders = []
        cwd_contents = []
        df = "Unknown"

    return f"""
OS: Arch Linux
USER: {user}
PWD: {cwd}
HOME_FOLDERS: {home_folders}
CWD_CONTENTS: {cwd_contents}
DISK_SPACE: {df}
TIME: {time.ctime()}
"""


# -------------------------
# SHELL EXECUTOR
# -------------------------
def execute_shell(command):
    """
    Safely execute shell commands requested by the AI.
    """

    command = command.strip()

    if not command:
        return "[Empty command]"

    # -------------------------
    # SECURITY FILTER
    # -------------------------
    if any(keyword in command for keyword in BLOCKED_KEYWORDS):
        return f"[SECURITY BLOCKED] {command}"

    # -------------------------
    # DIRECTORY HANDLING
    # -------------------------
    if command.startswith("cd "):

        try:

            target = os.path.expanduser(
                command.replace("cd ", "").strip()
            )

            if not target:
                target = os.path.expanduser("~")

            os.chdir(target)

            return f"Changed directory to {os.getcwd()}"

        except Exception as e:
            return f"CD Error: {str(e)}"

    # -------------------------
    # WALLPAPER SUPPORT
    # -------------------------
    try:
        if "swww" in command:
            subprocess.run(
                ["bash", "-c", "pgrep swww-daemon || swww-daemon &"],
                capture_output=True,
            )
    except Exception:
        pass

    # -------------------------
    # COMMAND EXECUTION
    # -------------------------
    try:

        result = subprocess.run(
            ["bash", "-c", command],
            capture_output=True,
            text=True,
            timeout=60,
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if stdout:
            return stdout

        if stderr:
            return stderr

        return "[Command executed successfully]"

    except subprocess.TimeoutExpired:
        return "[Command timed out]"

    except Exception as e:
        return f"Execution Error: {str(e)}"