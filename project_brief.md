# My agent: LoreForge

**Background & Backstory:**
In the bustling taverns and torchlit archives of the realm, adventurers and Dungeon Masters often wrestle with scattered character sheets, lost spell scrolls, complex rule checks, and forgotten backstories. LoreForge was conceived as an arcane companion—a sentient grimoire imbued with reasoning—that journeys alongside tabletop RPG players. Whether forging a fledgling hero from an ember of backstory, tracking enchanted inventory and spellbooks, rendering vivid character portraits, or computing tactical combat odds in the heat of battle, LoreForge bridges imaginative roleplay with tabletop mechanics so players can immerse themselves in their adventures.

One-liner: A conversational agent that helps tabletop RPG players build characters, manage equipment & spellbooks, look up rules, and visualize heroes and scenes with a catalog of spells, equipment, and character sheets.

Tool coverage:
- Memory: Remembers player character details (Name, Class, Level, Backstory) and playstyle preferences across sessions.
- Tools: `lookup_spell_or_item` (searches rules/items), `roll_dice` (executes dice rolls e.g. `2d6+3`), `update_inventory` (modifies equipment list).
- Catalog/UI: Equipment inventory tables, spellbook cards, and character summary cards formatted via A2UI.
- Image gen: Generates custom character portraits, item illustrations, and scene concepts using Gemini image generation.
- Sandbox: Calculates point-buy stat validation, encounter challenge rating metrics, and dice probability distributions using Python code execution.

Recommended for every project: memory, storage, tools, image generation, A2UI
Agent-specific / stretch (pick what fits): Code sandbox for combat & stat calculations, Vertex AI Memory Bank for long-term character persistence.
