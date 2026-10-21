"""Seed script to populate Firestore database for LoreForge."""

from google.cloud import firestore

# Hardcoded Project ID string (DO NOT use os.getenv("GOOGLE_CLOUD_PROJECT") or google.auth.default())
PROJECT_ID = "qwiklabs-gcp-04-0f9a780981ba"

db = firestore.Client(project=PROJECT_ID)

ITEMS = [
    {
        "id": "fireball",
        "name": "Fireball",
        "type": "spell",
        "level_or_rarity": "3rd-level Evocation",
        "description": "A bright streak flashes from your pointing finger to a point you choose and then blossoms with a low roar into an explosion of flame.",
        "damage_or_effect": "8d6 fire damage (DC 15 Dex save for half)",
        "weight_lbs": 0.0,
    },
    {
        "id": "healing-word",
        "name": "Healing Word",
        "type": "spell",
        "level_or_rarity": "1st-level Evocation",
        "description": "A creature of your choice that you can see within range regains hit points equal to 1d4 + your spellcasting ability modifier.",
        "damage_or_effect": "1d4 + spellcasting modifier healing",
        "weight_lbs": 0.0,
    },
    {
        "id": "longsword-plus-one",
        "name": "Longsword +1",
        "type": "weapon",
        "level_or_rarity": "Uncommon",
        "description": "A finely crafted martial blade etched with draconic runes. You gain a +1 bonus to attack and damage rolls made with this weapon.",
        "damage_or_effect": "1d8 + 1 slashing damage (versatile 1d10 + 1)",
        "weight_lbs": 3.0,
    },
    {
        "id": "shield-of-faith",
        "name": "Shield of Faith",
        "type": "spell",
        "level_or_rarity": "1st-level Abjuration",
        "description": "A shimmering field appears and surrounds a creature of your choice within range, granting it a +2 bonus to AC for the duration.",
        "damage_or_effect": "+2 bonus to AC",
        "weight_lbs": 0.0,
    },
    {
        "id": "bag-of-holding",
        "name": "Bag of Holding",
        "type": "wondrous item",
        "level_or_rarity": "Uncommon",
        "description": "This bag has an interior space considerably larger than its outside dimensions. It can hold up to 500 pounds.",
        "damage_or_effect": "Dimensional storage up to 500 lbs / 64 cu. ft.",
        "weight_lbs": 15.0,
    },
]

CHARACTERS = [
    {
        "id": "valerius-sunblade",
        "name": "Valerius Sunblade",
        "character_class": "Paladin",
        "race": "High Elf",
        "level": 4,
        "stats": {
            "strength": 16,
            "dexterity": 10,
            "constitution": 14,
            "intelligence": 10,
            "wisdom": 12,
            "charisma": 15,
        },
        "inventory": ["Longsword +1", "Chain Mail", "Bag of Holding", "Potion of Healing"],
        "backstory": "A noble knight sworn to the Order of the Radiant Sun, seeking ancient relics lost in dark dungeons.",
    },
    {
        "id": "lyra-shadowwhisper",
        "name": "Lyra Shadowwhisper",
        "character_class": "Rogue",
        "race": "Tiefling",
        "level": 3,
        "stats": {
            "strength": 10,
            "dexterity": 17,
            "constitution": 12,
            "intelligence": 14,
            "wisdom": 10,
            "charisma": 14,
        },
        "inventory": ["Shortsword", "Thieves' Tools", "Parchment & Ink", "Potion of Invisibility"],
        "backstory": "A former guild burglar turned mercenary scholar who deciphers ancient ruins for profit and knowledge.",
    },
]


def seed():
    print(f"Seeding Firestore in project '{PROJECT_ID}'...")
    
    items_ref = db.collection("spells_and_items")
    for item in ITEMS:
        doc_id = item["id"]
        items_ref.document(doc_id).set(item)
        print(f"  - Seeded item: {item['name']} ({doc_id})")

    chars_ref = db.collection("characters")
    for char in CHARACTERS:
        doc_id = char["id"]
        chars_ref.document(doc_id).set(char)
        print(f"  - Seeded character: {char['name']} ({doc_id})")

    print("Firestore seeding complete! ✅")


if __name__ == "__main__":
    seed()
