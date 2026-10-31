import fs from 'node:fs';
import vm from 'node:vm';

const root = new URL('.', import.meta.url);
const read = path => fs.readFileSync(new URL(path, root), 'utf8');
const write = (path, value) => fs.writeFileSync(new URL(path, root), value);
const old = read('HSK5_1/HSK5_1.html');
const extract = name => {
  const pattern = new RegExp('const ' + name + '=(\\[[\\s\\S]*?\\]);\\n    const ');
  const match = old.match(pattern);
  if (!match) throw new Error('Cannot read ' + name);
  return vm.runInNewContext(match[1]);
};
const lesson1 = {words: extract('words'), chapters: extract('chapters')};
const lesson2 = JSON.parse(read('HSK5_2/lesson_data.json'));
const lesson3 = JSON.parse(read('HSK5_3/lesson_data.json'));
const byLesson = [lesson1, lesson2, lesson3];
const labels = ['HSK5_1', 'HSK5_2', 'HSK5_3'];
const categoryRules = {
  'คนและความรู้สึก': '白领 心情 压力 分手 熟悉 惊喜 优秀',
  'เวลาและจำนวน': '按时 超过 亿 世纪 之前 将来 种',
  'งานและข้อมูล': '调查 应用 部分 进行 输入 标准 屏幕 记录 真实 标 创建 条件 合作',
  'การสื่อสาร': '解释 确实',
  'คำเชื่อม': '甚至 其次 其中 按照',
  'การกระทำ': '赶 抽烟',
  'สิ่งของและสถานที่': '现实'
};
const categoryMap = new Map(Object.entries(categoryRules).flatMap(([category, list]) => list.split(' ').map(word => [word, category])));
const words = byLesson.flatMap((lesson, i) => lesson.words.map(word => ({
  h: word.h, p: word.p, m: word.m, ex: word.ex, th: word.th,
  use: word.use || '', lesson: labels[i], category: word.cat || categoryMap.get(word.h)
})));
const seen = new Set();
for (const word of words) {
  if (seen.has(word.h)) throw new Error('Duplicate vocabulary: ' + word.h);
  if (!word.category) throw new Error('Missing category: ' + word.h);
  seen.add(word.h);
}
if (words.length !== 57) throw new Error('Expected 57 cumulative words, found ' + words.length);
write('vocabulary-data.js', 'window.VOCABULARY_DATA=' + JSON.stringify(words) + ';\n');

const extra = JSON.parse(read('reading-glossary.json'));
const lexicon = Object.fromEntries(Object.entries(extra).map(([word, [p, m]]) => [word, {p, m}]));
for (const word of words) lexicon[word.h] = {p: word.p, m: word.m, use: word.use, ex: word.ex, th: word.th, lesson: word.lesson};
const keys = Object.keys(lexicon).sort((a, b) => b.length - a.length);
const strip = text => text.replace(/<\/?em>/g, '');
const missing = new Map();
for (let lessonIndex = 0; lessonIndex < byLesson.length; lessonIndex++) {
  const lesson = byLesson[lessonIndex];
  for (let chapterIndex = 0; chapterIndex < lesson.chapters.length; chapterIndex++) {
    const source = strip(lesson.chapters[chapterIndex].cn);
    for (let i = 0; i < source.length;) {
      const char = source[i];
      if (!/\p{Script=Han}/u.test(char)) { i++; continue; }
      const match = keys.find(word => source.startsWith(word, i));
      if (!match) {
        const at = labels[lessonIndex] + '/' + (chapterIndex + 1);
        missing.set(char, [...new Set([...(missing.get(char) || []), at])]);
        i++;
      } else i += match.length;
    }
  }
}
if (missing.size) {
  for (const [word, locations] of missing) console.error(word, locations.join(','));
  throw new Error('Reading words without a definition: ' + missing.size);
}
write('reading-lexicon.js', 'window.READING_LEXICON=' + JSON.stringify(lexicon) + ';\n');
console.log('Checked', words.length, 'lesson words and', Object.keys(lexicon).length, 'reading definitions; every story character is covered.');
