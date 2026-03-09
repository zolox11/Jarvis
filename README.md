# 🤖 Jarvis – Autonomous Linux AI Agent

Jarvis is a **local AI-powered autonomous assistant for Linux** designed to execute tasks using natural language.
It combines **Google Gemini (reasoning)** with **Ollama (vision)** to interact with your system, browse the web, analyze images, and execute shell commands safely.

Jarvis runs entirely in your terminal and can:

* Execute Linux commands
* Browse and summarize web pages
* Download files
* Analyze screenshots or images
* Write reports and save them to files
* Assist with automation tasks

---

# ✨ Features

## 🧠 AI Reasoning

* Uses **Google Gemini** for intelligent reasoning and task planning.

## 👁 Computer Vision

* Uses **Ollama vision models** to analyze screenshots and images.

## 🌐 Web Interaction

Jarvis can:

* Fetch and parse webpages
* Extract information
* Summarize content

## 📁 File Management

Jarvis can:

* Create files
* Save reports
* Download resources
* Organize directories

## 🖥 System Automation

Jarvis can run safe Linux shell commands for automation.

Examples:

* File manipulation
* Process inspection
* System diagnostics
* Automation tasks

---

# 🏗 Project Structure

```
Jarvis/
│
├── main.py
├── ai.py
├── logic.py
├── requirements.txt
├── README.md
└── venv/
```

| File               | Purpose                    |
| ------------------ | -------------------------- |
| `main.py`          | Main runtime loop          |
| `ai.py`            | AI reasoning engine        |
| `logic.py`         | Tools & system interaction |
| `requirements.txt` | Python dependencies        |

---

# ⚙️ Requirements

## System Requirements

* Linux (recommended: **Arch Linux**)
* Python **3.10+**
* Internet connection
* Ollama installed

### Install required Linux tools

Arch Linux:

```
sudo pacman -S grim imagemagick wl-clipboard slurp
```

---

# 🐍 Python Setup

## 1️⃣ Clone or download the project

```
git clone <repo>
cd Jarvis
```

---

## 2️⃣ Create Python Virtual Environment

```
python -m venv venv
```

Activate it:

```
source venv/bin/activate
```

Your terminal should show:

```
(venv)
```

---

## 3️⃣ Install Python Dependencies

```
pip install -r requirements.txt
```

---

# 🔑 Gemini API Key Setup

Jarvis requires a **Google Gemini API key**.

Get one from:

https://ai.google.dev/

---

## Set API Key (Temporary)

```
export GOOGLE_API_KEY="YOUR_API_KEY_HERE"
```

---

## Set API Key (Permanent)

Add to your shell config:

### Bash

```
nano ~/.bashrc
```

Add:

```
export GOOGLE_API_KEY="YOUR_API_KEY_HERE"
```

Reload shell:

```
source ~/.bashrc
```

---

# 🧠 Ollama Setup (Vision)

Install Ollama:

https://ollama.com/download

Start the service:

```
ollama serve
```

Pull the vision model:

```
ollama pull llava:7b
```

---

# 🚀 Running Jarvis

Start the assistant:

```
python main.py
```

Example prompt:

```
[Jarvis] >
```

Exit with:

```
exit
```

or

```
quit
```

---

# 💬 Example Commands

## Web Research

```
Write a summary of https://en.wikipedia.org/wiki/Linux
```

---

## Save a Report

```
Write a report on Spain and save it to ~/Pictures/Cells/spain.txt
```

---

## Download Files

```
Download this file:
https://example.com/file.pdf
```

---

## Analyze Images

```
Analyze this image:
~/Pictures/photo.png
```

---

## Screen Inspection

```
What is currently on my screen?
```

Jarvis will:

1. Capture a screenshot
2. Send it to the vision model
3. Describe the screen

---

# ⚙️ Supported AI Commands

Jarvis internally uses special commands:

| Command                      | Description           |
| ---------------------------- | --------------------- |
| `FETCH_WEB <url>`            | Retrieve webpage text |
| `DOWNLOAD <url> <file>`      | Download a file       |
| `ANALYZE_IMG <path>`         | Analyze an image      |
| `SAVE_TEXT <path> <content>` | Save generated text   |

Users **do not need to type these manually**.

Jarvis generates them automatically.

---

# 🧩 How Jarvis Works

1. User sends request
2. Gemini AI plans actions
3. Jarvis executes commands
4. Tool outputs return to AI
5. AI refines the result
6. Final response is printed

This creates an **autonomous reasoning loop**.

---

# 🔒 Safety Rules

Jarvis enforces:

* No multi-command chaining
* No shell logic (`&&`, `||`, `;`)
* One command per execution
* Output validation

This prevents dangerous automation.

---

# 🧪 Troubleshooting

## "No module named google"

Install dependencies:

```
pip install google-genai
```

---

## "No API key provided"

Set your API key:

```
export GOOGLE_API_KEY="your_key"
```

---

## Ollama not responding

Start Ollama:

```
ollama serve
```

---

## Vision not working

Ensure the model exists:

```
ollama pull llava:7b
```

---

# 📈 Future Improvements

Planned features:

* Memory persistence
* File indexing
* Voice control
* GUI dashboard
* Multi-agent reasoning
* Local LLM fallback

---

# 🤝 Contributing

Pull requests are welcome.

Ideas for contributions:

* New automation tools
* Improved web scraping
* Additional vision models
* Security improvements

---

# 📜 License

MIT License

---

# 👤 Author

Jarvis Linux AI Agent
Built for advanced autonomous Linux interaction.

---
