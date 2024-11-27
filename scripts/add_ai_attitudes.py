import json
import random

# Define attitudes and their probabilities
attitudes = {
    "ai_enthusiast": 0.25,    # 25% chance
    "moderate_user": 0.35,    # 35% chance
    "reluctant_user": 0.20,   # 20% chance
    "non_user": 0.20         # 20% chance
}

# Define attitude descriptions
attitude_descriptions = {
    "ai_enthusiast": "Uses ChatGPT daily. Embraces AI tools enthusiastically. Sees significant benefits in their work.",
    "moderate_user": "Uses ChatGPT occasionally. Selective about when and how to use it. Balanced view of benefits and limitations.",
    "reluctant_user": "Rarely uses ChatGPT. Skeptical but tries it occasionally. Prefers traditional methods.",
    "non_user": "Does not use ChatGPT at all. May have ethical concerns or prefer traditional methods. Might be uninterested in or unaware of AI tools."
}

# Read the input file
with open('data/persona_tsinghua.jsonl', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Process each line
updated_lines = []
for line in lines:
    data = json.loads(line)
    
    # Randomly select an attitude based on probabilities
    attitude = random.choices(
        list(attitudes.keys()),
        weights=list(attitudes.values())
    )[0]
    
    # Concatenate the AI attitude description to the existing persona
    data['persona'] = f"{data['persona']} I am a {attitude}. {attitude_descriptions[attitude]}"
    
    # Add to updated lines
    updated_lines.append(json.dumps(data, ensure_ascii=False))

# Write back to file
with open('data/persona_tsinghua_altitudes.jsonl', 'w', encoding='utf-8') as f:
    for line in updated_lines:
        f.write(line + '\n') 