import re
html = open('telde.html', encoding='utf-8', errors='ignore').read()
links = set(re.findall(r'https://teldecultura\.org/[^\s\"\'<]+', html))
for l in links:
    if 'wp-' not in l:
        print(l)
