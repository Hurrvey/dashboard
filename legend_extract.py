import re
from pathlib import Path
text = Path('node_modules/chart.xkcd/dist/index.js').read_text(encoding='utf-8')
idx = text.find('Legend(')
print(idx)
if idx != -1:
    print(text[idx-200:idx+400])
