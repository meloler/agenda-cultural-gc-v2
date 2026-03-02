import re

def n(t):
    t = str(t).strip()
    # Match specific city/island phrases optionally preceded by 'en' and separated by [-|,/]
    pattern = r'(?i)\s*[-|/,]*\s*(?:en\s+)?(?:las palmas de gran canaria|las palmas|gran canaria|islas canarias|canarias|telde|infecar)\b\s*$'
    t = re.sub(pattern, '', t)
    # clean trailing punctuation
    t = re.sub(r'(?i)\s+[-|/,]\s*$', '', t)
    return t.strip()

tests = [
    "Concierto Rock en Gran Canaria",
    "Festival | Las Palmas de Gran Canaria",
    "Música - Telde",
    "Los Coquillos",
    "El lago de los cisnes en Las Palmas"
]

for t in tests:
    print(f"'{t}' -> '{n(t)}'")
