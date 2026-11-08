const { lexicon, grammar, verses, imageAlt } = window.SONG_DATA;
const $ = (id) => document.getElementById(id);
const dialog = $('detailDialog');
const dialogContent = $('dialogContent');
let availableVoices = [];
let selectedVoiceURI = '';
try { selectedVoiceURI = localStorage.getItem('song-study-voice') || ''; } catch {}
const grammarFocus = {
  le: ['了'], zhe: ['逼', '着'], neng: ['能不能'], guo: ['看过', '了'],
  cai: ['才'], congdao: ['从', '到'], feiyao: ['非要'], ba: ['把', '困', '在'],
  bushi: ['不是', '不爱', '了', '吧'], shi: ['是不是'], jiushi: ['就', '让'],
  rang: ['让', '地'], you: ['又'], zhi: ['只是'], na: ['哪怕', '也'], dup: ['骗骗']
};

function el(tag, className, textValue) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (textValue !== undefined) node.textContent = textValue;
  return node;
}

function speak(text) {
  if (!('speechSynthesis' in window)) return;
  speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  const voice = availableVoices.find(v => v.voiceURI === selectedVoiceURI) ||
    availableVoices.find(v => /google/i.test(v.name) && /^zh[-_]TW/i.test(v.lang)) ||
    availableVoices.find(v => /^zh[-_]TW/i.test(v.lang)) ||
    availableVoices.find(v => /^zh[-_]CN/i.test(v.lang));
  if (voice) utterance.voice = voice;
  utterance.lang = voice?.lang || 'zh-TW';
  utterance.rate = 0.82;
  speechSynthesis.speak(utterance);
}

function showWord(word, context) {
  const info = lexicon[word];
  if (!info) return;
  dialogContent.replaceChildren();
  dialogContent.append(el('p', 'dialog-kicker', 'WORD DETAIL'));
  const hanzi = el('h2', 'dialog-hanzi', word);
  hanzi.id = 'dialogTitle';
  hanzi.lang = word === 'Baby' ? 'en' : 'zh-CN';
  dialogContent.append(hanzi, el('p', 'dialog-pinyin', info.pinyin), el('p', 'dialog-meaning', info.thai));
  const meta = el('div', 'dialog-meta');
  meta.append(el('span', `level-badge ${info.hsk === 'นอกบัญชี' ? 'out' : ''}`, info.hsk));
  const listen = el('button', 'dialog-speak', '▶ ฟังคำอ่าน');
  listen.type = 'button';
  if (word === 'Baby' || !('speechSynthesis' in window)) listen.disabled = true;
  listen.addEventListener('click', () => speak(word));
  meta.append(listen);
  dialogContent.append(meta);
  if (context) {
    const box = el('div', 'dialog-context');
    box.append(el('strong', '', 'ในเพลง: '), el('span', '', context));
    dialogContent.append(box);
  }
  dialog.showModal();
}

function showGrammar(id) {
  const rule = grammar[id];
  dialogContent.replaceChildren();
  dialogContent.append(el('p', 'dialog-kicker', 'GRAMMAR NOTE'));
  const title = el('h2', 'dialog-hanzi', rule.label);
  title.id = 'dialogTitle';
  title.style.fontSize = '1.5rem';
  dialogContent.append(title, el('p', 'dialog-meaning', rule.note));
  dialog.showModal();
}

function renderStory() {
  const scenes = [
    ['การจากลา', 'ถนนว่างเปล่า เหลือไว้เพียงใบไม้กับคนที่ยังรอ'],
    ['คืนที่ไม่หลับ', 'ลบประวัติแล้ว ก็ยังลบความคิดถึงไม่ได้'],
    ['ขึ้นสูง · ตกแรง', 'ความสัมพันธ์พุ่งขึ้นฟ้า ก่อนดิ่งลงทันที'],
    ['ฝนในใจ', 'แม้ฟ้าจะเปิด คำพูดบางคำยังทำให้ติดอยู่ในฤดูฝน']
  ];
  scenes.forEach(([title, desc], index) => {
    const card = el('article', 'story-card');
    const img = el('img');
    img.src = `images/scene-${index + 1}.webp`;
    img.alt = imageAlt[index + 1];
    img.loading = index === 0 ? 'eager' : 'lazy';
    const body = el('div', 'story-body');
    body.append(el('span', 'story-num', `SCENE 0${index + 1}`), el('h3', '', title), el('p', '', desc));
    card.append(img, body);
    $('storyGrid').append(card);
  });
}

function renderVerses() {
  verses.forEach((verse, verseIndex) => {
    const card = el('article', 'verse-card');
    card.id = `verse-${verseIndex + 1}`;
    const cover = el('div', 'verse-cover');
    const img = el('img');
    img.src = `images/scene-${verse.image}.webp`;
    img.alt = imageAlt[verse.image];
    img.loading = 'lazy';
    cover.append(img, el('span', 'verse-number', `PART 0${verseIndex + 1}`), el('h3', 'verse-title', verse.title));
    const lines = el('div', 'lines');
    verse.lines.forEach(([segmented, thai, grammarId], lineIndex) => {
      const tokens = segmented.split('|');
      const row = el('div', 'lyric-line');
      row.append(el('span', 'line-no', String(lineIndex + 1).padStart(2, '0')));
      const main = el('div', 'line-main');
      const cn = el('div', 'cn-line');
      cn.lang = 'zh-CN';
      for (const token of tokens) {
        const rule = grammarId && grammar[grammarId];
        const highlighted = rule && grammarFocus[grammarId]?.includes(token);
        const button = el('button', `word${highlighted ? ` grammar-${rule.color}` : ''}`, token);
        button.type = 'button';
        button.title = `${lexicon[token].pinyin} · ${lexicon[token].thai} · ${lexicon[token].hsk}`;
        button.setAttribute('aria-label', `${token}, ${lexicon[token].pinyin}, ${lexicon[token].thai}, ${lexicon[token].hsk}`);
        button.addEventListener('click', () => showWord(token, thai));
        cn.append(button);
      }
      main.append(cn);
      main.append(el('div', 'py-line', tokens.map(token => lexicon[token].pinyin).join(' ')));
      main.append(el('div', 'th-line', thai));
      if (grammarId) {
        const rule = grammar[grammarId];
        const note = el('button', `grammar-trigger ${rule.color}`, rule.label);
        note.type = 'button';
        note.addEventListener('click', () => showGrammar(grammarId));
        main.append(note);
      }
      row.append(main);
      const actions = el('div', 'line-actions');
      const audioButton = el('button', 'speak-line', '▶');
      audioButton.type = 'button';
      audioButton.title = 'ฟังบรรทัดนี้';
      audioButton.setAttribute('aria-label', `ฟังบรรทัดที่ ${lineIndex + 1}`);
      if (!('speechSynthesis' in window)) audioButton.disabled = true;
      audioButton.addEventListener('click', () => speak(tokens.join('')));
      actions.append(audioButton);
      row.append(actions);
      lines.append(row);
    });
    card.append(cover, lines);
    $('verseList').append(card);
  });
}

function setupToggle(buttonId, className) {
  const button = $(buttonId);
  button.addEventListener('click', () => {
    document.body.classList.toggle(className);
    const on = !document.body.classList.contains(className);
    button.classList.toggle('active', on);
    button.setAttribute('aria-pressed', String(on));
  });
}

function renderVocab() {
  const query = $('vocabSearch').value.trim().toLocaleLowerCase();
  const level = $('levelFilter').value;
  const items = Object.entries(lexicon).filter(([word, info]) =>
    (level === 'all' || info.hsk === level) &&
    `${word} ${info.pinyin} ${info.thai}`.toLocaleLowerCase().includes(query)
  );
  const grid = $('vocabGrid');
  grid.replaceChildren();
  $('vocabCount').textContent = `แสดง ${items.length} จาก ${Object.keys(lexicon).length} คำ`;
  if (!items.length) grid.append(el('p', 'empty-state', 'ไม่พบคำที่ตรงกับการค้นหา'));
  for (const [word, info] of items) {
    const button = el('button', 'vocab-item');
    button.type = 'button';
    button.append(el('strong', 'vocab-hanzi', word), el('span', `level-badge ${info.hsk === 'นอกบัญชี' ? 'out' : ''}`, info.hsk), el('span', 'vocab-pinyin', info.pinyin), el('span', 'vocab-meaning', info.thai));
    button.addEventListener('click', () => showWord(word));
    grid.append(button);
  }
}

function renderGrammar() {
  Object.values(grammar).forEach(rule => {
    const card = el('article', `grammar-card ${rule.color}`);
    card.append(el('h3', '', rule.label), el('p', '', rule.note));
    $('grammarGrid').append(card);
  });
}

function loadVoices() {
  if (!('speechSynthesis' in window)) {
    $('voiceSelect').innerHTML = '<option value="">เบราว์เซอร์นี้ไม่มีเสียงอ่าน</option>';
    $('voiceSelect').disabled = true;
    $('voiceHint').textContent = 'ไม่มี Web Speech API';
    return;
  }
  availableVoices = speechSynthesis.getVoices();
  const select = $('voiceSelect');
  const previous = selectedVoiceURI;
  select.replaceChildren();
  const preferred = availableVoices.find(v => /google/i.test(v.name) && /^zh[-_]TW/i.test(v.lang)) ||
    availableVoices.find(v => /^zh[-_]TW/i.test(v.lang)) ||
    availableVoices.find(v => /^zh[-_]CN/i.test(v.lang));
  const chineseVoices = availableVoices.filter(v => /^zh([-_]|$)/i.test(v.lang));
  const options = chineseVoices.length ? chineseVoices : availableVoices;
  if (!options.length) {
    const option = document.createElement('option');
    option.value = '';
    option.textContent = 'ยังไม่พบเสียงอ่าน';
    select.append(option);
    $('voiceHint').textContent = 'เสียงอ่านขึ้นกับเสียงที่ติดตั้งใน Chrome/เครื่อง';
    return;
  }
  for (const voice of options) {
    const option = document.createElement('option');
    option.value = voice.voiceURI;
    option.textContent = `${voice.name} · ${voice.lang}`;
    select.append(option);
  }
  const current = options.find(v => v.voiceURI === previous);
  const chosen = current || (preferred && options.find(v => v.voiceURI === preferred.voiceURI)) || options[0];
  selectedVoiceURI = chosen.voiceURI;
  select.value = selectedVoiceURI;
  try { localStorage.setItem('song-study-voice', selectedVoiceURI); } catch {}
  $('voiceHint').textContent = /^zh[-_]TW/i.test(chosen.lang)
    ? (/google/i.test(chosen.name) ? 'เลือกเสียง Google ภาษาจีนไต้หวันแล้ว' : 'เลือกเสียงภาษาจีนไต้หวันแล้ว')
    : 'ไม่พบเสียง zh-TW; เลือกเสียงที่มีในเครื่อง';
}

renderStory();
renderVerses();
renderVocab();
renderGrammar();
setupToggle('togglePinyin', 'hide-pinyin');
setupToggle('toggleThai', 'hide-thai');
setupToggle('toggleGrammar', 'hide-grammar');
$('vocabSearch').addEventListener('input', renderVocab);
$('levelFilter').addEventListener('change', renderVocab);
$('dialogClose').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
$('voiceSelect').addEventListener('change', event => {
  selectedVoiceURI = event.target.value;
  try { localStorage.setItem('song-study-voice', selectedVoiceURI); } catch {}
  const voice = availableVoices.find(v => v.voiceURI === selectedVoiceURI);
  $('voiceHint').textContent = voice ? `${voice.name} · ${voice.lang}` : '';
});
loadVoices();
if ('speechSynthesis' in window) speechSynthesis.addEventListener('voiceschanged', loadVoices);
