import os
import re
from loguru import logger

from ai import JarvisBrain
from logic import (
    fetch_web_content,
    download_resource,
    analyze_image_with_vision,
    execute_shell,
    capture_screen
)


def main():
    jarvis = JarvisBrain()
    print(f"--- JARVIS V5.3 ONLINE ---")

    while True:
        try:
            prompt = f"[{os.path.basename(os.getcwd())}] > "
            user_input = input(prompt)

            if user_input.lower() in ["exit", "quit", "bye"]:
                print("Shutting down Jarvis.")
                break

            # Step 1: initial query to AI
            current_response = jarvis.process_query(user_input)

            # Allow up to 3 self-correction/tool use turns
            for turn in range(3):

                # Extract COMMANDS block safely
                cmds_block = re.search(
                    r"COMMANDS:\s*\n(.*?)\n\s*OUTPUT:",
                    current_response,
                    re.DOTALL | re.IGNORECASE
                )

                # Detect if vision is requested
                vision_flag = re.search(
                    r"VISION:\s*(True|False)",
                    current_response,
                    re.IGNORECASE
                )

                results_buffer = []

                if cmds_block:
                    commands = [c.strip() for c in cmds_block.group(1).splitlines()]

                    for cmd in commands:
                        if not cmd or cmd.upper() == "NONE":
                            continue

                        # --- Special AI tool commands ---
                        if cmd.startswith("FETCH_WEB "):
                            url = cmd.replace("FETCH_WEB ", "").strip()
                            print(f"[*] Browsing: {url}")
                            results_buffer.append(fetch_web_content(url))

                        elif cmd.startswith("DOWNLOAD "):
                            parts = cmd.split(" ", 2)
                            if len(parts) >= 3:
                                print(f"[*] Downloading: {parts[1]}")
                                results_buffer.append(
                                    download_resource(parts[1], parts[2])
                                )

                        elif cmd.startswith("ANALYZE_IMG "):
                            path = cmd.replace("ANALYZE_IMG ", "").strip()
                            print(f"[*] Analyzing image: {path}")
                            results_buffer.append(
                                analyze_image_with_vision(path)
                            )

                        elif cmd.startswith("SAVE_TEXT "):
                            # SAVE_TEXT <filepath> <content>
                            parts = cmd.split(" ", 2)
                            if len(parts) >= 3:
                                filepath = os.path.expanduser(parts[1])
                                content = parts[2]
                                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                                with open(filepath, "w", encoding="utf-8") as f:
                                    f.write(content)
                                results_buffer.append(f"Saved text to {filepath}")
                                print(f"[*] Saved text to {filepath}")

                        # --- fallback to shell command ---
                        else:
                            res = execute_shell(cmd)
                            if res:
                                short_res = res[:200] + ("..." if len(res) > 200 else "")
                                print(f"  └ {short_res}")
                                results_buffer.append(f"CMD '{cmd}' OUTPUT: {res}")

                # Handle vision request
                if vision_flag and vision_flag.group(1).lower() == "true":
                    print("[*] Inspecting desktop screen...")
                    scr = capture_screen()
                    if scr:
                        results_buffer.append(
                            analyze_image_with_vision(scr, "Describe the user's current screen.")
                        )

                # Feed results back into AI
                if results_buffer:
                    tool_feedback_text = "\n".join(results_buffer)
                    current_response = jarvis.process_query(user_input, tool_feedback=tool_feedback_text)
                else:
                    break  # nothing more to process

            # Extract OUTPUT section safely
            final_output = re.search(
                r"OUTPUT:\s*(.*)",
                current_response,
                re.DOTALL | re.IGNORECASE
            )

            if final_output:
                output_text = final_output.group(1).strip()
            else:
                output_text = current_response.strip()

            # Limit output length for readability
            max_len = 1500
            if len(output_text) > max_len:
                output_text = output_text[:max_len] + " ...[truncated]"

            print(f"\nJarvis: {output_text}\n")

        except KeyboardInterrupt:
            print("\nShutting down Jarvis.")
            break

        except Exception as e:
            logger.error(f"Global Loop Error: {e}")


if __name__ == "__main__":
    main()