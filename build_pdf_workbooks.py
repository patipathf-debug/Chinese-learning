"""Build four handwriting-friendly HSK5 PDF workbooks from lesson sources.

Run with the bundled Python runtime: python3 build_pdf_workbooks.py
The PDFs are placed beside each lesson's HTML, so GitHub Pages can serve them.
"""
from __future__ import annotations

import html
import json
import re
import subprocess
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image

from pdf_workbook_content import LESSONS


ROOT = Path(__file__).resolve().parent
FONT_PATH = Path('/Library/Fonts/Arial Unicode.ttf')
FONT = 'StudyArialUnicode'
pdfmetrics.registerFont(TTFont(FONT, str(FONT_PATH)))
W, H = A4
M = 44
CONTENT = W - 2 * M
BG = HexColor('#F9F6F0')
INK = HexColor('#2B2929')
MUTED = HexColor('#6A625D')
ACCENT = HexColor('#8E5D49')
SOFT = HexColor('#EEDFD4')
LINE = HexColor('#D5CBC1')
PAPER = HexColor('#FFFEFB')


def source_data(n: int) -> dict:
    base = ROOT / f'HSK5_{n}'
    if n != 1:
        return json.loads((base / 'lesson_data.json').read_text(encoding='utf-8'))
    # The first chapter predates lesson_data.json. Read the same arrays used by
    # the working HTML instead of maintaining a second copy of its vocabulary.
    script = r'''
const fs=require('fs'), vm=require('vm');
const s=fs.readFileSync(process.argv[1],'utf8'), out={};
for(const key of ['words','chapterImages','chapters','chapterPinyin','questions','usageNotes']) {
  const end=key==='usageNotes' ? '(\\{.*?^    \\})' : '(\\[.*?^    \\])';
  const m=s.match(new RegExp('    const '+key+'='+end+';','ms'));
  if(!m) throw new Error('Missing '+key);
  out[key]=vm.runInNewContext('('+m[1]+')');
}
console.log(JSON.stringify(out));
'''
    p = subprocess.run(
        ['node', '-e', script, str(base / 'HSK5_1.html')],
        check=True, capture_output=True, text=True,
    )
    raw = json.loads(p.stdout)
    chapters = raw['chapters']
    for word in raw['words']:
        word['use'] = raw['usageNotes'].get(word['h'], '')
    if len(chapters) != len(raw['chapterPinyin']):
        raise ValueError('Chapter and pinyin counts differ')
    for chapter, pinyin in zip(chapters, raw['chapterPinyin']):
        chapter['py'] = pinyin
    return {
        'words': raw['words'], 'chapters': chapters,
        'images': raw['chapterImages'], 'questions': raw['questions'],
    }


def clean(text: str) -> str:
    return html.unescape(re.sub(r'<[^>]+>', '', str(text)))


def wrap(text: str, max_width: float, size: float) -> list[str]:
    lines: list[str] = []
    for paragraph in str(text).split('\n'):
        if not paragraph.strip():
            lines.append('')
            continue
        current = ''
        for piece in re.findall(r'\S+\s*', paragraph):
            candidate = current + piece
            if pdfmetrics.stringWidth(candidate.rstrip(), FONT, size) <= max_width:
                current = candidate
                continue
            if current:
                lines.append(current.rstrip())
                current = ''
            if pdfmetrics.stringWidth(piece.rstrip(), FONT, size) <= max_width:
                current = piece
            else:
                # Long Chinese and Thai runs have no spaces. Keep glyphs on the
                # page by wrapping them at character boundaries as needed.
                for char in piece:
                    if pdfmetrics.stringWidth(current + char, FONT, size) > max_width and current:
                        lines.append(current.rstrip())
                        current = ''
                    current += char
        if current:
            lines.append(current.rstrip())
    return lines


class Workbook:
    def __init__(self, n: int, data: dict):
        self.n = n
        self.data = data
        self.info = LESSONS[n]
        self.path = ROOT / f'HSK5_{n}' / f'HSK5_{n}_workbook.pdf'
        self.c = canvas.Canvas(str(self.path), pagesize=A4, pageCompression=1)
        self.c.setTitle(f'HSK5 {n} - {self.info["title"]} - iPad writing workbook')
        self.c.setAuthor('SuperChinese Study Workbooks')
        self.page = 0

    def page_start(self, section: str, kicker: str = '') -> None:
        if self.page:
            self.c.showPage()
        self.page += 1
        c = self.c
        c.setFillColor(BG)
        c.rect(0, 0, W, H, fill=1, stroke=0)
        c.setFillColor(ACCENT)
        c.rect(0, H - 13, W, 13, fill=1, stroke=0)
        c.setFont(FONT, 9)
        c.setFillColor(MUTED)
        c.drawString(M, H - 35, f'SUPERCHINESE  /  HSK5 · {self.n:02d}')
        c.drawRightString(W - M, H - 35, kicker.upper() if kicker else 'WRITE · READ · REMEMBER')
        c.setStrokeColor(LINE)
        c.line(M, H - 45, W - M, H - 45)
        c.setFillColor(INK)
        c.setFont(FONT, 23)
        c.drawString(M, H - 82, section)
        c.setStrokeColor(LINE)
        c.line(M, 49, W - M, 49)
        c.setFont(FONT, 8.5)
        c.setFillColor(MUTED)
        c.drawString(M, 34, f'{self.info["title"]}  ·  สมุดฝึกเขียน HSK5 บทที่ {self.n}')
        c.drawRightString(W - M, 34, f'{self.page:02d}')

    def text(self, value: str, x: float, y: float, maxw: float,
             size: float = 11, leading: float | None = None,
             color=INK) -> float:
        leading = leading or size * 1.55
        self.c.setFont(FONT, size)
        self.c.setFillColor(color)
        for line in wrap(value, maxw, size):
            self.c.drawString(x, y, line)
            y -= leading
        return y

    def label(self, value: str, x: float, y: float, size: float = 9) -> None:
        self.c.setFillColor(ACCENT)
        self.c.setFont(FONT, size)
        self.c.drawString(x, y, value)

    def write_lines(self, x: float, top: float, width: float, count: int,
                    gap: float = 29) -> float:
        self.c.setStrokeColor(LINE)
        self.c.setLineWidth(.7)
        for i in range(count):
            yy = top - i * gap
            self.c.line(x, yy, x + width, yy)
        return top - count * gap

    def image(self, path: Path, x: float, y: float, width: float,
              height: float) -> None:
        self.c.setFillColor(SOFT)
        self.c.roundRect(x, y, width, height, 12, fill=1, stroke=0)
        # The source art stays untouched. A 1100 px PDF copy is sharp at A4
        # reading size and makes the iPad download much smaller.
        cache = ROOT / 'tmp' / 'pdfs' / 'embed'
        cache.mkdir(parents=True, exist_ok=True)
        embedded = cache / f'lesson-{self.n}-{path.name}'
        if not embedded.exists() or embedded.stat().st_mtime < path.stat().st_mtime:
            with Image.open(path) as original:
                photo = original.convert('RGB')
                photo.thumbnail((1100, 700), Image.Resampling.LANCZOS)
                photo.save(embedded, format='JPEG', quality=75, optimize=True)
        img = ImageReader(str(embedded))
        iw, ih = img.getSize()
        scale = min(width / iw, height / ih)
        dw, dh = iw * scale, ih * scale
        self.c.drawImage(str(embedded), x + (width - dw) / 2, y + (height - dh) / 2,
                         width=dw, height=dh, mask='auto')

    def cover(self) -> None:
        self.page_start('เรียน • อ่าน • เขียน', 'iPad study workbook')
        c = self.c
        c.setFillColor(ACCENT)
        c.setFont(FONT, 10)
        c.drawString(M, 716, f'HSK5  /  CHAPTER {self.n:02d}')
        c.setFillColor(INK)
        c.setFont(FONT, 35)
        c.drawString(M, 675, self.info['title'])
        self.text(self.info['thai'], M, 648, CONTENT, 15, 20, ACCENT)
        self.text(self.info['focus'], M, 616, CONTENT, 11, 17, MUTED)
        image = ROOT / f'HSK5_{self.n}' / self.data['images'][0]['src']
        self.image(image, M, 305, CONTENT, 280)
        self.label('ในเล่มนี้', M, 281)
        items = [
            f'{len(self.data["words"])} คำศัพท์ + พินอิน + ความหมาย + ทริค',
            'เรื่องอ่าน 3 ตอนพร้อมภาพและพื้นที่จด',
            'แกรมม่า 3 จุด · ตัวอย่าง · แต่งประโยค',
            'แบบฝึกหัด 10 ข้อ + เฉลยท้ายเล่ม',
        ]
        for i, item in enumerate(items):
            c.setFillColor(ACCENT)
            c.circle(M + 4, 257 - i * 25, 2.5, fill=1, stroke=0)
            self.text(item, M + 17, 253 - i * 25, CONTENT - 17, 10.5, 15)
        self.label('ชื่อผู้เรียน', M, 131)
        self.write_lines(M + 74, 128, 225, 1)
        self.label('วันที่', 385, 131)
        self.write_lines(418, 128, 130, 1)
        self.text('เคล็ดลับ: อ่านจีนเองก่อนเปิดคำแปลในเว็บ แล้วจดคำที่ยังติดขัดลงในเล่มนี้',
                  M, 95, CONTENT, 9.5, 14, MUTED)

    def vocabulary(self) -> None:
        words = self.data['words']
        for offset in range(0, len(words), 4):
            self.page_start('คำศัพท์ใหม่', f'vocabulary  {offset + 1}-{min(len(words), offset + 4)} / {len(words)}')
            self.text('อ่านคำและตัวอย่าง แล้วเขียนความจำหรือประโยคของตัวเองบนเส้นว่าง',
                      M, 730, CONTENT, 10, 15, MUTED)
            for i, word in enumerate(words[offset:offset + 4]):
                top = 706 - i * 155
                self.c.setFillColor(PAPER)
                self.c.setStrokeColor(LINE)
                self.c.roundRect(M, top - 149, CONTENT, 146, 10, fill=1, stroke=1)
                self.c.setFillColor(ACCENT)
                self.c.setFont(FONT, 9)
                self.c.drawString(M + 12, top - 20, f'{offset + i + 1:02d}')
                self.c.setFillColor(INK)
                self.c.setFont(FONT, 23)
                self.c.drawString(M + 37, top - 30, word['h'])
                self.text(word['p'], M + 142, top - 19, CONTENT - 157, 10, 14, ACCENT)
                self.text(word['m'], M + 142, top - 39, CONTENT - 157, 10, 14)
                tip = word.get('use') or f'ลองจำจากประโยคตัวอย่าง: {word["ex"]}'
                self.text('ใช้เมื่อไร: ' + tip, M + 12, top - 64, CONTENT - 24, 8.5, 12, MUTED)
                self.text(word['ex'], M + 12, top - 94, CONTENT - 24, 10.5, 14, INK)
                self.c.setStrokeColor(LINE)
                self.c.line(M + 12, top - 119, W - M - 12, top - 119)
                self.c.line(M + 12, top - 139, W - M - 12, top - 139)
            remaining = len(words[offset:offset + 4])
            if remaining < 4:
                notes_y = 706 - remaining * 155 - 12
                self.label('ลองแต่งประโยคจากคำในหน้านี้ / จดคำที่ยังสับสน', M, notes_y)
                count = min(11, max(3, int((notes_y - 100) / 28)))
                self.write_lines(M, notes_y - 24, CONTENT, count, 28)

    def stories(self) -> None:
        for i, chapter in enumerate(self.data['chapters']):
            self.page_start(f'เรื่องอ่าน · ตอนที่ {i + 1}', 'story & notes')
            self.text(clean(chapter['title']), M, 728, CONTENT, 19, 25, ACCENT)
            self.text(clean(chapter.get('scene', '')), M, 697, CONTENT, 9.5, 14, MUTED)
            image = ROOT / f'HSK5_{self.n}' / self.data['images'][i]['src']
            self.image(image, M, 446, CONTENT, 225)
            self.label('อ่านภาษาจีน', M, 426)
            y = self.text(clean(chapter['cn']), M, 401, CONTENT, 13, 22)
            if y < 265:
                raise ValueError(f'Story Chinese too long for page: chapter {self.n}.{i + 1}: y={y}')
            self.label('คำแปลไทย', M, y - 5)
            y = self.text(clean(chapter['th']), M, y - 27, CONTENT, 10, 16, MUTED)
            if y < 156:
                raise ValueError(f'Story translation too long for page: chapter {self.n}.{i + 1}: y={y}')
            self.label('จดคำที่ไม่รู้ / สรุปตอนนี้', M, y - 4)
            self.write_lines(M, y - 25, CONTENT, 3, 25)

    def grammar(self) -> None:
        for i, item in enumerate(self.info['grammar']):
            self.page_start(f'แกรมม่า · จุดที่ {i + 1}', 'grammar & sentence writing')
            self.text(item['title'], M, 728, CONTENT, 19, 26, ACCENT)
            self.c.setFillColor(SOFT)
            self.c.roundRect(M, 633, CONTENT, 65, 9, fill=1, stroke=0)
            self.label('โครงสร้าง', M + 14, 676)
            self.text(item['pattern'], M + 14, 652, CONTENT - 28, 11, 16)
            self.label('วิธีใช้', M, 611)
            self.text(item['explain'], M, 588, CONTENT, 11, 17)
            self.label('ตัวอย่าง 3 ประโยค', M, 532)
            for j, (cn, th) in enumerate(item['examples']):
                top = 510 - j * 65
                self.text(cn, M + 13, top, CONTENT - 26, 12.5, 18)
                self.text(th, M + 13, top - 23, CONTENT - 26, 9.5, 15, MUTED)
                self.c.setStrokeColor(LINE)
                self.c.line(M + 13, top - 46, W - M - 13, top - 46)
            self.label('ลองเติมประโยค แล้วแต่งประโยคของตัวเอง', M, 301)
            self.text(item['prompt'], M, 274, CONTENT, 12, 18)
            self.write_lines(M, 239, CONTENT, 5, 30)

    def exercises(self) -> None:
        questions = self.data['questions']
        # Four grammar fill-in items, then six reading/vocabulary questions.
        mc = questions[:6]
        if len(mc) < 6:
            mc += self.info.get('extra_quiz', [])[:6 - len(mc)]
        assert len(mc) == 6
        items = [('fill', x) for x in self.info['fills']] + [('mc', x) for x in mc]
        assert len(items) == 10
        for page_ix in range(2):
            self.page_start('แบบฝึกหัด', f'practice  {page_ix * 5 + 1}-{page_ix * 5 + 5} / 10')
            intro = 'เติมคำลงในช่องว่าง แล้วเลือกคำตอบ' if page_ix == 0 else 'เลือกคำตอบที่ถูกต้อง และจดเหตุผลสั้น ๆ'
            self.text(intro, M, 728, CONTENT, 10.5, 16, MUTED)
            for j, (kind, obj) in enumerate(items[page_ix * 5:page_ix * 5 + 5]):
                num = page_ix * 5 + j + 1
                top = 690 - j * 126
                self.c.setFillColor(PAPER)
                self.c.setStrokeColor(LINE)
                self.c.roundRect(M, top - 111, CONTENT, 112, 9, fill=1, stroke=1)
                self.label(f'{num:02d}', M + 12, top - 23)
                if kind == 'fill':
                    question = obj[0]
                    self.text(question, M + 46, top - 22, CONTENT - 60, 11.5, 18)
                    self.c.setStrokeColor(LINE)
                    self.c.line(M + 46, top - 84, W - M - 16, top - 84)
                else:
                    self.text(obj['q'], M + 46, top - 22, CONTENT - 60, 10.5, 16)
                    opts = obj['options']
                    for k, option in enumerate(opts):
                        xx = M + 48 + (k % 2) * 230
                        yy = top - 56 - (k // 2) * 25
                        self.text(f'{chr(65+k)}. {option}', xx, yy, 215, 9.5, 13)
        self.page_start('เฉลยและทบทวน', 'answer key')
        self.text('ทำให้ครบก่อนเปิดหน้านี้ แล้วกลับไปจดว่าพลาดเพราะอะไร',
                  M, 730, CONTENT, 10.5, 16, MUTED)
        y = 694
        for k, (question, answer) in enumerate(self.info['fills'], 1):
            self.label(f'{k:02d}  {answer}', M, y, 10.5)
            y = self.text(question.replace('______', '___'), M + 28, y - 19,
                          CONTENT - 28, 9.5, 14, MUTED) - 13
        letters = 'ABCD'
        for j, obj in enumerate(mc, 5):
            ans = obj['options'][obj['a']]
            self.label(f'{j:02d}  {letters[obj["a"]]}. {ans}', M, y, 10.5)
            y = self.text(obj.get('why', ''), M + 28, y - 19,
                          CONTENT - 28, 9, 14, MUTED) - 13
        self.label('คำที่อยากกลับไปทบทวน', M, min(y - 25, 337))
        self.write_lines(M, min(y - 46, 316), CONTENT, 5, 30)

    def build(self) -> Path:
        self.cover()
        self.vocabulary()
        self.stories()
        self.grammar()
        self.exercises()
        self.c.save()
        return self.path


def main() -> None:
    import sys
    chapters = [int(sys.argv[1])] if len(sys.argv) == 2 else (1, 2, 3, 4, 5, 6)
    for n in chapters:
        path = Workbook(n, source_data(n)).build()
        print(path)


if __name__ == '__main__':
    main()
