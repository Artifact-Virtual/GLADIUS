import json
import re

def normalize(s: str) -> str:
    s = s.lower()
    s = re.sub(r"\[bot\]$", "", s)
    s = re.sub(r"[-_]", " ", s)
    s = " ".join(s.split())
    return s

with open('AI_AUTHORIZED.json') as f:
    data = json.load(f)

normalized = [normalize(a) for a in data['actors']]
print('Authorized (normalized):', normalized)

for actor in [
    'github-copilot[bot]',
    'github-copilot',
    'GitHub Copilot',
    'copilot',
    'robot',
    'ai',
    'unknown-bot',
]:
    print(actor, '->', normalize(actor), '->', normalize(actor) in normalized)
