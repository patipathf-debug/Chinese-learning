# -*- coding: utf-8 -*-
"""Fill the lesson's reading pinyin from the checked shared lexicon."""
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent
data_path = root / 'lesson_data.json'
data = json.loads(data_path.read_text(encoding='utf-8'))
source = (root.parent / 'reading-lexicon.js').read_text(encoding='utf-8')
lexicon = json.loads(source.removeprefix('window.READING_LEXICON=').rstrip(';\n'))
keys = sorted(lexicon, key=len, reverse=True)

for chapter in data['chapters']:
    text = re.sub(r'</?em>', '', chapter['cn'])
    parts = []
    i = 0
    while i < len(text):
        char = text[i]
        if '\u4e00' <= char <= '\u9fff':
            word = next((key for key in keys if text.startswith(key, i)), None)
            if word is None:
                raise ValueError(f'Missing pinyin for {char!r} in chapter {chapter["n"]}')
            parts.append(lexicon[word]['p'])
            i += len(word)
        else:
            if not char.isspace():
                parts.append(char)
            i += 1
    pinyin = ' '.join(parts)
    for punctuation in '，。！？；：,.!?;:、':
        pinyin = pinyin.replace(' ' + punctuation, punctuation)
    pinyin = pinyin.replace('“ ', '“').replace(' ”', '”')
    chapter['py'] = pinyin

data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Updated pinyin for', len(data['chapters']), 'chapters')
