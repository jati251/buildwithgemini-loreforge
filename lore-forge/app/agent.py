# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import random
import re
import urllib.parse
import urllib.request
import uuid

from google import genai
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.adk.tools import ToolContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.cloud import firestore, storage

from app.a2ui_prompt import A2UI_INSTRUCTION
from app.a2ui_utils import a2ui_callback
from google.genai import types

MODEL = "gemini-3.8-flash"


async def generate_memories_callback(callback_context: CallbackContext):
    await callback_context.add_session_to_memory()
    return None


# Hardcoded Project ID string for Firestore client (required on Agent Platform)
PROJECT_ID = "qwiklabs-gcp-04-0f9a780981ba"
db = firestore.Client(project=PROJECT_ID)

# Hardcoded Cloud Storage bucket for LoreForge public assets
BUCKET_NAME = "loreforge-assets-0f9a780981ba"


def roll_dice(expression: str) -> str:
    """Roll virtual tabletop dice given a dice expression like '2d6+3', '1d20', or 'd10-1'.

    Args:
        expression: Standard dice notation string (e.g. '2d6+3', '1d20-1', 'd20', '3d8').

    Returns:
        A string describing individual die rolls, modifier, and the total result.
    """
    expr = expression.lower().replace(" ", "")
    match = re.fullmatch(r"(\d*)d(\d+)([\+\-]\d+)?", expr)
    if not match:
        return f"Invalid dice expression '{expression}'. Please use format like '1d20+5', '2d6', or 'd8-1'."

    count_str, sides_str, modifier_str = match.groups()
    count = int(count_str) if count_str else 1
    sides = int(sides_str)
    modifier = int(modifier_str) if modifier_str else 0

    if count < 1 or count > 100 or sides < 1 or sides > 1000:
        return "Dice count must be between 1 and 100, and sides between 1 and 1000."

    rolls = [random.randint(1, sides) for _ in range(count)]
    total = sum(rolls) + modifier

    mod_str = f" {modifier_str}" if modifier_str else ""
    return f"Rolled {expression}: {rolls}{mod_str} = Total {total}"


def lookup_spell_or_item(query: str = "") -> str:
    """Look up spells or items from the LoreForge catalog database in Firestore.

    Args:
        query: The name, type, or keyword to search for (e.g., 'fireball', 'weapon', 'sword').
               If empty, lists all available catalog items.

    Returns:
        A formatted string describing the matching items.
    """
    try:
        items_ref = db.collection("spells_and_items")
        docs = items_ref.stream()
        results = []
        q = query.lower().strip()
        for doc in docs:
            data = doc.to_dict()
            name = data.get("name", "")
            item_type = data.get("type", "")
            desc = data.get("description", "")
            if not q or q in name.lower() or q in item_type.lower() or q in desc.lower():
                results.append(data)
        if not results:
            return f"No spells or items found matching query '{query}'."

        lines = []
        for item in results:
            lines.append(
                f"- **{item.get('name')}** ({item.get('type')}, {item.get('level_or_rarity')}): "
                f"{item.get('description')} [Effect/Damage: {item.get('damage_or_effect', 'N/A')}, "
                f"Weight: {item.get('weight_lbs', 0.0)} lbs]"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"Error retrieving items from Firestore: {e}"


def add_or_update_item(
    name: str,
    item_type: str,
    level_or_rarity: str,
    description: str,
    damage_or_effect: str = "N/A",
    weight_lbs: float = 0.0,
) -> str:
    """Add a new spell or item to the catalog in Firestore or update an existing one.

    Args:
        name: Name of the spell or item (e.g. 'Ring of Protection').
        item_type: Type of item (e.g. 'spell', 'weapon', 'armor', 'wondrous item').
        level_or_rarity: Spell level or item rarity (e.g. '2nd-level Abjuration', 'Rare').
        description: Detailed lore or description of the item.
        damage_or_effect: Game effect or damage roll (e.g. '+1 AC', '3d6 cold').
        weight_lbs: Weight in pounds.

    Returns:
        Confirmation message.
    """
    try:
        doc_id = name.lower().replace(" ", "-").replace("'", "")
        item_data = {
            "id": doc_id,
            "name": name,
            "type": item_type,
            "level_or_rarity": level_or_rarity,
            "description": description,
            "damage_or_effect": damage_or_effect,
            "weight_lbs": weight_lbs,
        }
        db.collection("spells_and_items").document(doc_id).set(item_data)
        return f"Successfully saved '{name}' ({item_type}) to Firestore with ID '{doc_id}'."
    except Exception as e:
        return f"Error saving item to Firestore: {e}"


def get_character(name: str) -> str:
    """Retrieve character details and inventory from Firestore.

    Args:
        name: Name or partial name of the character (e.g. 'Valerius', 'Lyra').

    Returns:
        Formatted character summary including stats and inventory.
    """
    try:
        chars_ref = db.collection("characters")
        docs = chars_ref.stream()
        q = name.lower().strip()
        matched = []
        for doc in docs:
            data = doc.to_dict()
            c_name = data.get("name", "").lower()
            if q in c_name or q in doc.id.lower():
                matched.append(data)
        if not matched:
            return f"No character found matching '{name}'."

        lines = []
        for c in matched:
            inv = ", ".join(c.get("inventory", [])) or "None"
            stats = c.get("stats", {})
            stats_str = ", ".join(f"{k.capitalize()}: {v}" for k, v in stats.items())
            lines.append(
                f"**Character: {c.get('name')}** (Level {c.get('level')} {c.get('race')} {c.get('character_class')})\n"
                f"- Backstory: {c.get('backstory')}\n"
                f"- Stats: {stats_str}\n"
                f"- Inventory: {inv}"
            )
        return "\n\n".join(lines)
    except Exception as e:
        return f"Error retrieving character from Firestore: {e}"


def update_character_inventory(
    character_name: str, item_name: str, action: str = "add"
) -> str:
    """Add or remove an item in a character's inventory stored in Firestore.

    Args:
        character_name: The name or ID of the character (e.g., 'Valerius Sunblade').
        item_name: The name of the item to add or remove.
        action: Either 'add' or 'remove'.

    Returns:
        Confirmation message with updated inventory.
    """
    try:
        chars_ref = db.collection("characters")
        docs = list(chars_ref.stream())
        target_doc = None
        q = character_name.lower().strip()
        for doc in docs:
            if q in doc.to_dict().get("name", "").lower() or q in doc.id.lower():
                target_doc = doc
                break

        if not target_doc:
            return f"Character '{character_name}' not found."

        data = target_doc.to_dict()
        inventory = data.get("inventory", [])

        if action.lower() == "add":
            if item_name not in inventory:
                inventory.append(item_name)
        elif action.lower() == "remove":
            if item_name in inventory:
                inventory.remove(item_name)
        else:
            return f"Invalid action '{action}'. Use 'add' or 'remove'."

        target_doc.reference.update({"inventory": inventory})
        return f"Updated inventory for {data.get('name')}: {', '.join(inventory)}"
    except Exception as e:
        return f"Error updating inventory in Firestore: {e}"


def lookup_dnd_monster_stats(query: str) -> str:
    """Look up official D&D 5e monster stats, challenge rating, hit points, and armor class from the public D&D 5e API.

    Args:
        query: The name or keyword of the monster to search for (e.g., 'goblin', 'adult red dragon', 'beholder').

    Returns:
        A formatted monster stat block string, or an informative error message.
    """
    if not query or not query.strip():
        return "Please provide a monster name or query."

    base_url = os.getenv("DND_API_BASE_URL", "https://www.dnd5eapi.co/api")
    api_key = os.getenv("DND_5E_API_KEY", "")

    headers = {"User-Agent": "LoreForgeAgent/1.0"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    index = query.lower().strip().replace(" ", "-")
    url = f"{base_url}/monsters/{urllib.parse.quote(index)}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception:
        search_url = f"{base_url}/monsters?name={urllib.parse.quote(query)}"
        try:
            req_search = urllib.request.Request(search_url, headers=headers)
            with urllib.request.urlopen(req_search) as resp:
                search_data = json.loads(resp.read().decode("utf-8"))
            results = search_data.get("results", [])
            if not results:
                return f"No monster found matching '{query}'."
            first_index = results[0]["index"]
            url = f"{base_url}/monsters/{urllib.parse.quote(first_index)}"
            req_first = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req_first) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return f"Error retrieving monster data for '{query}': {e}"

    name = data.get("name", query)
    size = data.get("size", "Unknown")
    m_type = data.get("type", "monster")
    alignment = data.get("alignment", "unaligned")
    cr = data.get("challenge_rating", "N/A")
    hp = data.get("hit_points", "N/A")
    hp_formula = data.get("hit_points_roll", "")

    ac_list = data.get("armor_class", [])
    if isinstance(ac_list, list) and ac_list:
        ac = ac_list[0].get("value", "N/A")
    else:
        ac = "N/A"

    stats = (
        f"STR: {data.get('strength', '-')} | DEX: {data.get('dexterity', '-')} | "
        f"CON: {data.get('constitution', '-')} | INT: {data.get('intelligence', '-')} | "
        f"WIS: {data.get('wisdom', '-')} | CHA: {data.get('charisma', '-')}"
    )

    actions = [a.get("name") for a in data.get("actions", [])[:3] if "name" in a]
    actions_str = ", ".join(actions) if actions else "None listed"

    return (
        f"**Monster Stat Block: {name}**\n"
        f"- **Type:** {size} {m_type} ({alignment})\n"
        f"- **Challenge Rating (CR):** {cr}\n"
        f"- **Hit Points (HP):** {hp} ({hp_formula})\n"
        f"- **Armor Class (AC):** {ac}\n"
        f"- **Stats:** {stats}\n"
        f"- **Notable Actions:** {actions_str}"
    )


async def generate_item_image(
    prompt: str, tool_context: ToolContext = None
) -> str:
    """Generate an image illustration for an item, character portrait, or scene in the tabletop RPG domain using Gemini image generation.

    Args:
        prompt: Detailed text description of the item, character, or scene to illustrate (e.g. 'an enchanted flaming sword', 'a dark tavern interior').
        tool_context: Context automatically injected by ADK runtime for artifact saving.

    Returns:
        The public HTTPS Cloud Storage URL of the generated image.
    """
    try:
        client = genai.Client(
            vertexai=True, project=PROJECT_ID, location="global"
        )
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio="1:1",
                    image_size="1K",
                ),
            ),
        )

        image_bytes = None
        mime_type = "image/jpeg"
        if (
            response.candidates
            and response.candidates[0].content
            and response.candidates[0].content.parts
        ):
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    image_bytes = part.inline_data.data
                    mime_type = part.inline_data.mime_type or "image/jpeg"
                    break

        if not image_bytes:
            return "Failed to generate image from model response."

        ext = ".png" if "png" in mime_type.lower() else ".jpg"
        slug = (
            re.sub(r"[^a-zA-Z0-9_-]", "_", prompt[:30]).strip("_").lower()
            or "item"
        )
        filename = f"{slug}_{uuid.uuid4().hex[:8]}{ext}"

        if tool_context:
            artifact_part = types.Part.from_bytes(
                data=image_bytes, mime_type=mime_type
            )
            await tool_context.save_artifact(
                filename=filename, artifact=artifact_part
            )

        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        return f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    except Exception as e:
        return f"Error generating image: {e}"


try:
    with open("deployment_metadata.json") as f:
        _meta = json.load(f)
        _ae_name = _meta.get("remote_agent_runtime_id")
except Exception:
    _ae_name = None

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=AgentEngineSandboxCodeExecutor(
        agent_engine_resource_name=_ae_name
    ) if _ae_name else None,
    instruction=A2UI_INSTRUCTION,
    tools=[
        roll_dice,
        lookup_spell_or_item,
        add_or_update_item,
        get_character,
        update_character_inventory,
        lookup_dnd_monster_stats,
        generate_item_image,
        PreloadMemoryTool(),
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
