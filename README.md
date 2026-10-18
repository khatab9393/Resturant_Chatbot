# Quick Bite: Restaurant Menu Chatbot

A simple, ChatGPT-style chatbot for restaurants that answers customer questions about the menu: dishes, prices, spicy and vegetarian options, and allergens. It runs locally with [Ollama](https://ollama.com) and Qwen, and can optionally use the Claude API instead. No frameworks, no `pip install`: just Python.

## Features

- Clean white chat interface with a centered input bar and quick-question buttons
- Streaming replies (text appears as it is generated)
- Answers only from your own menu, so it won't invent dishes or prices
- Menu stored in SQLite (editable with any SQLite viewer) with a JSON fallback
- Allergen, vegetarian, vegan and spicy information per dish
- Runs fully offline and free with Ollama + Qwen, or with the Claude API
- Replies in the customer's language

## How it works

```
Browser (index.html)  ->  server.py  ->  Ollama (Qwen)
```

The server loads the menu from the database, adds it to the model's instructions together with a few rules, and streams the model's answer back to the browser. The conversation history is sent with every request.

## Requirements

- Python 3.8+
- [Ollama](https://ollama.com) with a Qwen model (or a Claude API key)

## Quick start (Ollama + Qwen)

```bash
# 1. Download a model once
ollama pull qwen2.5:3b        # use qwen2.5:7b if you have 8 GB+ RAM

# 2. Create the sample menu database
python setup_db.py

# 3. Start the bot
python server.py              # default model is qwen2.5:7b
```

To use a different model, set `MODEL` first:

```bash
# Windows
set MODEL=qwen2.5:3b
# macOS / Linux
export MODEL=qwen2.5:3b
```

Open <http://localhost:8000>. Ollama must be running in the background.

## Using the Claude API instead

```bash
export ANTHROPIC_API_KEY="your-key"     # Windows: set ANTHROPIC_API_KEY=your-key
python server_api.py
```

Keep your API key on the server only. Never put it in `index.html` or commit it to Git.

## Customize

| What | Where |
|---|---|
| Menu, prices, allergens | `menu.db` (open with [DB Browser for SQLite](https://sqlitebrowser.org)), or edit `setup_db.py` and recreate the database |
| Restaurant name, welcome message, quick questions | the config block at the top of the `<script>` in `index.html` |
| Colors | `--accent` and `--accent2` at the top of the `<style>` in `index.html` |
| Bot personality and rules | `build_system_prompt()` in `server.py` |
| Another database file | `DB_FILE=menu_fastfood.db python server.py` |

`setup_fastfood_db.py` creates a second sample menu (burgers, chicken, fries and more).

## Project structure

```
index.html              Chat interface
server.py               Web server + Ollama connection
server_api.py           Same server using the Claude API
menu.json               Fallback menu (used if no database exists)
setup_db.py             Creates menu.db (sample fast-food menu)
setup_fastfood_db.py    Creates menu_fastfood.db (second sample menu)
```

## Troubleshooting

- **HTTP 500 / "Error talking to Ollama":** check the model is downloaded (`ollama list`) and that the model name matches `MODEL`.
- **Asked to download the model again:** the default model name (`qwen2.5:7b`) probably differs from the one you downloaded. Change the default in `server.py` or set `MODEL`.
- **Windows: "untrusted mount point" error:** move Ollama's model folder to a plain path, for example `setx OLLAMA_MODELS "C:\ollama-models"`, then restart Ollama.

## Disclaimer

The bot answers from your menu data, but small language models can make mistakes. Always have staff confirm allergen information.

## License

Add your license here (for example MIT).
