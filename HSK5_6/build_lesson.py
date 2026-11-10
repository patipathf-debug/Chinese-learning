# -*- coding: utf-8 -*-
"""Build HSK5_6.html and an Anki import file from lesson_data.json."""
from __future__ import annotations

import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent
data = json.loads((root / "lesson_data.json").read_text(encoding="utf-8"))
html = (root.parent / "HSK5_5" / "HSK5_5.html").read_text(encoding="utf-8")


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

swap("<title>消失的那一票 · HSK5 บทที่ 5</title>", "<title>照片里的人 · HSK5 บทที่ 6</title>")
swap("เรียนศัพท์ใหม่ HSK5 บทที่ 5 ผ่านเรื่องต่อของหลินอวี่ กดดูคำอ่านและความหมายของทุกคำในเรื่องได้", "เรียนศัพท์ใหม่ HSK5 บทที่ 6 ผ่านเรื่องต่อของหลินอวี่ กดดูคำอ่านและความหมายของทุกคำในเรื่องได้")
swap("SUPERCHINESE · HSK5/05", "SUPERCHINESE · HSK5/06")
swap('<a href="../HSK5_4/HSK5_4.html">← บทที่ 4</a>', '<a href="../HSK5_5/HSK5_5.html">← บทที่ 5</a>')
html = html.replace('<a href="../HSK5_6/HSK5_6.html">บทที่ 6 →</a>', '')

hero = '''  <header class="hero" id="top"><div class="wrap"><div class="eyebrow">HSK 5 · Chapter 06 · เรื่องต่อเนื่อง</div><h1 lang="zh-CN">照片里的人</h1><p class="subtitle">คนในภาพถ่าย</p><p>ผู้กำกับโฆษณาเดินเข้าห้องประชุมพร้อมเซลฟีที่ถ่ายวันทดสอบ ภาพที่ถูกห้ามแชร์อาจพิสูจน์ว่าใครสร้างบัญชีปลอม แต่กลับโยงหลินเสวี่ยและเฉินหนิงเข้ากับแฟ้มหลักฐานที่หายไป</p><div class="hero-actions"><a class="btn primary" href="#story">เริ่มอ่านตอนที่ 1 →</a><a class="btn" href="../vocabulary-orbit.html">เล่นวงคำศัพท์รวม ↗</a></div><div class="statline"><span><b>19</b> คำฝึกใหม่จาก Google Sheet</span><span><b>3</b> ตอนต่อเนื่อง</span><span><b>10</b> ข้อทดสอบ</span></div></div></header>'''
html, count = re.subn(r'  <header class="hero".*?</header>', lambda _: hero, html, count=1, flags=re.S)
if count != 1:
    raise ValueError("Could not replace cover")

swap("ตำรวจพบชื่อศาสตราจารย์กู้ในรายชื่อผู้รับผิดชอบ หลินอวี่และเฉินหนิงตามไปถามเขา ก่อนพบว่าคะแนนคัดค้านการใช้บัญชีทดสอบถูกลบออกจากระบบ", "โจวหลาน ผู้กำกับโฆษณา ปรากฏตัวพร้อมภาพเซลฟีจากวันทดสอบ หลินอวี่ต้องเทียบภาพกับวิดีโอและถามว่าหลักฐานที่หายไปอยู่ในมือใคร")
swap("จำได้แล้ว 0 / 27 คำ", "จำได้แล้ว 0 / 19 คำ")
swap("คำฝึก 27 รายการมาจาก Excel แถว 82–107: แยก 以为/认为 เป็นสองคำ และเก็บ 既…又 เป็นหนึ่งโครงสร้าง", "คำฝึก 19 รายการจาก Google Sheet แถว 108–125: แยก 要是/如果 เป็นสองคำสำหรับเปรียบเทียบ")

notes = '''    <section class="section alt" id="notes"><div class="wrap"><div class="section-head"><div><div class="tagline">Language notes</div><h2>คำคู่และโครงสร้างในสมุด</h2></div></div><div class="note-list"><div class="panel"><h3>要是 กับ 如果</h3><p><span lang="zh-CN">要是照片是真的，我们就有证据。如果有人改过照片，我们就再检查。</span><br>ทั้งสองคำแปลว่า “ถ้า”; 要是 เป็นกันเองกว่า ส่วน 如果 ใช้ได้ทั่วไปและเป็นทางการกว่า</p></div><div class="panel"><h3>对于……来说</h3><p><span lang="zh-CN">对于林雪来说，保护数据更重要。</span><br>วางคนหรือเรื่องที่เป็นมุมมองไว้ระหว่าง 对于 กับ 来说 แล้วตามด้วยความเห็น</p></div><div class="panel"><h3>跟/和 + คน + 说 + เรื่อง</h3><p><span lang="zh-CN">我还要跟你说另外一件事。</span><br>ใช้ลำดับ “พูดกับใครเรื่องอะไร” ตามแท็บ จุดที่ต้องฝึก ในสมุดต้นทาง; 经过 = หลังจากผ่านเหตุการณ์</p></div></div></div></section>'''
html, count = re.subn(r'^    <section class="section alt" id="notes">.*</section>\n', lambda _: notes + "\n", html, count=1, flags=re.M)
if count != 1:
    raise ValueError("Could not replace language notes")

html = html.replace("anki_hsk5_5.txt", "anki_hsk5_6.txt")
html = html.replace("HSK5_5_workbook.pdf", "HSK5_6_workbook.pdf")
swap("HSK5 / บทที่ 5", "HSK5 / บทที่ 6")
swap("hsk5_5_mastered_v1", "hsk5_6_mastered_v1")
(root / "HSK5_6.html").write_text(html, encoding="utf-8")

cards = ["#separator:tab", "#html:true", "#tags column:3"]
for word in data["words"]:
    back = f'<b>{word["p"]}</b><br>{word["m"]}<br><i>ใช้เมื่อไร:</i> {word["use"]}<br><br>{word["ex"]}<br>{word["th"]}'
    cards.append(f'{word["h"]}\t{back}\tHSK5_6')
(root / "anki_hsk5_6.txt").write_text("\n".join(cards) + "\n", encoding="utf-8")
