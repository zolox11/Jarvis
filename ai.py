import time
import base64
import requests
from logic import get_full_system_context
from ollama import Client as OllamaClient
from google import genai
from google.genai import types
import os

# -------------------------
# CONFIGURATION
# -------------------------
BRAIN_MODEL = "gemini-3-flash-preview"
VISION_MODEL = "llava:7b"

# Gemini API client (requires API key set in environment)
gemini_client = genai.Client()
ollama_client = OllamaClient()  # For vision processing

SYSTEM_PROMPT = """
You are Jarvis, a high-level Linux Autonomous Agent running on Arch Linux.

You have access to:
• Linux shell
• Web retrieval
• File downloads
• Computer vision

Your job is to safely execute user requests by reasoning step-by-step
and issuing commands when necessary.

--------------------------------------------------

AVAILABLE SPECIAL COMMANDS

FETCH_WEB <url>
DOWNLOAD <url> <filename>
ANALYZE_IMG <path>
SAVE_TEXT <filepath> <content>

All standard Linux shell commands are allowed.

--------------------------------------------------

STRICT OUTPUT FORMAT

INSTRUCTIONS:
PROCESS: <step-by-step reasoning>
PATHS: <file paths involved or NONE>
VISION: <True or False>

COMMANDS:
<one command per line or NONE>

OUTPUT:
<final message to the user>

--------------------------------------------------

RULES

1. NEVER use backticks in COMMANDS
2. ONLY ONE command per line
3. NO shell logic (no if, &&, ||, ;)
4. Use simple commands only
5. Wait for command results before issuing more commands
6. Always include OUTPUT
7. If no command is required write NONE
8. Never explain reasoning inside OUTPUT
"""


class JarvisBrain:

    def __init__(self):
        self.memory = []
        self.max_memory = 8
        self.last_activity = time.time()

    # -------------------------
    # CLEAN & VALIDATE RESPONSE
    # -------------------------
    def _clean_response(self, text: str) -> str:
        """Ensure AI response follows strict output format."""
        if "OUTPUT:" not in text:
            text += "\n\nOUTPUT:\nTask processed."
        if "COMMANDS:" not in text:
            text = text.replace(
                "OUTPUT:",
                "COMMANDS:\nNONE\n\nOUTPUT:"
            )
        return text

    def _trim_memory(self):
        """Trim memory to prevent excessive growth."""
        if len(self.memory) > self.max_memory * 2:
            self.memory = self.memory[-self.max_memory * 2:]

    # -------------------------
    # GEMINI 3.1 PRO CALL
    # -------------------------
    def _call_gemini(self, prompt: str) -> str:
        """Send prompt to Google Gemini 3.1 Pro for brain processing."""
        try:
            response = gemini_client.models.generate_content(
                model=BRAIN_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_level="high")
                )
            )
            return response.text.strip()
        except Exception as e:
            return f"Brain API Error: {str(e)}"

    # -------------------------
    # VISION ANALYSIS (OLLAMA)
    # -------------------------
    def analyze_image(self, image_path: str, query: str = "What is in this image?") -> str:
        """Analyze image using Ollama vision model."""
        try:
            resp = ollama_client.chat(
                model=VISION_MODEL,
                messages=[{"role": "user", "content": query, "images": [image_path]}]
            )
            return resp.message.content
        except Exception as e:
            return f"Vision Error: {str(e)}"

    # -------------------------
    # MAIN QUERY PROCESSING
    # -------------------------
    def process_query(self, user_input: str, tool_feedback: str = "") -> str:

        state = get_full_system_context()

        full_query = f"""
USER REQUEST:
{user_input}

SYSTEM STATE:
{state}
"""
        if tool_feedback:
            full_query += f"\n\nTOOL FEEDBACK:\n{tool_feedback}"

        # Build memory for context
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(self.memory[-self.max_memory:])
        messages.append({"role": "user", "content": full_query})

        # Combine memory into one prompt
        combined_prompt = SYSTEM_PROMPT + "\n\nUSER QUERY:\n" + full_query

        try:
            # Call Gemini 3.1 Pro for reasoning
            content = self._call_gemini(combined_prompt)
            content = self._clean_response(content)

            # Save memory
            self.memory.append({"role": "user", "content": user_input})
            self.memory.append({"role": "assistant", "content": content})
            self._trim_memory()
            self.last_activity = time.time()

            return content

        except Exception as e:
            return f"""
PROCESS:
Brain execution failure.

PATHS:
NONE

VISION:
False

COMMANDS:
NONE

OUTPUT:
Brain error: {str(e)}
"""

    # -------------------------
    # HELPER FOR SAVE_TEXT COMMAND
    # -------------------------
    def save_text_file(self, filepath: str, content: str) -> str:
        """Save AI-generated text safely to disk."""
        try:
            filepath = os.path.expanduser(filepath)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Saved text to {filepath}"
        except Exception as e:
            return f"Failed to save text: {str(e)}"