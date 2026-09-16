from pathlib import Path
from PIL import Image, ImageOps

files = sorted(Path('tmp/pdfs').glob('go-polished-*.png'),
               key=lambda p: int(p.stem.split('-')[-1]))
for start in range(0, len(files), 6):
    pages = [Image.open(p).convert('RGB') for p in files[start:start + 6]]
    out = Image.new('RGB', (1500, 1414), 'white')
    for i, page in enumerate(pages):
        thumb = ImageOps.contain(page, (500, 707))
        out.paste(thumb, ((i % 3) * 500, (i // 3) * 707))
    out.save(f'tmp/pdfs/go-polished-contact-{start // 6 + 1}.png')
