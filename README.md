# 🎓 HSK 4 SuperChinese — Web Learning Dashboard

## เรียนออนไลน์และซิงก์ความจำ

เปิด [เว็บไซต์บทเรียน](https://patipathf-debug.github.io/Chinese-learning/) แล้วกด **☁️ เข้าสู่ระบบเพื่อซิงก์** ใส่อีเมลและเปิดลิงก์ที่ Supabase ส่งมา ใช้อีเมลเดียวกันบนทุกเครื่องเพื่อให้คำที่กด “จำได้แล้ว” ผลเกมสปีด และประวัติเกมห้องฝึกจำตรงกัน ระบบเก็บการเปลี่ยนแปลงในเครื่องเมื่อออฟไลน์และส่งขึ้นคลาวด์เมื่อเชื่อมต่ออีกครั้ง

เกมห้องฝึกจำอยู่ที่ [GAME/memory_lab.html](GAME/memory_lab.html) เลือกบทหรือรวมทุกบทได้ มีโหมดจีน→ไทย ไทย→จีน ฟังเสียง→เลือกคำ และโหมดผสม พร้อมรอบทวนแบบเว้นระยะ เสียงอ่านใช้ระบบเสียงของอุปกรณ์

การตั้งค่าฐานข้อมูลอยู่ใน [database/study_progress_items.sql](database/study_progress_items.sql) ต้องรันใน Supabase โปรเจกต์นี้ก่อนใช้งานซิงก์ ตารางใหม่ใช้ Supabase Auth และ Row Level Security เพื่อให้แต่ละบัญชีเห็นเฉพาะความจำของตน ตาราง `user_progress` เดิมเก็บไว้เป็นข้อมูลสำรอง

เว็บแอปพลิเคชันคลังบทเรียนคำศัพท์ ไวยากรณ์ เรื่องอ่าน และแบบทดสอบวัดผลระดับ **HSK 4** ออกแบบและพัฒนาด้วยระบบ **Active Recall** พร้อมเสียงอ่านภาษาจีนและไฟล์บัตรคำ Anki สำหรับนำไปทบทวนต่อ

---

## 🌟 ฟีเจอร์หลัก (Key Features)

1. **📚 คลังบทเรียนประจำวัน (Day 1 - Day 7 พร้อมบทเสริม Day 6.1):**
   * **คำศัพท์เจาะลึก (Vocab Cards):** แสดงตัวอักษรจีน พินอิน คำแปล Collocation เคล็ดลับการจำ และตัวอย่างประโยค
   * **จุดไวยากรณ์ (Grammar Points):** อธิบายโครงสร้างประโยคพร้อมตัวอย่างเปรียบเทียบและการออกเสียง
   * **เรื่องอ่านไล่ระดับ 3 ระดับ (Graded Readings):** อ่านง่าย ได้ระดับมาตรฐาน HSK 4 พร้อมภาพประกอบสีน้ำและปุ่มเปิด-ปิดพินอิน/คำแปล
   * **แบบทดสอบประจำบท (Lesson Quizzes):** บัตรคำความจำสลับสุ่ม และข้อสอบตัวเลือก 12 ข้อพร้อมคำอธิบายละเอียด

2. **🎓 แบบทดสอบประมวลผลรวม (Comprehensive Exam D1-D5):**
   * รวบรวมคำศัพท์ 116 คำ และไวยากรณ์ 20 เรื่อง
   * พาร์ทการอ่านภาษาจีนมาตรฐาน HSK 4
   * พาร์ทแต่งประโยคที่รองรับการตรวจและให้คะแนนผ่าน **Gemini AI**

3. **🗣️ เสียงออกเสียงภาษาจีน (Fixed Voice System):**
   * ล็อกและบันทึกเสียงออกเสียงอัตโนมัติ (ข้ามไปยังทุกบทเรียนด้วยเสียงเดียวกัน เช่น `Google 國語 (臺灣)` หรือเสียงจีนระบบ)

4. **🎴 ไฟล์บัตรคำ Anki (Anki Decks):**
   * มีไฟล์ `.txt` พร้อมนำเข้าแอป Anki สำหรับบทเรียนต่างๆ (อยู่ในโฟลเดอร์ของแต่ละวัน)

---

## 📁 โครงสร้างโฟลเดอร์ (Project Structure)

```text
06_SuperChinese word/
├── index.html                  # 🏠 หน้าหลักสารบัญ (Main Entry Point)
├── README.md                   # 📖 คู่มือการใช้งานและรายละเอียดโปรเจกต์
├── .gitignore                  # 🚫 ไฟล์ยกเว้นสำหรับ Git
├── DAY1/
│   ├── HSK4_L1_SuperChinese.html
│   └── images/
├── DAY2/
│   ├── HSK4_L2_SuperChinese.html
│   └── images/
├── DAY3/
│   ├── HSK4_L3_SuperChinese.html
│   └── images/
├── DAY4/
│   ├── HSK4_L4_SuperChinese.html
│   └── images/
├── DAY5/
│   ├── HSK4_L5_SuperChinese.html
│   ├── anki_day5_vocab.txt
│   └── images/
├── DAY6/
│   ├── HSK4_L6_SuperChinese.html
│   ├── anki_day6_vocab.txt
│   └── images/
├── DAY6.1/
│   ├── HSK4_L6_1_SuperChinese.html
│   ├── anki_day6_1_vocab.txt
│   └── images/
├── DAY7/
│   ├── HSK4_L7_SuperChinese.html
│   ├── anki_day7_vocab.txt
│   └── images/
└── EXAM_DAY1_5/
    ├── HSK4_Exam_Day1_5.html
    └── images/
```

---

## 🚀 วิธีการนำขึ้น GitHub & GitHub Pages

1. **สร้าง Repository บน GitHub** (เช่น ชื่อ `hsk4-superchinese`)
2. **Push โฟลเดอร์นี้ขึ้น GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - HSK4 SuperChinese Web App"
   git branch -M main
   git remote add origin https://github.com/<YOUR_USERNAME>/<REPO_NAME>.git
   git push -u origin main
   ```
3. **เปิดใช้งาน GitHub Pages (ดูออนไลน์ได้ทันที):**
   * ไปที่ **Settings** -> **Pages** ในหน้า GitHub Repository
   * เลือก Branch: `main` / Folder: `/ (root)` แล้วกด **Save**
   * เว็บไซต์ของคุณจะเปิดใช้งานผ่านลิงก์ `https://<YOUR_USERNAME>.github.io/<REPO_NAME>/` โดยมีหน้าแรกคือ `index.html` อัตโนมัติ!
