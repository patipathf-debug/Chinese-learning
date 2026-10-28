"""Build HSK5_2.html and Anki cards from lesson_data.json.

The HSK5_1 page is the shared interaction/design template. Rerun this script
after editing lesson_data.json; then check the resulting Chinese and Thai text.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent
data = json.loads((root / "lesson_data.json").read_text(encoding="utf-8"))
html = (root.parent / "HSK5_1" / "HSK5_1.html").read_text(encoding="utf-8")


def swap(old: str, new: str) -> None:
    global html
    count = html.count(old)
    if count != 1:
        raise ValueError(f"Expected one match for {old[:50]!r}; found {count}")
    html = html.replace(old, new)


def js(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def replace_array(name: str, value: object) -> None:
    global html
    pattern = rf"^    const {name}=\[.*?^    \];\n"
    replacement = f"    const {name}={js(value)};\n"
    html, count = re.subn(pattern, lambda _: replacement, html, count=1, flags=re.M | re.S)
    if count != 1:
        raise ValueError(f"Could not replace {name}")


replace_array("words", data["words"])
replace_array("chapterImages", data["images"])
replace_array("chapters", [{key: value for key, value in chapter.items() if key != "py"} for chapter in data["chapters"]])
replace_array("chapterPinyin", [chapter["py"] for chapter in data["chapters"]])
replace_array("questions", data["questions"])

html, count = re.subn(r"^    const usageNotes=\{.*?^    \};\n", "    const usageNotes={};\n", html, count=1, flags=re.M | re.S)
if count != 1:
    raise ValueError("Could not replace usage notes")

swap("<title>数字背后的名字 · HSK5 บทที่ 1</title>", "<title>两种名单 · HSK5 บทที่ 2</title>")
swap("เรียนศัพท์ HSK5 ผ่านเรื่องต่อเนื่องของหลินอวี่ พร้อมบัตรคำ แบบทดสอบ และเสียงอ่านภาษาจีน", "เรียนศัพท์ใหม่ HSK5 บทที่ 2 ผ่านเรื่องของหลินอวี่ พร้อมพินอิน คำแปล บัตรคำ และเสียงอ่านภาษาจีน")
swap("SUPERCHINESE · HSK5/01", "SUPERCHINESE · HSK5/02")
html = html.replace('<a href="../HSK5_2/HSK5_2.html">บทที่ 2 →</a>', '')
swap('<a href="#story">เรื่องเล่า</a>', '<a href="../HSK5_1/HSK5_1.html">← บทที่ 1</a><a href="#story">เรื่องเล่า</a>')

hero = '''  <header class="hero" id="top"><div class="wrap"><div class="eyebrow">HSK 5 · Chapter 02 · เรื่องต่อเนื่อง</div><h1 lang="zh-CN">两种名单</h1><p class="subtitle">รายชื่อสองชุด</p><p>หลินเสวี่ยยอมรับว่าเธอสร้างบัญชีบางส่วน แต่รายชื่อที่เธอให้หลินอวี่ดูบอกความจริงอีกด้าน ก่อนงานแถลงข่าวจบ สองพี่น้องต้องตัดสินใจว่าจะเปิดเผยข้อมูลที่เปลี่ยนอนาคตของทั้งคู่หรือไม่</p><div class="hero-actions"><a class="btn primary" href="#story">เริ่มอ่านตอนที่ 1 →</a><a class="btn" href="#vocab">ดูศัพท์ใหม่ 23 คำ</a></div><div class="statline"><span><b>23</b> คำใหม่จาก Excel</span><span><b>3</b> ตอนต่อเนื่อง</span><span><b>10</b> ข้อทดสอบ</span></div></div></header>'''
html, count = re.subn(r'  <header class="hero".*?</header>', lambda _: hero, html, count=1, flags=re.S)
if count != 1:
    raise ValueError("Could not replace cover")

swap("ตัวละครหลัก: 林雨 (Lín Yǔ) — หลินอวี่", "ตัวละครหลัก: 林雨 (Lín Yǔ) และ 林雪 (Lín Xuě)")
swap("พนักงานออฟฟิศผู้ดูแลข้อมูลของแอป “同路” เธอทำงานตรงเวลาเสมอ แต่คืนนี้ตัวเลขในรายงานบังคับให้เธอเลือกระหว่างความก้าวหน้ากับความจริง", "หลังพบชื่อพี่สาวในฐานข้อมูล หลินอวี่ต้องแยกบัญชีทดสอบออกจากผู้ใช้จริง หลินเสวี่ยกลับมาพร้อมหลักฐานและความลับเรื่องผู้จัดการ")
swap("จำได้แล้ว 0 / 13 คำ", "จำได้แล้ว 0 / 23 คำ")
swap("คำศัพท์และพินอินอ้างอิงจากชีต “คลังคำศัพท์” ในไฟล์ Excel; ประโยคตัวอย่างและเรื่องแต่งขึ้นสำหรับบทนี้", "คำจีน 23 คำใหม่มาจาก Excel; พินอิน ความหมาย คำอธิบาย และตัวอย่างเพิ่มเติมจัดทำสำหรับบทนี้")
swap("คำสีทองคือคำศัพท์ใหม่ กดเพื่อฟังเสียงคำได้ เปิดคำแปลเมื่ออ่านจบแต่ละตอน", "คำที่ขีดเส้นจุดคือศัพท์ใหม่ กดดูพินอิน ความหมาย และวิธีใช้ได้ เปิดพินอินหรือคำแปลทั้งตอนเมื่อพร้อม")

notes = '''    <section class="section alt" id="notes"><div class="wrap"><div class="section-head"><div><div class="tagline">Language notes</div><h2>3 จุดภาษาที่เจอในเรื่อง</h2></div></div><div class="note-list"><div class="panel"><h3>按照 + มาตรฐาน/แผน</h3><p><span lang="zh-CN">按照公司的测试标准输入。</span><br>ป้อนข้อมูลตามมาตรฐานการทดสอบของบริษัท; 按照 วางหน้าสิ่งที่ยึดเป็นเกณฑ์</p></div><div class="panel"><h3>确实 กับ 真实</h3><p><span lang="zh-CN">她确实创建过账号，但真实用户不一样。</span><br>确实 ยืนยันว่า “จริง ๆ”; 真实 ขยายสิ่งที่เป็นจริง เช่น ข้อมูลจริง</p></div><div class="panel"><h3>种 และ 标</h3><p><span lang="zh-CN">两种名单；把错误标出来。</span><br>种 อ่าน zhǒng เมื่อหมายถึง “ชนิด”; 标出 คือทำเครื่องหมายให้เห็น</p></div></div></div></section>'''
html, count = re.subn(r'^    <section class="section alt" id="notes">.*</section>\n', lambda _: notes + "\n", html, count=1, flags=re.M)
if count != 1:
    raise ValueError("Could not replace language notes")

swap("แบบทดสอบ 8 ข้อ", "แบบทดสอบ 10 ข้อ")
html = html.replace("anki_hsk5_1.txt", "anki_hsk5_2.txt")
swap("HSK5 / บทที่ 1", "HSK5 / บทที่ 2")
swap("hsk5_1_mastered_v1", "hsk5_2_mastered_v1")

(root / "HSK5_2.html").write_text(html, encoding="utf-8")

cards = ["#separator:tab", "#html:true", "#tags column:3"]
for word in data["words"]:
    back = f'<b>{word["p"]}</b><br>{word["m"]}<br><i>ใช้เมื่อไร:</i> {word["use"]}<br><br>{word["ex"]}<br>{word["th"]}'
    cards.append(f'{word["h"]}\t{back}\tHSK5_2')
(root / "anki_hsk5_2.txt").write_text("\n".join(cards) + "\n", encoding="utf-8")
