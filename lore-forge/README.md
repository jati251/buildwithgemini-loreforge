# LoreForge

LoreForge is a conversational agent that helps tabletop RPG players build characters, manage equipment & spellbooks, look up rules, and visualize heroes and scenes with a catalog of spells, equipment, and character sheets.

## Features

- **Memory Bank**: Remembers player character details (Name, Class, Level, Backstory) and playstyle preferences across sessions using Vertex AI Memory Bank.
- **Rule & Catalog Lookup**: Look up spells, items, and rules using a database powered by **Firestore**.
- **Inventory Management**: Add or remove items from a character's inventory directly in Firestore.
- **Monster Stat Lookup**: Retrieve official D&D 5e monster stats via the public D&D 5e API.
- **Virtual Dice Rolling**: Roll tabletop dice directly through the agent (e.g. `2d6+3`).
- **Rich UI Cards**: Renders equipment tables, spellbook cards, and character summaries using **A2UI**.
- **Image Generation**: Generates custom character portraits, item illustrations, and scenes using `gemini-3.1-flash-lite-image` and uploads them to **Cloud Storage**.
- **Sandbox Code Execution**: Calculates point-buy stat validation, encounter challenge ratings, and dice probabilities securely using the Python **Code Sandbox**.

*(Note: Features are strictly based on the current implementation in the `app` directory.)*

## Setup and Run Locally

Ensure you have your environment set up and the necessary Google Cloud permissions.

### 1. Install Dependencies

Using `agents-cli`:

```bash
uvx google-agents-cli setup
agents-cli install
```

### 2. Run the Agent (Local CLI / Web UI)

To test the agent with a local web server (with auto-reload):

```bash
agents-cli playground
```

Or using ADK CLI directly:

```bash
uv run adk web
```

### 3. Run the Custom Frontend

If you want to use the custom frontend interface:

```bash
cd frontend
# Create and activate a virtual environment if needed
python -m venv .venv
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run the proxy server
python main.py
```
