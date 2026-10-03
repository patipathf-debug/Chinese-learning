(() => {
  'use strict';
  const source = window.HSK4_VOCAB || [];
  const words = source.map((w, index) => ({ ...w, id: index }));
  const key = 'hsk4_memory_lab_v1';
  const intervals = [0, 1, 3, 7, 14, 30];
  const $ = id => document.getElementById(id);
  const daySelect = $('daySelect');
  const poolSelect = $('poolSelect');
  let mode = 'mixed';
  let round = [];
  let position = 0;
  let score = 0;
  let missed = [];
  let answered = false;
  let state = {};

  try { state = JSON.parse(localStorage.getItem(key) || '{}') || {}; } catch (_) { state = {}; }
  const idOf = w => `${w.day}|${w.id}`;
  const today = () => new Date().toLocaleDateString('en-CA');
  const addDays = n => { const d = new Date(); d.setHours(12, 0, 0, 0); d.setDate(d.getDate() + n); return d.toLocaleDateString('en-CA'); };
  const record = w => state[idOf(w)] || { box: 0, seen: 0, wrong: 0, due: today() };
  const save = () => { try { localStorage.setItem(key, JSON.stringify(state)); } catch (_) {} };
  const shuffle = a => { const copy = [...a]; for (let i = copy.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [copy[i], copy[j]] = [copy[j], copy[i]]; } return copy; };
  const clean = s => String(s || '').replace(/<[^>]*>/g, '').trim();

  function scoped() {
    return daySelect.value === 'all' ? words : words.filter(w => w.day === daySelect.value);
  }
  function candidates() {
    const all = scoped();
    if (poolSelect.value === 'weak') return all.filter(w => record(w).wrong > 0);
    if (poolSelect.value === 'all') return all;
    return all.filter(w => !record(w).seen || record(w).due <= today());
  }
  function updateStats() {
    const all = scoped();
    const due = all.filter(w => record(w).seen && record(w).due <= today()).length;
    const unseen = all.filter(w => !record(w).seen).length;
    const weak = all.filter(w => record(w).wrong > 0).length;
    $('setupStats').textContent = `${all.length} คำในชุด · ถึงเวลาทวน ${due} · คำใหม่ ${unseen} · เคยพลาด ${weak}`;
    $('startBtn').disabled = candidates().length === 0;
    $('startBtn').textContent = candidates().length ? `เริ่มฝึก ${Math.min(10, candidates().length)} คำ →` : 'ไม่มีคำในชุดนี้';
  }
  function speak(text) {
    if (!('speechSynthesis' in window)) return;
    speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(clean(text));
    utterance.lang = 'zh-CN';
    utterance.rate = .86;
    const preferred = localStorage.getItem('preferred_voice');
    const voices = speechSynthesis.getVoices();
    utterance.voice = voices.find(v => v.name === preferred && /^zh|cmn/i.test(v.lang)) || voices.find(v => /^zh-CN|cmn/i.test(v.lang)) || null;
    speechSynthesis.speak(utterance);
  }
  function setView(view) {
    $('setup').style.display = view === 'setup' ? 'grid' : 'none';
    $('play').style.display = view === 'play' ? 'block' : 'none';
    $('result').style.display = view === 'result' ? 'block' : 'none';
  }
  function chooseRound() {
    const c = candidates();
    if (poolSelect.value === 'due') {
      const due = c.filter(w => record(w).seen && record(w).due <= today()).sort((a, b) => record(a).due.localeCompare(record(b).due));
      const fresh = shuffle(c.filter(w => !record(w).seen));
      return [...due, ...fresh].slice(0, 10);
    }
    return shuffle(c).slice(0, 10);
  }
  function typeFor(index) { return mode === 'mixed' ? ['meaning', 'listen', 'reverse'][index % 3] : mode; }
  function makeChoices(w, type) {
    const answer = type === 'meaning' ? w.m : w.h;
    const field = type === 'meaning' ? 'm' : 'h';
    const seen = new Set([answer]);
    const pool = shuffle(words.filter(x => x.h !== w.h && x.day === w.day).concat(shuffle(words.filter(x => x.h !== w.h && x.day !== w.day))));
    const choices = [answer];
    for (const x of pool) { if (!seen.has(x[field])) { choices.push(x[field]); seen.add(x[field]); } if (choices.length === 4) break; }
    return shuffle(choices);
  }
  function renderQuestion() {
    if (position >= round.length) return showResult();
    answered = false;
    const w = round[position];
    const type = typeFor(position);
    $('roundLabel').textContent = `ข้อ ${position + 1} / ${round.length} · Day ${w.day}`;
    $('scoreLabel').textContent = `ตอบถูก ${score}`;
    $('progressBar').style.width = `${position / round.length * 100}%`;
    $('feedback').className = 'feedback';
    $('feedback').replaceChildren();
    $('choices').replaceChildren();
    $('prompt').replaceChildren();
    const hasDuplicate = source.some(x => x !== source[w.id] && x.h === w.h && x.day === w.day);
    $('promptLabel').textContent = type === 'meaning' ? (hasDuplicate ? `คำนี้ในบริบท “${w.coll}” แปลว่าอะไร?` : 'คำนี้แปลว่าอะไร?') : type === 'listen' ? 'ฟังเสียงแล้วเลือกคำจีน' : 'ความหมายนี้คือคำจีนคำไหน?';
    $('hint').textContent = type === 'listen' ? 'กดฟังซ้ำได้ตามต้องการ' : 'ลองนึกคำตอบก่อนดูตัวเลือก';
    const prompt = document.createElement('div');
    prompt.className = type === 'meaning' ? 'hanzi' : type === 'listen' ? 'audio-icon' : 'meaning-prompt';
    prompt.textContent = type === 'meaning' ? w.h : type === 'listen' ? '🔊' : w.m;
    $('prompt').append(prompt);
    $('speakBtn').style.display = type === 'reverse' ? 'none' : 'inline-block';
    for (const choice of makeChoices(w, type)) {
      const button = document.createElement('button');
      button.type = 'button'; button.className = 'choice'; button.textContent = choice;
      button.addEventListener('click', () => answer(choice, button, type));
      $('choices').append(button);
    }
    if (type === 'listen') setTimeout(() => { if (!answered && $('play').style.display === 'block') speak(w.h); }, 200);
  }
  function answer(choice, button, type) {
    if (answered) return;
    answered = true;
    const w = round[position];
    const correct = type === 'meaning' ? w.m : w.h;
    const ok = choice === correct;
    if (ok) score++; else missed.push(w);
    const previous = record(w);
    const box = ok ? Math.min(previous.box + 1, 5) : 0;
    state[idOf(w)] = { box, seen: previous.seen + 1, wrong: previous.wrong + (ok ? 0 : 1), due: addDays(intervals[box]), updatedAt: new Date().toISOString() };
    save();
    if (typeof syncToCloud === 'function') syncToCloud();
    for (const b of $('choices').children) {
      b.disabled = true;
      if (b.textContent === correct) b.classList.add('correct');
    }
    if (!ok) button.classList.add('wrong');
    $('scoreLabel').textContent = `ตอบถูก ${score}`;
    const feedback = $('feedback');
    feedback.className = 'feedback show';
    const title = document.createElement('strong'); title.textContent = ok ? '✓ ถูกต้อง' : 'ลองจำคำนี้อีกครั้ง';
    const hanzi = document.createElement('p'); hanzi.className = 'cn'; hanzi.textContent = w.h;
    const detail = document.createElement('p'); detail.textContent = `${w.p} · ${w.m}`;
    const example = document.createElement('p'); example.textContent = `ใช้คู่กัน: ${w.coll}`;
    const schedule = document.createElement('p'); schedule.className = 'helper'; schedule.textContent = ok ? `ทวนครั้งถัดไป: ${state[idOf(w)].due}` : 'คำนี้จะกลับมาอยู่ในชุดทวน';
    const next = document.createElement('button'); next.className = 'next'; next.type = 'button'; next.textContent = position === round.length - 1 ? 'ดูผลเซตนี้ →' : 'คำถัดไป →';
    next.addEventListener('click', () => { position++; renderQuestion(); });
    feedback.append(title, hanzi, detail, example, schedule, next);
    speak(w.h);
  }
  function start() {
    round = chooseRound(); if (!round.length) return;
    position = 0; score = 0; missed = [];
    setView('play'); renderQuestion();
  }
  function showResult() {
    window.speechSynthesis?.cancel();
    setView('result');
    $('resultText').textContent = score === round.length ? 'แม่นมาก! กลับมาทวนเมื่อถึงรอบถัดไป' : 'คำที่พลาดถูกเก็บไว้ให้ฝึกซ้ำได้ทันที';
    $('resultScore').textContent = `${score}/${round.length}`;
    $('resultWeak').textContent = missed.length;
    $('resultDue').textContent = scoped().filter(w => record(w).seen && record(w).due <= today()).length;
    $('weakBtn').disabled = missed.length === 0;
  }
  function setup() { window.speechSynthesis?.cancel(); updateStats(); setView('setup'); }

  const days = [...new Set(words.map(w => w.day))].sort((a, b) => Number(a) - Number(b));
  daySelect.append(new Option(`ทุกบท (${words.length} คำ)`, 'all'));
  for (const day of days) daySelect.append(new Option(`Day ${day} (${words.filter(w => w.day === day).length} คำ)`, day));
  const requestedDay = new URLSearchParams(location.search).get('day');
  if (days.includes(requestedDay)) {
    daySelect.value = requestedDay;
    const back = $('lessonBack');
    back.href = `../DAY${requestedDay}/HSK4_L${requestedDay.replace('.', '_')}_SuperChinese.html`;
    back.textContent = `← กลับ Day ${requestedDay}`;
    back.hidden = false;
  }
  daySelect.addEventListener('change', updateStats);
  poolSelect.addEventListener('change', updateStats);
  for (const button of document.querySelectorAll('.mode')) button.addEventListener('click', () => {
    mode = button.dataset.mode;
    document.querySelectorAll('.mode').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
  });
  $('startBtn').addEventListener('click', start);
  $('exitBtn').addEventListener('click', setup);
  $('speakBtn').addEventListener('click', () => speak(round[position].h));
  $('againBtn').addEventListener('click', () => { updateStats(); start(); });
  $('weakBtn').addEventListener('click', () => { poolSelect.value = 'weak'; updateStats(); start(); });
  window.addEventListener('hsk4:cloud-updated', () => {
    try { state = JSON.parse(localStorage.getItem(key) || '{}') || {}; } catch (_) { state = {}; }
    updateStats();
  });
  setup();
})();
