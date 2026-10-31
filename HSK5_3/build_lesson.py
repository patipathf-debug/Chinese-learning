"""Build HSK5_3.html and an Anki import file from lesson_data.json."""
from __future__ import annotations

import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent
data = json.loads((root / "lesson_data.json").read_text(encoding="utf-8"))
html = (root.parent / "HSK5_2" / "HSK5_2.html").read_text(encoding="utf-8")


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

swap("<title>两种名单 · HSK5 บทที่ 2</title>", "<title>屏幕上的名字 · HSK5 บทที่ 3</title>")
swap("เรียนศัพท์ใหม่ HSK5 บทที่ 2 ผ่านเรื่องของหลินอวี่ พร้อมพินอิน คำแปล บัตรคำ และเสียงอ่านภาษาจีน", "เรียนศัพท์ใหม่ HSK5 บทที่ 3 ผ่านเรื่องของหลินอวี่ กดดูคำอ่านและความหมายของทุกคำในเรื่องได้")
swap("SUPERCHINESE · HSK5/02", "SUPERCHINESE · HSK5/03")
swap('<a href="../HSK5_1/HSK5_1.html">← บทที่ 1</a>', '<a href="../HSK5_2/HSK5_2.html">← บทที่ 2</a>')
html = html.replace('<a href="../HSK5_3/HSK5_3.html">บทที่ 3 →</a>', '')

hero = '''  <header class="hero" id="top"><div class="wrap"><div class="eyebrow">HSK 5 · Chapter 03 · เรื่องต่อเนื่อง</div><h1 lang="zh-CN">屏幕上的名字</h1><p class="subtitle">ชื่อบนหน้าจอ</p><p>ชื่อของหลินอวี่ปรากฏในฐานะผู้สร้างบัญชีปลอม เธอกับพี่สาวต้องตามรอยเว็บไซต์รับสมัครงานและกล่องเอกสารเก่า ก่อนพยานคนหนึ่งจะบอกว่าคนที่ถูกลบจากรายชื่อคือใคร</p><div class="hero-actions"><a class="btn primary" href="#story">เริ่มอ่านตอนที่ 1 →</a><a class="btn" href="../vocabulary-orbit.html">เล่นวงคำศัพท์รวม ↗</a></div><div class="statline"><span><b>21</b> คำใหม่จาก Excel</span><span><b>3</b> ตอนต่อเนื่อง</span><span><b>10</b> ข้อทดสอบ</span></div></div></header>'''
html, count = re.subn(r'  <header class="hero".*?</header>', lambda _: hero, html, count=1, flags=re.S)
if count != 1:
    raise ValueError("Could not replace cover")

swap("ตัวละครหลัก: 林雨 (Lín Yǔ) และ 林雪 (Lín Xuě)", "ตัวละครหลัก: 林雨 (Lín Yǔ), 林雪 (Lín Xuě) และ 陈宁 (Chén Níng)")
swap("หลังพบชื่อพี่สาวในฐานข้อมูล หลินอวี่ต้องแยกบัญชีทดสอบออกจากผู้ใช้จริง หลินเสวี่ยกลับมาพร้อมหลักฐานและความลับเรื่องผู้จัดการ", "หลังเปิดเผยข้อมูลผู้ใช้ปลอม หลินอวี่กลับถูกระบุว่าเป็นผู้สร้างบัญชี เธอตามรอยเว็บไซต์รับสมัครงานและเอกสารเก่าที่อาจพิสูจน์ว่าใครอยู่เบื้องหลัง")
swap("จำได้แล้ว 0 / 23 คำ", "จำได้แล้ว 0 / 21 คำ")
swap("คำจีน 23 คำใหม่มาจาก Excel; พินอิน ความหมาย คำอธิบาย และตัวอย่างเพิ่มเติมจัดทำสำหรับบทนี้", "คำจีน พินอิน และความหมาย 21 คำใหม่มาจาก Excel; ตัวอย่างและเรื่องอ่านจัดทำสำหรับบทนี้")
swap("คำที่ขีดเส้นจุดคือศัพท์ใหม่ กดดูพินอิน ความหมาย และวิธีใช้ได้ เปิดพินอินหรือคำแปลทั้งตอนเมื่อพร้อม", "แตะคำจีนทุกคำในเรื่องเพื่อดูคำอ่านและความหมาย ศัพท์ใหม่เน้นสีเข้ม เปิดพินอินหรือคำแปลทั้งตอนแยกกันได้")

notes = '''    <section class="section alt" id="notes"><div class="wrap"><div class="section-head"><div><div class="tagline">Language notes</div><h2>จุดที่ต้องฝึกจากสมุด</h2></div></div><div class="note-list"><div class="panel"><h3>พูดกับใครเรื่องอะไร</h3><p><span lang="zh-CN">我还有一件事要和你说。</span><br>ฉันยังมีอีกเรื่องหนึ่งที่จะคุยกับคุณ — ใช้ 和/跟 + คน + 说 + เรื่อง</p></div><div class="panel"><h3>另外 + คำนาม</h3><p><span lang="zh-CN">另外一件事</span><br>อีกเรื่องหนึ่ง; 另外 อยู่หน้าคำนามที่ขยาย</p></div><div class="panel"><h3>既然……就…… และ 而</h3><p><span lang="zh-CN">既然有证据，就不能沉默。她想说，而经理不让她说。</span><br>ในเมื่อมีหลักฐานก็เงียบไม่ได้; 而 เชื่อมข้อความสองด้านที่ต่างกัน</p></div></div></div></section>'''
html, count = re.subn(r'^    <section class="section alt" id="notes">.*</section>\n', lambda _: notes + "\n", html, count=1, flags=re.M)
if count != 1:
    raise ValueError("Could not replace language notes")

html = html.replace("anki_hsk5_2.txt", "anki_hsk5_3.txt")
swap("HSK5 / บทที่ 2", "HSK5 / บทที่ 3")
swap("hsk5_2_mastered_v1", "hsk5_3_mastered_v1")
(root / "HSK5_3.html").write_text(html, encoding="utf-8")

cards = ["#separator:tab", "#html:true", "#tags column:3"]
for word in data["words"]:
    back = f'<b>{word["p"]}</b><br>{word["m"]}<br><i>ใช้เมื่อไร:</i> {word["use"]}<br><br>{word["ex"]}<br>{word["th"]}'
    cards.append(f'{word["h"]}\t{back}\tHSK5_3')
(root / "anki_hsk5_3.txt").write_text("\n".join(cards) + "\n", encoding="utf-8")
