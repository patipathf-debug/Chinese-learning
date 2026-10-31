(() => {
  const lexicon = window.READING_LEXICON || {};
  const entries = Object.keys(lexicon).sort((a, b) => b.length - a.length);
  if (!entries.length) return;

  const dialog = document.createElement('dialog');
  dialog.className = 'reading-lookup';
  dialog.setAttribute('aria-labelledby', 'readingLookupWord');
  dialog.innerHTML = '<div class="reading-lookup-head"><div><div id="readingLookupWord" lang="zh-CN"></div><div id="readingLookupPinyin"></div></div><button type="button" id="readingLookupClose" aria-label="ปิด">✕</button></div><p id="readingLookupMeaning"></p><div id="readingLookupUse"></div><div id="readingLookupExample"></div><button type="button" id="readingLookupSpeak">🔊 ฟังคำนี้</button>';
  document.body.append(dialog);

  let currentWord = '';
  const byId = id => document.getElementById(id);
  function readAloud(word) {
    if (typeof speak === 'function') { speak(word); return; }
    if (!('speechSynthesis' in window)) return;
    speechSynthesis.cancel();
    const voice = new SpeechSynthesisUtterance(word);
    voice.lang = 'zh-CN';
    voice.rate = 0.82;
    speechSynthesis.speak(voice);
  }
  function openWord(word) {
    const entry = lexicon[word];
    if (!entry) return;
    currentWord = word;
    byId('readingLookupWord').textContent = word;
    byId('readingLookupPinyin').textContent = entry.p;
    byId('readingLookupMeaning').textContent = entry.m;
    byId('readingLookupUse').textContent = entry.use ? 'ใช้เมื่อไร: ' + entry.use : '';
    byId('readingLookupUse').hidden = !entry.use;
    byId('readingLookupExample').textContent = entry.ex ? entry.ex + (entry.th ? ' — ' + entry.th : '') : '';
    byId('readingLookupExample').hidden = !entry.ex;
    dialog.showModal();
  }
  function makeToken(word, highlighted) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'reading-token' + (highlighted ? ' is-new' : '');
    button.textContent = word;
    button.lang = 'zh-CN';
    button.setAttribute('aria-label', 'ดูคำอ่านและความหมายของ ' + word);
    button.addEventListener('click', () => openWord(word));
    return button;
  }
  function enrichReading(element) {
    const highlighted = new Set([...element.querySelectorAll('.target')].map(node => node.textContent));
    const source = element.textContent || '';
    const fragment = document.createDocumentFragment();
    let buffer = '';
    const flush = () => { if (buffer) { fragment.append(document.createTextNode(buffer)); buffer = ''; } };
    for (let i = 0; i < source.length;) {
      if (!/\p{Script=Han}/u.test(source[i])) { buffer += source[i++]; continue; }
      const word = entries.find(entry => source.startsWith(entry, i));
      if (!word) { buffer += source[i++]; continue; }
      flush();
      fragment.append(makeToken(word, highlighted.has(word)));
      i += word.length;
    }
    flush();
    element.replaceChildren(fragment);
  }
  document.querySelectorAll('.cn').forEach(enrichReading);
  byId('readingLookupClose').addEventListener('click', () => dialog.close());
  byId('readingLookupSpeak').addEventListener('click', () => readAloud(currentWord));
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
})();
