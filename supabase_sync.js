// Cross-device study progress. Requires the study_progress_items table and Supabase Auth.
const SUPABASE_URL = 'https://wuzxduexpjviysgihnxm.supabase.co';
const SUPABASE_KEY = 'sb_publishable_aBiJFgTYb9muvE2x0dMh9w_ZvZe-jLn';
const supabaseClient = typeof supabase === 'undefined' ? null : supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
const SYNC_PENDING_KEY = 'hsk4_sync_pending_v2';
const SYNC_MEMORY_KEY = 'hsk4_memory_lab_v1';
const SYNC_DAYS = ['1','2','3','4','5','6','6.1','7','8','9','10','11'];
let syncUser = null;
let cloudReady = false;
let syncSnapshot = {};
let syncPending = readJSON(SYNC_PENDING_KEY, {});
let syncFlushPromise = null;
let syncPullPromise = null;
let syncStatus = 'local';

function readJSON(key, fallback) {
    try { return JSON.parse(localStorage.getItem(key) || '') || fallback; }
    catch (_) { return fallback; }
}
function dayStorageKey(day) { return `hsk4_day${day.replace('.', '_')}_mastered`; }
function vocabularyByDay() {
    const map = new Map();
    for (const word of (window.HSK4_VOCAB || [])) {
        if (!map.has(word.day)) map.set(word.day, new Set());
        map.get(word.day).add(word.h);
    }
    return map;
}
function migrateLegacyMastery() {
    if (localStorage.getItem('hsk4_legacy_mastery_migrated_v2') === '1') return;
    const known = vocabularyByDay();
    for (const day of ['1','2','3','4','5']) {
        const legacy = readJSON(`superchinese_hsk4_l${day}_mastered`, []);
        if (!Array.isArray(legacy) || !legacy.length) continue;
        const canonical = new Set(readJSON(dayStorageKey(day), []));
        for (const hanzi of legacy) if (known.get(day)?.has(hanzi)) canonical.add(hanzi);
        localStorage.setItem(dayStorageKey(day), JSON.stringify([...canonical]));
    }
    localStorage.setItem('hsk4_legacy_mastery_migrated_v2', '1');
}
function collectProgress() {
    const items = {};
    const known = vocabularyByDay();
    for (const day of SYNC_DAYS) {
        const saved = new Set(readJSON(dayStorageKey(day), []));
        for (const hanzi of (known.get(day) || [])) items[`master:${day}:${hanzi}`] = saved.has(hanzi);
    }
    const memory = readJSON(SYNC_MEMORY_KEY, {});
    for (const [id, value] of Object.entries(memory)) {
        if (/^(?:\d+(?:\.1)?)\|\d+$/.test(id) && value && typeof value === 'object') items[`memory:${id}`] = value;
    }
    items['speed:weak'] = readJSON('hsk4_game_weak_words', []);
    items['speed:score'] = Number(localStorage.getItem('hsk4_game_high_score') || 0);
    return items;
}
function isMeaningful(value) {
    if (value === true) return true;
    if (typeof value === 'number') return value > 0;
    if (Array.isArray(value)) return value.length > 0;
    return !!(value && typeof value === 'object' && Number(value.seen) > 0);
}
function applyCloudItems(changes) {
    const known = vocabularyByDay();
    const mastery = new Map();
    for (const day of SYNC_DAYS) mastery.set(day, new Set(readJSON(dayStorageKey(day), [])));
    const memory = readJSON(SYNC_MEMORY_KEY, {});
    let changed = false;
    for (const [key, value] of Object.entries(changes)) {
        if (key.startsWith('master:')) {
            const match = /^master:([^:]+):(.+)$/.exec(key);
            if (!match || !known.get(match[1])?.has(match[2])) continue;
            const set = mastery.get(match[1]);
            if (value === true && !set.has(match[2])) { set.add(match[2]); changed = true; }
            if (value === false && set.has(match[2])) { set.delete(match[2]); changed = true; }
        } else if (key.startsWith('memory:')) {
            const id = key.slice(7);
            if (!/^(?:\d+(?:\.1)?)\|\d+$/.test(id) || !value || typeof value !== 'object') continue;
            if (JSON.stringify(memory[id]) !== JSON.stringify(value)) { memory[id] = value; changed = true; }
        } else if (key === 'speed:weak' && Array.isArray(value)) {
            if (JSON.stringify(readJSON('hsk4_game_weak_words', [])) !== JSON.stringify(value)) {
                localStorage.setItem('hsk4_game_weak_words', JSON.stringify(value)); changed = true;
            }
        } else if (key === 'speed:score' && Number.isFinite(Number(value))) {
            const highest = Math.max(Number(value), Number(localStorage.getItem('hsk4_game_high_score') || 0));
            if (highest !== Number(localStorage.getItem('hsk4_game_high_score') || 0)) {
                localStorage.setItem('hsk4_game_high_score', String(highest)); changed = true;
            }
        }
    }
    if (changed) {
        for (const [day, set] of mastery) localStorage.setItem(dayStorageKey(day), JSON.stringify([...set]));
        localStorage.setItem(SYNC_MEMORY_KEY, JSON.stringify(memory));
        window.dispatchEvent(new CustomEvent('hsk4:cloud-updated'));
    }
    return changed;
}
function queueLocalChanges() {
    const current = collectProgress();
    const timestamp = new Date().toISOString();
    for (const [key, value] of Object.entries(current)) {
        if (JSON.stringify(value) !== JSON.stringify(syncSnapshot[key])) syncPending[key] = { value, updated_at: timestamp };
    }
    syncSnapshot = current;
    localStorage.setItem(SYNC_PENDING_KEY, JSON.stringify(syncPending));
}
async function flushPending() {
    if (!cloudReady || !syncUser || !supabaseClient) return;
    if (syncFlushPromise) return syncFlushPromise;
    syncFlushPromise = (async () => {
        while (Object.keys(syncPending).length) {
            const batch = { ...syncPending };
            const rows = Object.entries(batch).map(([item_key, entry]) => ({
                user_id: syncUser.id, item_key, value: entry.value, updated_at: entry.updated_at
            }));
            const { error } = await supabaseClient.from('study_progress_items').upsert(rows, { onConflict: 'user_id,item_key' });
            if (error) { syncStatus = 'error'; updateSyncBadgeUI(); console.warn('Study sync:', error.message); return; }
            for (const [itemKey, entry] of Object.entries(batch)) {
                if (JSON.stringify(syncPending[itemKey]) === JSON.stringify(entry)) delete syncPending[itemKey];
            }
            localStorage.setItem(SYNC_PENDING_KEY, JSON.stringify(syncPending));
        }
        syncStatus = 'synced'; updateSyncBadgeUI();
    })();
    try { await syncFlushPromise; } finally { syncFlushPromise = null; }
}
async function syncToCloud() {
    queueLocalChanges();
    await flushPending();
}
async function syncFromCloud() {
    if (!supabaseClient) { syncStatus = 'offline'; updateSyncBadgeUI(); return; }
    if (syncPullPromise) return syncPullPromise;
    syncPullPromise = (async () => {
        const { data: userData, error: userError } = await supabaseClient.auth.getUser();
        if (userError || !userData?.user) {
            syncUser = null; cloudReady = false;
            syncStatus = userError && userError.name !== 'AuthSessionMissingError' ? 'offline' : 'local';
            updateSyncBadgeUI(); return;
        }
        syncUser = userData.user;
        syncStatus = 'syncing'; updateSyncBadgeUI();
        const { data, error } = await supabaseClient.from('study_progress_items')
            .select('item_key,value,updated_at').eq('user_id', syncUser.id);
        if (error) { syncStatus = 'error'; updateSyncBadgeUI(); console.warn('Study sync:', error.message); return; }
        const remote = new Map((data || []).map(row => [row.item_key, row]));
        const changes = {};
        for (const [key, row] of remote) {
            const localChange = syncPending[key];
            if (!localChange || localChange.updated_at < row.updated_at) {
                changes[key] = row.value;
                if (localChange) delete syncPending[key];
            }
        }
        applyCloudItems(changes);
        syncSnapshot = collectProgress();
        const timestamp = new Date().toISOString();
        for (const [key, value] of Object.entries(syncSnapshot)) {
            if (!remote.has(key) && isMeaningful(value) && !syncPending[key]) syncPending[key] = { value, updated_at: timestamp };
        }
        localStorage.setItem(SYNC_PENDING_KEY, JSON.stringify(syncPending));
        cloudReady = true;
        await flushPending();
        if (syncStatus !== 'error') { syncStatus = 'synced'; updateSyncBadgeUI(); }
    })();
    try { await syncPullPromise; } finally { syncPullPromise = null; }
}
function updateSyncBadgeUI() {
    const badge = document.getElementById('syncBadgeBtn');
    const labels = { local:'☁️ เข้าสู่ระบบเพื่อซิงก์', offline:'☁️ ออฟไลน์ · เก็บในเครื่อง', syncing:'☁️ กำลังซิงก์…', synced:'☁️ ซิงก์แล้ว', error:'⚠️ ซิงก์ไม่สำเร็จ' };
    if (badge) { badge.textContent = labels[syncStatus] || labels.local; badge.title = syncUser?.email || 'กดเพื่อตั้งค่าการซิงก์ข้ามเครื่อง'; }
    const status = document.getElementById('cloudDialogStatus');
    if (status) status.textContent = syncUser ? `${syncUser.email} · ${labels[syncStatus]}` : labels[syncStatus];
}
function promptChangeUserKey() { showCloudDialog(); }
async function importLegacyCloudProgress() {
    if (!syncUser || !supabaseClient) return;
    const legacyKey = prompt('ชื่อผู้ใช้ Cloud เดิมที่ต้องการนำเข้าความจำ', 'patipat')?.trim();
    if (!legacyKey) return;
    const status = document.getElementById('cloudDialogStatus');
    status.textContent = 'กำลังนำเข้าความจำเดิม…';
    const { data, error } = await supabaseClient.from('user_progress')
        .select('mastered_words,weak_words,high_score').eq('user_key', legacyKey).maybeSingle();
    if (error || !data) { status.textContent = error ? `นำเข้าไม่สำเร็จ: ${error.message}` : 'ไม่พบชื่อผู้ใช้เดิม'; return; }
    const known = vocabularyByDay();
    const legacyWords = new Set(Array.isArray(data.mastered_words) ? data.mastered_words : []);
    for (const day of SYNC_DAYS) {
        const saved = new Set(readJSON(dayStorageKey(day), []));
        for (const word of (known.get(day) || [])) if (legacyWords.has(word)) saved.add(word);
        localStorage.setItem(dayStorageKey(day), JSON.stringify([...saved]));
    }
    if (Array.isArray(data.weak_words)) localStorage.setItem('hsk4_game_weak_words', JSON.stringify(data.weak_words));
    const highest = Math.max(Number(data.high_score) || 0, Number(localStorage.getItem('hsk4_game_high_score') || 0));
    localStorage.setItem('hsk4_game_high_score', String(highest));
    window.dispatchEvent(new CustomEvent('hsk4:cloud-updated'));
    await syncToCloud();
    status.textContent = syncStatus === 'synced' ? 'นำเข้าความจำเดิมและซิงก์แล้ว' : 'นำเข้าแล้ว ระบบจะซิงก์เมื่อเชื่อมต่อได้';
}
function showCloudDialog() {
    let dialog = document.getElementById('cloudDialog');
    if (!dialog) {
        dialog = document.createElement('dialog'); dialog.id = 'cloudDialog';
        dialog.style.cssText = 'border:1px solid #d8c8ad;border-radius:18px;padding:24px;max-width:min(440px,calc(100vw - 28px));width:100%;box-shadow:0 20px 60px #0004;color:#2b1f1d;font-family:Sarabun,sans-serif';
        const heading = document.createElement('h2'); heading.textContent = '☁️ ซิงก์ความจำข้ามเครื่อง'; heading.style.margin = '0 0 8px';
        const explanation = document.createElement('p'); explanation.textContent = 'ใช้อีเมลเดียวกันทุกเครื่องเพื่อเก็บคำที่จำได้ ผลเกม และรอบทวนล่าสุด';
        const status = document.createElement('p'); status.id = 'cloudDialogStatus'; status.setAttribute('role','status');
        const form = document.createElement('form'); form.id = 'cloudLoginForm';
        const label = document.createElement('label'); label.textContent = 'อีเมล'; label.htmlFor = 'cloudEmail';
        const input = document.createElement('input'); input.id = 'cloudEmail'; input.type = 'email'; input.required = true; input.autocomplete = 'email'; input.placeholder = 'you@example.com'; input.style.cssText = 'display:block;width:100%;padding:10px;margin:6px 0 12px;border:1px solid #c8b99e;border-radius:8px';
        const submit = document.createElement('button'); submit.type = 'submit'; submit.textContent = 'ส่งลิงก์เข้าสู่ระบบ';
        form.append(label,input,submit);
        const actions = document.createElement('div'); actions.style.cssText = 'display:flex;gap:10px;flex-wrap:wrap;margin-top:14px';
        const refresh = document.createElement('button'); refresh.type = 'button'; refresh.textContent = 'ซิงก์ตอนนี้'; refresh.onclick = syncFromCloud;
        const importOld = document.createElement('button'); importOld.type = 'button'; importOld.id = 'cloudImportOld'; importOld.textContent = 'นำเข้าความจำ Cloud เดิม'; importOld.onclick = importLegacyCloudProgress;
        const signout = document.createElement('button'); signout.type = 'button'; signout.textContent = 'ออกจากระบบ';
        signout.onclick = async () => { if (supabaseClient) await supabaseClient.auth.signOut(); syncUser = null; cloudReady = false; syncStatus = 'local'; updateSyncBadgeUI(); updateDialog(); };
        const close = document.createElement('button'); close.type = 'button'; close.textContent = 'ปิด'; close.onclick = () => dialog.close();
        actions.append(refresh,importOld,signout,close);
        form.onsubmit = async event => {
            event.preventDefault();
            if (!supabaseClient) { status.textContent = 'ไม่สามารถโหลด Supabase ได้ กรุณาตรวจอินเทอร์เน็ต'; return; }
            if (!/^https?:$/.test(location.protocol)) { status.textContent = 'กรุณาเปิดเว็บไซต์ออนไลน์เพื่อเข้าสู่ระบบ'; return; }
            submit.disabled = true; status.textContent = 'กำลังส่งลิงก์…';
            const { error } = await supabaseClient.auth.signInWithOtp({ email: input.value.trim(), options: { emailRedirectTo: location.href.split('#')[0] } });
            status.textContent = error ? `ส่งไม่สำเร็จ: ${error.message}` : 'ส่งลิงก์แล้ว กรุณาเปิดอีเมลและกดลิงก์บนเครื่องนี้';
            submit.disabled = false;
        };
        dialog.append(heading,explanation,status,form,actions); document.body.append(dialog);
    }
    function updateDialog() {
        document.getElementById('cloudLoginForm').hidden = !!syncUser;
        document.getElementById('cloudImportOld').hidden = !syncUser;
        updateSyncBadgeUI();
    }
    updateDialog(); dialog.showModal();
}

migrateLegacyMastery();
syncSnapshot = collectProgress();
document.addEventListener('DOMContentLoaded', () => {
    updateSyncBadgeUI();
    if (!supabaseClient) { syncStatus = 'offline'; updateSyncBadgeUI(); return; }
    setTimeout(syncFromCloud, 300);
    supabaseClient.auth.onAuthStateChange((event) => {
        if (event === 'SIGNED_IN') setTimeout(syncFromCloud, 0);
        if (event === 'SIGNED_OUT') { syncUser = null; cloudReady = false; syncStatus = 'local'; updateSyncBadgeUI(); }
    });
    setInterval(() => { if (document.visibilityState === 'visible' && syncUser) syncFromCloud(); }, 30000);
    window.addEventListener('online', syncFromCloud);
});
