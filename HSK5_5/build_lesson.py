"""Build HSK5_5.html and an Anki import file from lesson_data.json."""
from __future__ import annotations

import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent
data = json.loads((root / "lesson_data.json").read_text(encoding="utf-8"))
html = (root.parent / "HSK5_4" / "HSK5_4.html").read_text(encoding="utf-8")


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

swap("<title>被删掉的名字 · HSK5 บทที่ 4</title>", "<title>消失的那一票 · HSK5 บทที่ 5</title>")
swap("เรียนศัพท์ใหม่ HSK5 บทที่ 4 ผ่านเรื่องต่อของหลินอวี่ กดดูคำอ่านและความหมายของทุกคำในเรื่องได้", "เรียนศัพท์ใหม่ HSK5 บทที่ 5 ผ่านเรื่องต่อของหลินอวี่ กดดูคำอ่านและความหมายของทุกคำในเรื่องได้")
swap("SUPERCHINESE · HSK5/04", "SUPERCHINESE · HSK5/05")
swap('<a href="../HSK5_3/HSK5_3.html">← บทที่ 3</a>', '<a href="../HSK5_4/HSK5_4.html">← บทที่ 4</a>')
html = html.replace('<a href="../HSK5_5/HSK5_5.html">บทที่ 5 →</a>', '')
html = html.replace('<a href="../HSK5_4/HSK5_4.html">← บทที่ 4</a>', '<a href="../HSK5_4/HSK5_4.html">← บทที่ 4</a><a href="../HSK5_6/HSK5_6.html">บทที่ 6 →</a>')

hero = '''  <header class="hero" id="top"><div class="wrap"><div class="eyebrow">HSK 5 · Chapter 05 · เรื่องต่อเนื่อง</div><h1 lang="zh-CN">消失的那一票</h1><p class="subtitle">คะแนนเสียงที่หายไป</p><p>รายชื่อผู้รับผิดชอบอีกคนชี้ไปที่ศาสตราจารย์กู้ ผู้ที่เฉินหนิงเคยไว้วางใจ แต่ผลทดสอบและบันทึกการลงคะแนนกลับเล่าเรื่องอีกแบบ หลินอวี่ต้องหาว่าใครลบคะแนนคัดค้านและทำไม</p><div class="hero-actions"><a class="btn primary" href="#story">เริ่มอ่านตอนที่ 1 →</a><a class="btn" href="../vocabulary-orbit.html">เล่นวงคำศัพท์รวม ↗</a></div><div class="statline"><span><b>27</b> คำใหม่จาก Excel</span><span><b>3</b> ตอนต่อเนื่อง</span><span><b>10</b> ข้อทดสอบ</span></div></div></header>'''
html, count = re.subn(r'  <header class="hero".*?</header>', lambda _: hero, html, count=1, flags=re.S)
if count != 1:
    raise ValueError("Could not replace cover")

swap("หลังพบชื่อพี่สาวในรายชื่อผู้ใช้ที่ถูกลบ หลินอวี่ เฉินหนิง และหลินเสวี่ยตามข้อความนัดพบไปโกดังเก่า ความจริงเรื่องผู้แจ้งเบาะแสกำลังจะปรากฏ", "ตำรวจพบชื่อศาสตราจารย์กู้ในรายชื่อผู้รับผิดชอบ หลินอวี่และเฉินหนิงตามไปถามเขา ก่อนพบว่าคะแนนคัดค้านการใช้บัญชีทดสอบถูกลบออกจากระบบ")
swap("จำได้แล้ว 0 / 19 คำ", "จำได้แล้ว 0 / 27 คำ")
swap("คำใหม่ 19 รายการมาจาก Excel; รายการเปรียบเทียบแยกเป็น 地方 และ 咱们 พร้อมอธิบายคู่คำและไวยากรณ์", "คำฝึก 27 รายการมาจาก Excel แถว 82–107: แยก 以为/认为 เป็นสองคำ และเก็บ 既…又 เป็นหนึ่งโครงสร้าง")

notes = '''    <section class="section alt" id="notes"><div class="wrap"><div class="section-head"><div><div class="tagline">Language notes</div><h2>คำคู่และโครงสร้างในสมุด</h2></div></div><div class="note-list"><div class="panel"><h3>以为 กับ 认为</h3><p><span lang="zh-CN">我以为他同意了；我认为他在保护证据。</span><br>以为 = นึกว่า (มักพบภายหลังว่าเข้าใจผิด); 认为 = คิดว่า/เห็นว่า เป็นการแสดงความคิดเห็น</p></div><div class="panel"><h3>既……又……</h3><p><span lang="zh-CN">她既害羞又认真。</span><br>ใช้เชื่อมคุณลักษณะหรือการกระทำสองอย่างของประธานเดียวกัน = ทั้ง…และ…</p></div><div class="panel"><h3>并且 และ 与……无关</h3><p><span lang="zh-CN">他保存了记录，并且通知了警察。这件事与他无关。</span><br>并且 เพิ่มข้อมูลในทิศทางเดียวกัน; 与……无关 บอกว่าไม่เกี่ยวข้องกับอีกสิ่งหนึ่ง</p></div></div></div></section>'''
html, count = re.subn(r'^    <section class="section alt" id="notes">.*</section>\n', lambda _: notes + "\n", html, count=1, flags=re.M)
if count != 1:
    raise ValueError("Could not replace language notes")

html = html.replace("anki_hsk5_4.txt", "anki_hsk5_5.txt")
html = html.replace("HSK5_4_workbook.pdf", "HSK5_5_workbook.pdf")
swap("HSK5 / บทที่ 4", "HSK5 / บทที่ 5")
swap("hsk5_4_mastered_v1", "hsk5_5_mastered_v1")
(root / "HSK5_5.html").write_text(html, encoding="utf-8")

cards = ["#separator:tab", "#html:true", "#tags column:3"]
for word in data["words"]:
    back = f'<b>{word["p"]}</b><br>{word["m"]}<br><i>ใช้เมื่อไร:</i> {word["use"]}<br><br>{word["ex"]}<br>{word["th"]}'
    cards.append(f'{word["h"]}\t{back}\tHSK5_5')
(root / "anki_hsk5_5.txt").write_text("\n".join(cards) + "\n", encoding="utf-8")
