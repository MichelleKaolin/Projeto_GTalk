/* GTalk Frontend — API Integration */
const API_BASE = window.GTALK_API_URL || 'http://localhost:8000';
let isDark = true, isRec = false, recInterval = null, recSecs = 0, isPlaying = false;
let authToken = localStorage.getItem('gtalk_token');
let currentUser = null;

/* ── Helpers ─────────────────────────────────────────────────────────────── */

function escapeHTML(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}

async function apiFetch(path, options = {}) {
  const headers = options.headers || {};
  if (authToken) headers['Authorization'] = 'Bearer ' + authToken;
  if (options.body && typeof options.body === 'object') {
    headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(options.body);
  }
  const res = await fetch(API_BASE + '/api' + path, { ...options, headers });
  if (res.status === 401) { doLogout(); throw new Error('Session expired'); }
  if (res.status === 204) return null;
  return res;
}

function toast(msg) {
  const t = document.createElement('div');
  t.className = 'toast';
  t.textContent = msg;
  document.getElementById('toasts').appendChild(t);
  setTimeout(() => t.remove(), 3000);
}

function formatDuration(secs) {
  if (!secs) return '';
  const h = Math.floor(secs / 3600);
  const m = Math.floor((secs % 3600) / 60);
  return h > 0 ? h + 'h' + m + 'min' : m + 'min';
}

function formatRelativeDate(iso) {
  const d = new Date(iso);
  const now = new Date();
  const diffMs = now - d;
  const diffDays = Math.floor(diffMs / 86400000);
  if (diffDays === 0) return 'Hoje, ' + d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  if (diffDays === 1) return 'Ontem, ' + d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  return diffDays + ' dias atras';
}

/* ── Navigation ──────────────────────────────────────────────────────────── */

function goPage(id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  if (id === 'dashboard' && authToken) loadDashboardData();
}

function goAuth(tab) { goPage('auth'); switchT(tab); }

function switchT(t) {
  document.getElementById('f-login').style.display = t === 'login' ? 'block' : 'none';
  document.getElementById('f-signup').style.display = t === 'signup' ? 'block' : 'none';
  document.getElementById('t-login').classList.toggle('active', t === 'login');
  document.getElementById('t-signup').classList.toggle('active', t === 'signup');
}

function toggleTheme() {
  isDark = !isDark;
  document.body.classList.toggle('light', !isDark);
  document.querySelectorAll('.theme-btn').forEach(b => b.textContent = isDark ? '\u{1F319}' : '\u{2600}\u{FE0F}');
}

function sv(v) {
  document.querySelectorAll('.view').forEach(d => d.classList.remove('active'));
  document.querySelectorAll('.ni').forEach(n => n.classList.remove('active'));
  const el = document.getElementById('v-' + v);
  if (el) el.classList.add('active');
  if (v === 'home') loadDashboardData();
  if (v === 'transcricoes') loadTranscriptionsList();
}

/* ── Auth ─────────────────────────────────────────────────────────────────── */

async function login() {
  const email = document.getElementById('login-email').value;
  const password = document.getElementById('login-password').value;
  if (!email || !password) { toast('Preencha email e senha'); return; }
  try {
    const res = await fetch(API_BASE + '/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json();
      toast(err.detail || 'Erro ao fazer login');
      return;
    }
    const data = await res.json();
    authToken = data.access_token;
    currentUser = data.user;
    localStorage.setItem('gtalk_token', authToken);
    localStorage.setItem('gtalk_user', JSON.stringify(currentUser));
    goPage('dashboard');
    updateUserUI();
    toast('Bem-vindo ao GTalk, ' + currentUser.name + '!');
  } catch (e) {
    toast('Erro de conexao com o servidor');
  }
}

async function signup() {
  const name = document.getElementById('signup-name').value;
  const email = document.getElementById('signup-email').value;
  const password = document.getElementById('signup-password').value;
  if (!name || !email || !password) { toast('Preencha todos os campos'); return; }
  if (password.length < 8) { toast('Senha deve ter no minimo 8 caracteres'); return; }
  try {
    const res = await fetch(API_BASE + '/api/auth/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password }),
    });
    if (!res.ok) {
      const err = await res.json();
      toast(err.detail || 'Erro ao criar conta');
      return;
    }
    const data = await res.json();
    authToken = data.access_token;
    currentUser = data.user;
    localStorage.setItem('gtalk_token', authToken);
    localStorage.setItem('gtalk_user', JSON.stringify(currentUser));
    goPage('dashboard');
    updateUserUI();
    toast('Conta criada! Bem-vindo, ' + currentUser.name + '!');
  } catch (e) {
    toast('Erro de conexao com o servidor');
  }
}

function doLogout() {
  if (authToken) {
    fetch(API_BASE + '/api/auth/logout', {
      method: 'POST',
      headers: { 'Authorization': 'Bearer ' + authToken },
    }).catch(() => {});
  }
  authToken = null;
  currentUser = null;
  localStorage.removeItem('gtalk_token');
  localStorage.removeItem('gtalk_user');
  goPage('landing');
}

function updateUserUI() {
  const avatarEls = document.querySelectorAll('.avatar');
  if (currentUser) {
    const initial = currentUser.name.charAt(0).toUpperCase();
    avatarEls.forEach(el => el.textContent = initial);
    const nameEl = document.getElementById('user-greeting');
    if (nameEl) nameEl.textContent = 'Ola, ' + currentUser.name.split(' ')[0] + '!';
  }
}

/* ── Dashboard Data ──────────────────────────────────────────────────────── */

async function loadDashboardData() {
  try {
    const res = await apiFetch('/dashboard/overview?days=30');
    if (!res) return;
    const data = await res.json();
    const s = data.stats;
    const el1 = document.getElementById('stat-transcriptions');
    if (el1) el1.textContent = s.total_transcriptions;
    const el2 = document.getElementById('stat-hours');
    if (el2) el2.textContent = s.total_hours_recorded + 'h';
    const el3 = document.getElementById('stat-tts');
    if (el3) el3.textContent = s.total_texts_read;
    const el4 = document.getElementById('stat-words');
    if (el4) el4.textContent = s.total_words_transcribed;
    // Render recent transcriptions
    const recentEl = document.getElementById('recent-list');
    if (recentEl && data.recent_transcriptions) {
      recentEl.innerHTML = data.recent_transcriptions.slice(0, 5).map(t => `
        <div class="tr-card fu">
          <div class="tr-header">
            <div class="tr-title">${escapeHTML(t.title)}</div>
            <div class="tr-time">${escapeHTML(formatRelativeDate(t.created_at))}</div>
          </div>
          <div class="tr-text">${escapeHTML(String(t.word_count))} palavras ${t.duration_seconds ? '| ' + escapeHTML(formatDuration(t.duration_seconds)) : ''} | Status: ${escapeHTML(t.status)}</div>
          <div class="tr-actions">
            <button class="ta-btn ta-play" onclick="sv('tts')">&#9654; Ouvir</button>
            <button class="ta-btn ta-quiz" onclick="toast('Quiz gerado no GeniUs!')">&#9889; Gerar Quiz</button>
          </div>
        </div>
      `).join('');
    }
  } catch (e) {
    console.error('Error loading dashboard:', e);
  }
}

/* ── Transcriptions List ─────────────────────────────────────────────────── */

async function loadTranscriptionsList() {
  try {
    const searchEl = document.getElementById('search-transcriptions');
    const search = searchEl ? searchEl.value : '';
    const url = '/transcriptions/?page=1&page_size=50' + (search ? '&search=' + encodeURIComponent(search) : '');
    const res = await apiFetch(url);
    if (!res) return;
    const data = await res.json();
    const listEl = document.getElementById('transcriptions-list');
    if (listEl) {
      listEl.innerHTML = data.items.map(t => `
        <div class="tr-card fu">
          <div class="tr-header">
            <div class="tr-title">${escapeHTML(t.title)}</div>
            <div class="tr-time">${escapeHTML(formatRelativeDate(t.created_at))} ${t.duration_seconds ? '| ' + escapeHTML(formatDuration(t.duration_seconds)) : ''}</div>
          </div>
          <div class="tr-text">${t.transcribed_text ? escapeHTML(t.transcribed_text.substring(0, 200)) + '...' : '(Pendente)'}</div>
          <div class="tr-actions">
            <button class="ta-btn ta-play" onclick="sv('tts')">&#9654; Ouvir</button>
            <button class="ta-btn ta-quiz" onclick="toast('Quiz gerado!')">&#9889; Quiz</button>
            <button class="ta-btn ta-del" onclick="deleteTranscription('${escapeHTML(t.id)}')">&#128465; Remover</button>
          </div>
        </div>
      `).join('');
    }
  } catch (e) {
    console.error('Error loading transcriptions:', e);
  }
}

async function deleteTranscription(id) {
  try {
    await apiFetch('/transcriptions/' + id, { method: 'DELETE' });
    toast('Transcricao removida');
    loadTranscriptionsList();
  } catch (e) {
    toast('Erro ao remover');
  }
}

/* ── Recording ───────────────────────────────────────────────────────────── */

function toggleRec() {
  isRec = !isRec;
  const btn = document.getElementById('recBtn');
  const status = document.getElementById('recStatus');
  if (isRec) {
    btn.classList.add('recording');
    btn.textContent = '\u23F9';
    status.textContent = 'Gravando...';
    recInterval = setInterval(() => {
      recSecs++;
      document.getElementById('recTime').textContent =
        String(Math.floor(recSecs / 60)).padStart(2, '0') + ':' + String(recSecs % 60).padStart(2, '0');
      updateWaveBig(true);
    }, 1000);
  } else {
    btn.classList.remove('recording');
    btn.textContent = '\u{1F399}\u{FE0F}';
    status.textContent = 'Transcrevendo...';
    clearInterval(recInterval);
    const durationSecs = recSecs;
    recSecs = 0;
    document.getElementById('recTime').textContent = '00:00';
    simulateTranscription(durationSecs).then(() => {
      status.textContent = 'Clique para gravar';
      updateWaveBig(false);
      toast('Transcricao concluida e salva!');
    });
  }
}

async function simulateTranscription(durationSecs) {
  try {
    await apiFetch('/transcriptions/simulate', {
      method: 'POST',
      body: {
        title: 'Gravacao ' + new Date().toLocaleString('pt-BR'),
        text: 'Transcricao simulada de audio gravado com duracao de ' + durationSecs + ' segundos. Este e um conteudo de demonstracao gerado automaticamente pelo GTalk.',
        duration_seconds: durationSecs,
        category: 'Gravacoes',
      },
    });
  } catch (e) {
    console.error('Error simulating transcription:', e);
  }
}

function updateWaveBig(active) {
  const c = document.getElementById('waveBig');
  c.innerHTML = '';
  for (let i = 0; i < 24; i++) {
    const b = document.createElement('div');
    b.className = 'wb' + (active ? ' active' : '');
    const h = active ? (Math.random() * 35 + 8) : 8;
    b.style.cssText = 'height:' + h + 'px;--h:' + h + 'px;animation-delay:' + (i * 0.05) + 's';
    c.appendChild(b);
  }
}

/* ── TTS (GeniVoice) ─────────────────────────────────────────────────────── */

async function startTTS() {
  const text = document.getElementById('ttsText').value;
  if (!text.trim()) { toast('Digite ou cole um texto'); return; }
  const voiceSelect = document.querySelector('.voice-select');
  const voiceMap = { 0: 'female_pt_br', 1: 'male_pt_br', 2: 'child_pt_br' };
  const voice = voiceMap[voiceSelect.selectedIndex] || 'female_pt_br';
  const speed = parseFloat(document.querySelector('.speed-control input').value) || 1.0;

  isPlaying = true;
  document.getElementById('playingInd').classList.add('visible');
  toast('Reproduzindo com GeniVoice...');

  try {
    await apiFetch('/tts/', {
      method: 'POST',
      body: { input_text: text, voice: voice, speed: speed },
    });
  } catch (e) {
    console.error('TTS error:', e);
  }
}

function stopTTS() {
  isPlaying = false;
  document.getElementById('playingInd').classList.remove('visible');
}

/* ── Landing Bars ────────────────────────────────────────────────────────── */

function initBars() {
  const c = document.getElementById('landingBars');
  c.innerHTML = '';
  for (let i = 0; i < 32; i++) {
    const b = document.createElement('div');
    b.className = 'bar';
    const h = Math.floor(Math.random() * 40) + 8;
    b.style.cssText = 'height:' + h + 'px;--h:' + h + 'px;animation-delay:' + (i * 0.08).toFixed(2) + 's';
    c.appendChild(b);
  }
  const av = document.getElementById('authViz');
  if (av) {
    av.innerHTML = '';
    const colors = ['#00D9B5', '#8B5CF6', '#FF4081', '#FFB300', '#00B4D8'];
    for (let i = 0; i < 16; i++) {
      const b = document.createElement('div');
      b.className = 'av-bar';
      const h = Math.floor(Math.random() * 60) + 20;
      b.style.cssText = 'height:' + h + 'px;background:' + colors[i % colors.length] + ';width:8px;border-radius:4px;animation-delay:' + (i * 0.1).toFixed(1) + 's';
      av.appendChild(b);
    }
  }
}

/* ── Init ─────────────────────────────────────────────────────────────────── */

initBars();
document.getElementById('waveBig').innerHTML = '';
document.querySelector('.speed-control input').addEventListener('input', function () {
  document.getElementById('speedVal').textContent = parseFloat(this.value).toFixed(1) + 'x';
});

// Auto-login if token exists
if (authToken) {
  const stored = localStorage.getItem('gtalk_user');
  if (stored) currentUser = JSON.parse(stored);
  goPage('dashboard');
  updateUserUI();
}
