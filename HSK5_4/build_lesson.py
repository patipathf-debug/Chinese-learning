"""Build HSK5_4.html and an Anki import file from lesson_data.json."""
from __future__ import annotations

import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent
data = json.loads((root / "lesson_data.json").read_text(encoding="utf-8"))
html = (root.parent / "HSK5_3" / "HSK5_3.html").read_text(encoding="utf-8")


def swap(old: str, new: str) -> None:
    global html
    count = html.count(old)
    if count != 1:
        raise ValueError(f"Expected one match for {old[:55]!r}; found {count}")
    html = html.replace(old, new)


def replace_array(name: str, value: object) -> None:
    global html
    replacement = "    const " + name + "=" + json.dumps(value, ensure_ascii=False, separators=(",", ":")) + ";\n"
    html, count = re.subn(r"^    const " + name + r"=.*;\n", lambda _: replacement, html, count=1, flags=re.M)
    if count != 1:
        raise ValueError(f"Could not replace {name}")


replace_array("words", data["words"])
replace_array("chapterImages", data["images"])
replace_array("chapters", [{key: value for key, value in chapter.items() if key != "py"} for chapter in data["chapters"]])
replace_array("chapterPinyin", [chapter["py"] for chapter in data["chapters"]])
replace_array("questions", data["questions"])

swap("<title>屏幕上的名字 · HSK5 บทที่ 3</title>", "<title>被删掉的名字 · HSK5 บทที่ 4</title>")
swap("เรียนศัพท์ใหม่ HSK5 บทที่ 3 ผ่านเรื่องของหลินอวี่ กดดูคำอ่านและความหมายของทุกคำในเรื่องได้", "เรียนศัพท์ใหม่ HSK5 บทที่ 4 ผ่านเรื่องต่อของหลินอวี่ กดดูคำอ่านและความหมายของทุกคำในเรื่องได้")
swap("SUPERCHINESE · HSK5/03", "SUPERCHINESE · HSK5/04")
swap('<a href="../HSK5_2/HSK5_2.html">← บทที่ 2</a>', '<a href="../HSK5_3/HSK5_3.html">← บทที่ 3</a>')
html = html.replace('<a href="../HSK5_4/HSK5_4.html">บทที่ 4 →</a>', '')
html = html.replace('<a href="../HSK5_5/HSK5_5.html">บทที่ 5 →</a>', '')
html = html.replace('<a href="../HSK5_3/HSK5_3.html">← บทที่ 3</a>', '<a href="../HSK5_3/HSK5_3.html">← บทที่ 3</a><a href="../HSK5_5/HSK5_5.html">บทที่ 5 →</a>')

hero = '''  <header class="hero" id="top"><div class="wrap"><div class="eyebrow">HSK 5 · Chapter 04 · เรื่องต่อเนื่อง</div><h1 lang="zh-CN">被删掉的名字</h1><p class="subtitle">ชื่อที่ถูกลบออก</p><p>ชื่อหลินเสวี่ยอยู่ในรายชื่อผู้ใช้ที่ถูกลบ หลินอวี่ต้องถามพี่สาวให้ชัด ข้อความนัดพบที่โกดังเก่านำทั้งสามไปเจอรถชน ตำรวจ และบันทึกที่เปลี่ยนความหมายของชื่อในรายชื่อนั้น</p><div class="hero-actions"><a class="btn primary" href="#story">เริ่มอ่านตอนที่ 1 →</a><a class="btn" href="../vocabulary-orbit.html">เล่นวงคำศัพท์รวม ↗</a></div><div class="statline"><span><b>19</b> คำใหม่จาก Excel</span><span><b>3</b> ตอนต่อเนื่อง</span><span><b>10</b> ข้อทดสอบ</span></div></div></header>'''
html, count = re.subn(r'  <header class="hero".*?</header>', lambda _: hero, html, count=1, flags=re.S)
if count != 1:
    raise ValueError("Could not replace cover")

swap("หลังเปิดเผยข้อมูลผู้ใช้ปลอม หลินอวี่กลับถูกระบุว่าเป็นผู้สร้างบัญชี เธอตามรอยเว็บไซต์รับสมัครงานและเอกสารเก่าที่อาจพิสูจน์ว่าใครอยู่เบื้องหลัง", "หลังพบชื่อพี่สาวในรายชื่อผู้ใช้ที่ถูกลบ หลินอวี่ เฉินหนิง และหลินเสวี่ยตามข้อความนัดพบไปโกดังเก่า ความจริงเรื่องผู้แจ้งเบาะแสกำลังจะปรากฏ")
swap("จำได้แล้ว 0 / 21 คำ", "จำได้แล้ว 0 / 19 คำ")
swap("คำจีน พินอิน และความหมาย 21 คำใหม่มาจาก Excel; ตัวอย่างและเรื่องอ่านจัดทำสำหรับบทนี้", "คำใหม่ 19 รายการมาจาก Excel; รายการเปรียบเทียบแยกเป็น 地方 และ 咱们 พร้อมอธิบายคู่คำและไวยากรณ์")

notes = '''    <section class="section alt" id="notes"><div class="wrap"><div class="section-head"><div><div class="tagline">Language notes</div><h2>คำคู่และโครงสร้างในสมุด</h2></div></div><div class="note-list"><div class="panel"><h3>地点 กับ 地方</h3><p><span lang="zh-CN">地点是仓库门口；那个地方没有人。</span><br>地点 เป็นจุดที่ระบุชัด ส่วน 地方 เป็นบริเวณหรือสถานที่ทั่วไป</p></div><div class="panel"><h3>咱们 / 我们 และ 得</h3><p><span lang="zh-CN">咱们得先告诉警察。</span><br>咱们 รวมผู้ฟังด้วย; 我们 อาจรวมหรือไม่รวมก็ได้; 得 ในประโยคนี้อ่าน děi แปลว่า “ต้อง”</p></div><div class="panel"><h3>无论……都/也……</h3><p><span lang="zh-CN">无论结果怎么样，我们都要调查。</span><br>ไม่ว่าผลจะเป็นอย่างไร เราก็ต้องตรวจสอบ</p></div></div></div></section>'''
html, count = re.subn(r'^    <section class="section alt" id="notes">.*</section>\n', lambda _: notes + "\n", html, count=1, flags=re.M)
if count != 1:
    raise ValueError("Could not replace language notes")

html = html.replace("anki_hsk5_3.txt", "anki_hsk5_4.txt")
html = html.replace("HSK5_3_workbook.pdf", "HSK5_4_workbook.pdf")
swap("HSK5 / บทที่ 3", "HSK5 / บทที่ 4")
swap("hsk5_3_mastered_v1", "hsk5_4_mastered_v1")
(root / "HSK5_4.html").write_text(html, encoding="utf-8")

cards = ["#separator:tab", "#html:true", "#tags column:3"]
for word in data["words"]:
    back = f'<b>{word["p"]}</b><br>{word["m"]}<br><i>ใช้เมื่อไร:</i> {word["use"]}<br><br>{word["ex"]}<br>{word["th"]}'
    cards.append(f'{word["h"]}\t{back}\tHSK5_4')
(root / "anki_hsk5_4.txt").write_text("\n".join(cards) + "\n", encoding="utf-8")
