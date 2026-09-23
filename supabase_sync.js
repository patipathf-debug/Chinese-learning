// Supabase Sync Helper for SuperChinese HSK4
const SUPABASE_URL = 'https://wuzxduexpjviysgihnxm.supabase.co';
const SUPABASE_KEY = 'sb_publishable_aBiJFgTYb9muvE2x0dMh9w_ZvZe-jLn';
let supabaseClient = null;

if (typeof supabase !== 'undefined') {
    supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
}

function getActiveUserKey() {
    let key = localStorage.getItem('hsk4_user_key');
    if (!key) {
        key = 'patipat';
        localStorage.setItem('hsk4_user_key', key);
    }
    return key;
}

function setActiveUserKey(newKey) {
    if (newKey && newKey.trim()) {
        localStorage.setItem('hsk4_user_key', newKey.trim());
        syncFromCloud();
    }
}

async function syncToCloud() {
    if (!supabaseClient) return;
    const userKey = getActiveUserKey();
    
    // Collect all mastered words across days
    let allMastered = new Set();
    try {
        for (let i = 1; i <= 10; i++) {
            let m = JSON.parse(localStorage.getItem(`hsk4_day${i}_mastered`) || '[]');
            m.forEach(x => allMastered.add(x));
        }
        let m61 = JSON.parse(localStorage.getItem('hsk4_day6_1_mastered') || '[]');
        m61.forEach(x => allMastered.add(x));
    } catch(e) {}
    
    let weakWords = [];
    try {
        weakWords = JSON.parse(localStorage.getItem('hsk4_game_weak_words') || '[]');
    } catch(e) {}
    
    let highScore = parseInt(localStorage.getItem('hsk4_game_high_score') || '0');

    try {
        const { data, error } = await supabaseClient
            .from('user_progress')
            .upsert({
                user_key: userKey,
                mastered_words: Array.from(allMastered),
                weak_words: weakWords,
                high_score: highScore,
                updated_at: new Date().toISOString()
            }, { onConflict: 'user_key' });
            
        if (!error) {
            updateSyncBadgeUI(true);
        }
    } catch(e) {
        console.warn('Cloud sync error:', e);
    }
}

async function syncFromCloud() {
    if (!supabaseClient) return;
    const userKey = getActiveUserKey();
    
    try {
        const { data, error } = await supabaseClient
            .from('user_progress')
            .select('*')
            .eq('user_key', userKey)
            .single();
            
        if (data) {
            if (data.mastered_words && Array.isArray(data.mastered_words)) {
                // Group mastered words by day if possible or store globally
                let masteredSet = new Set(data.mastered_words);
                // Save to localStorage
                for (let i = 1; i <= 10; i++) {
                    let current = JSON.parse(localStorage.getItem(`hsk4_day${i}_mastered`) || '[]');
                    let combined = new Set([...current, ...data.mastered_words]);
                    localStorage.setItem(`hsk4_day${i}_mastered`, JSON.stringify(Array.from(combined)));
                }
                let current61 = JSON.parse(localStorage.getItem('hsk4_day6_1_mastered') || '[]');
                let combined61 = new Set([...current61, ...data.mastered_words]);
                localStorage.setItem('hsk4_day6_1_mastered', JSON.stringify(Array.from(combined61)));
            }
            
            if (data.weak_words && Array.isArray(data.weak_words)) {
                localStorage.setItem('hsk4_game_weak_words', JSON.stringify(data.weak_words));
            }
            
            if (typeof data.high_score === 'number') {
                let currentHigh = parseInt(localStorage.getItem('hsk4_game_high_score') || '0');
                if (data.high_score > currentHigh) {
                    localStorage.setItem('hsk4_game_high_score', data.high_score.toString());
                }
            }
            
            updateSyncBadgeUI(true);
            if (typeof updateMasteredCounts === 'function') updateMasteredCounts();
            if (typeof updateGlobalStats === 'function') updateGlobalStats();
            if (typeof renderVocab === 'function') renderVocab();
        }
    } catch(e) {
        console.warn('Fetch sync error:', e);
    }
}

function updateSyncBadgeUI(success = true) {
    const el = document.getElementById('syncBadgeBtn');
    if (el) {
        const key = getActiveUserKey();
        el.innerHTML = `☁️ ซิงก์ Cloud แล้ว (${key})`;
        el.style.borderColor = 'var(--gold)';
    }
}

function promptChangeUserKey() {
    const current = getActiveUserKey();
    const input = prompt('กรอกชื่อผู้ใช้สำหรับซิงก์ข้อมูลข้ามเครื่อง (เช่น patipat):', current);
    if (input && input.trim() && input.trim() !== current) {
        setActiveUserKey(input.trim());
        alert(`เปลี่ยนผู้ใช้เป็น "${input.trim()}" และดึงข้อมูลแล้ว!`);
        location.reload();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    setTimeout(syncFromCloud, 500);
});
