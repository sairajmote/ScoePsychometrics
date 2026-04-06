import re

def parse_enneagram():
    with open('z:/projects/Psycho/psycho_one/enneagram_questions.txt', 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find: (number). (text) [E(type)]
    pattern = r'(\d+)\.\s+(.*?)\s+\[(E\d+)\]'
    matches = re.finditer(pattern, content)

    questions = []
    for match in matches:
        text = match.group(2).strip()
        etype = match.group(3).strip()
        questions.append((text, etype))
    
    print(f"Parsed {len(questions)} questions.")
    
    # Generate the QUESTIONS list for seed_enneagram.py
    for text, etype in questions:
        # Escape double quotes
        escaped_text = text.replace('"', '\\"')
        print(f'    ("{escaped_text}", "{etype}"),')

if __name__ == "__main__":
    parse_enneagram()
