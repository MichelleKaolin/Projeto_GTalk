"""Dashboard HTML views served by the backend."""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Dashboard Views"])

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GTalk Dashboard — Analytics</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Fraunces:wght@400;700;900&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<style>
:root{
  --teal:#00D9B5;--purple:#8B5CF6;--pink:#FF4081;--amber:#FFB300;--sky:#00B4D8;
  --bg:#060612;--bg2:#0D0D20;--bg3:#141428;--card:#18182E;--border:rgba(255,255,255,0.07);
  --text:#EEF0FF;--text2:#8890BB;--text3:#404466;
  --radius:18px;--shadow:0 12px 50px rgba(0,0,0,0.5);
}
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Space Grotesk',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;}
body::before{content:'';position:fixed;inset:0;background:radial-gradient(ellipse 800px 600px at 80% 20%,rgba(0,217,181,.07) 0%,transparent 60%),radial-gradient(ellipse 600px 600px at 20% 80%,rgba(139,92,246,.07) 0%,transparent 60%);pointer-events:none;z-index:0;}

.topbar{display:flex;align-items:center;justify-content:space-between;padding:16px 32px;background:var(--bg2);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100;}
.logo{font-family:'Fraunces',sans-serif;font-size:22px;font-weight:900;letter-spacing:-1px;}
.logo .g{color:var(--teal);}
.topbar-info{display:flex;align-items:center;gap:16px;color:var(--text2);font-size:14px;}

.container{max-width:1200px;margin:0 auto;padding:32px;position:relative;z-index:1;}

.page-title{font-family:'Fraunces',sans-serif;font-size:32px;font-weight:900;margin-bottom:8px;}
.page-sub{color:var(--text2);font-size:16px;margin-bottom:32px;}

/* Auth form */
.auth-box{max-width:400px;margin:80px auto;background:var(--card);border:1px solid var(--border);border-radius:24px;padding:40px;text-align:center;}
.auth-box h2{font-family:'Fraunces',sans-serif;font-size:24px;margin-bottom:8px;}
.auth-box p{color:var(--text2);font-size:14px;margin-bottom:24px;}
.auth-box input{width:100%;padding:14px 18px;border-radius:12px;border:1.5px solid var(--border);background:var(--bg3);color:var(--text);font-family:'Space Grotesk',sans-serif;font-size:15px;outline:none;margin-bottom:14px;}
.auth-box input:focus{border-color:var(--teal);}
.auth-box button{width:100%;padding:14px;font-size:16px;font-weight:700;border-radius:12px;background:linear-gradient(135deg,var(--teal),var(--sky));color:#000;border:none;cursor:pointer;margin-top:8px;}
.auth-box button:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,217,181,.4);}
.auth-box .hint{margin-top:16px;color:var(--text3);font-size:13px;}

/* Stats grid */
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin-bottom:32px;}
.stat{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:24px;transition:all .3s;}
.stat:hover{transform:translateY(-3px);box-shadow:var(--shadow);}
.stat-label{font-size:12px;font-weight:600;color:var(--text2);text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px;}
.stat-val{font-family:'Fraunces',sans-serif;font-size:32px;font-weight:900;}
.c-teal{color:var(--teal);}
.c-purple{color:var(--purple);}
.c-pink{color:var(--pink);}
.c-amber{color:var(--amber);}
.c-sky{color:var(--sky);}

/* Charts */
.charts{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:32px;}
@media(max-width:900px){.charts{grid-template-columns:1fr;}}
.chart-card{background:var(--card);border:1px solid var(--border);border-radius:20px;padding:24px;}
.chart-title{font-weight:700;font-size:16px;margin-bottom:16px;}
.chart-wrap{position:relative;height:260px;}

/* Table */
.section-title{font-family:'Fraunces',sans-serif;font-size:22px;font-weight:700;margin-bottom:16px;}
.table-wrap{background:var(--card);border:1px solid var(--border);border-radius:20px;overflow:hidden;margin-bottom:32px;}
table{width:100%;border-collapse:collapse;}
th{text-align:left;padding:14px 20px;font-size:12px;font-weight:700;color:var(--text2);text-transform:uppercase;letter-spacing:.5px;background:var(--bg3);border-bottom:1px solid var(--border);}
td{padding:14px 20px;font-size:14px;border-bottom:1px solid var(--border);}
tr:last-child td{border-bottom:none;}
.badge{display:inline-block;padding:4px 12px;border-radius:50px;font-size:12px;font-weight:600;}
.badge-completed{background:rgba(0,217,181,.15);color:var(--teal);}
.badge-pending{background:rgba(255,179,0,.15);color:var(--amber);}
.badge-failed{background:rgba(255,64,129,.15);color:var(--pink);}
.badge-processing{background:rgba(0,180,216,.15);color:var(--sky);}

.loading{text-align:center;padding:60px;color:var(--text2);font-size:18px;}
.error-msg{text-align:center;padding:40px;color:var(--pink);font-size:16px;}
</style>
</head>
<body>

<div class="topbar">
  <div class="logo"><span class="g">G</span>Talk <span style="color:var(--text2);font-size:14px;font-family:'Space Grotesk';font-weight:400;margin-left:8px;">Analytics Dashboard</span></div>
  <div class="topbar-info">
    <span id="user-name"></span>
    <button onclick="logout()" style="background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:8px 16px;color:var(--text2);cursor:pointer;font-family:'Space Grotesk';font-size:13px;">Sair</button>
  </div>
</div>

<!-- Auth Section -->
<div id="auth-section" style="display:none;">
  <div class="auth-box">
    <h2><span style="color:var(--teal);">G</span>Talk Analytics</h2>
    <p>Entre com sua conta para acessar o dashboard</p>
    <input type="email" id="login-email" placeholder="Email" value="alex@gtalk.demo">
    <input type="password" id="login-password" placeholder="Senha" value="demo1234">
    <button onclick="doLogin()">Entrar</button>
    <div class="hint">Demo: alex@gtalk.demo / demo1234</div>
    <div id="login-error" class="error-msg" style="display:none;padding:12px;"></div>
  </div>
</div>

<!-- Dashboard Section -->
<div id="dashboard-section" style="display:none;">
  <div class="container">
    <div class="page-title">Dashboard de Analytics</div>
    <div class="page-sub">Visao geral do uso de transcricoes e GeniVoice</div>

    <div class="stats" id="stats-grid"></div>

    <div class="charts">
      <div class="chart-card">
        <div class="chart-title">Atividade Diaria (ultimos 30 dias)</div>
        <div class="chart-wrap"><canvas id="dailyChart"></canvas></div>
      </div>
      <div class="chart-card">
        <div class="chart-title">Transcricoes por Categoria</div>
        <div class="chart-wrap"><canvas id="categoryChart"></canvas></div>
      </div>
      <div class="chart-card">
        <div class="chart-title">Status das Transcricoes</div>
        <div class="chart-wrap"><canvas id="statusChart"></canvas></div>
      </div>
      <div class="chart-card">
        <div class="chart-title">Uso de Vozes (GeniVoice)</div>
        <div class="chart-wrap"><canvas id="voiceChart"></canvas></div>
      </div>
    </div>

    <div class="section-title">Transcricoes Recentes</div>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Titulo</th><th>Status</th><th>Palavras</th><th>Duracao</th><th>Data</th></tr></thead>
        <tbody id="recent-table"></tbody>
      </table>
    </div>

    <div class="section-title">Distribuicao de Velocidade (TTS)</div>
    <div class="charts" style="grid-template-columns:1fr;">
      <div class="chart-card">
        <div class="chart-wrap" style="height:200px;"><canvas id="speedChart"></canvas></div>
      </div>
    </div>
  </div>
</div>

<script>
const API = window.location.origin + '/api';
let token = localStorage.getItem('gtalk_token');
let userName = localStorage.getItem('gtalk_user_name');

function showAuth(){ document.getElementById('auth-section').style.display='block'; document.getElementById('dashboard-section').style.display='none'; }
function showDashboard(){ document.getElementById('auth-section').style.display='none'; document.getElementById('dashboard-section').style.display='block'; document.getElementById('user-name').textContent=userName||''; }
function logout(){ localStorage.removeItem('gtalk_token'); localStorage.removeItem('gtalk_user_name'); token=null; showAuth(); }

async function doLogin(){
  const email=document.getElementById('login-email').value;
  const password=document.getElementById('login-password').value;
  const errEl=document.getElementById('login-error');
  errEl.style.display='none';
  try{
    const res=await fetch(API+'/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,password})});
    if(!res.ok){const d=await res.json();throw new Error(d.detail||'Login failed');}
    const data=await res.json();
    token=data.access_token;
    userName=data.user.name;
    localStorage.setItem('gtalk_token',token);
    localStorage.setItem('gtalk_user_name',userName);
    showDashboard();
    loadDashboard();
  }catch(e){errEl.textContent=e.message;errEl.style.display='block';}
}

async function apiFetch(path){
  const res=await fetch(API+path,{headers:{'Authorization':'Bearer '+token}});
  if(res.status===401){logout();throw new Error('Session expired');}
  return res.json();
}

function badgeClass(status){
  return 'badge badge-'+(status||'pending');
}
function formatDuration(secs){
  if(!secs) return '-';
  const h=Math.floor(secs/3600); const m=Math.floor((secs%3600)/60);
  return h>0? h+'h '+m+'min' : m+'min';
}
function formatDate(iso){
  const d=new Date(iso);
  return d.toLocaleDateString('pt-BR',{day:'2-digit',month:'short',year:'numeric'});
}

const COLORS={teal:'#00D9B5',purple:'#8B5CF6',pink:'#FF4081',amber:'#FFB300',sky:'#00B4D8'};

async function loadDashboard(){
  try{
    const [overview, ttsAnalytics] = await Promise.all([
      apiFetch('/dashboard/overview?days=30'),
      apiFetch('/dashboard/tts-analytics?days=30')
    ]);

    // Stats
    const s=overview.stats;
    document.getElementById('stats-grid').innerHTML=`
      <div class="stat"><div class="stat-label">Transcricoes</div><div class="stat-val c-teal">${s.total_transcriptions}</div></div>
      <div class="stat"><div class="stat-label">Horas Gravadas</div><div class="stat-val c-purple">${s.total_hours_recorded}h</div></div>
      <div class="stat"><div class="stat-label">Palavras Transcritas</div><div class="stat-val c-sky">${s.total_words_transcribed.toLocaleString()}</div></div>
      <div class="stat"><div class="stat-label">Textos Lidos (TTS)</div><div class="stat-val c-amber">${s.total_texts_read}</div></div>
      <div class="stat"><div class="stat-label">Caracteres Vocalizados</div><div class="stat-val c-pink">${s.total_chars_vocalized.toLocaleString()}</div></div>
      <div class="stat"><div class="stat-label">Concluidas</div><div class="stat-val c-teal">${s.completed_transcriptions}</div></div>
    `;

    // Daily activity chart
    const daily=overview.daily_activity;
    new Chart(document.getElementById('dailyChart'),{
      type:'bar',
      data:{
        labels:daily.map(d=>d.date.slice(5)),
        datasets:[
          {label:'Transcricoes',data:daily.map(d=>d.transcriptions),backgroundColor:COLORS.teal,borderRadius:6},
          {label:'TTS',data:daily.map(d=>d.tts_requests),backgroundColor:COLORS.purple,borderRadius:6}
        ]
      },
      options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{labels:{color:'#8890BB'}}},scales:{x:{ticks:{color:'#8890BB'},grid:{color:'rgba(255,255,255,0.05)'}},y:{ticks:{color:'#8890BB'},grid:{color:'rgba(255,255,255,0.05)'}}}}
    });

    // Category chart
    const cats=overview.category_breakdown;
    new Chart(document.getElementById('categoryChart'),{
      type:'doughnut',
      data:{labels:cats.map(c=>c.category),datasets:[{data:cats.map(c=>c.count),backgroundColor:[COLORS.teal,COLORS.purple,COLORS.pink,COLORS.amber,COLORS.sky],borderWidth:0}]},
      options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{color:'#8890BB',padding:12}}}}
    });

    // Status chart
    const statuses=overview.transcription_status;
    const statusColors={'completed':COLORS.teal,'pending':COLORS.amber,'processing':COLORS.sky,'failed':COLORS.pink};
    new Chart(document.getElementById('statusChart'),{
      type:'pie',
      data:{labels:statuses.map(s=>s.status),datasets:[{data:statuses.map(s=>s.count),backgroundColor:statuses.map(s=>statusColors[s.status]||'#666'),borderWidth:0}]},
      options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{color:'#8890BB',padding:12}}}}
    });

    // Voice usage chart
    const voices=ttsAnalytics.voice_usage;
    new Chart(document.getElementById('voiceChart'),{
      type:'bar',
      data:{labels:voices.map(v=>v.voice.replace(/_/g,' ')),datasets:[{label:'Requests',data:voices.map(v=>v.count),backgroundColor:COLORS.sky,borderRadius:6},{label:'Chars (k)',data:voices.map(v=>Math.round(v.total_chars/1000)),backgroundColor:COLORS.amber,borderRadius:6}]},
      options:{responsive:true,maintainAspectRatio:false,indexAxis:'y',plugins:{legend:{labels:{color:'#8890BB'}}},scales:{x:{ticks:{color:'#8890BB'},grid:{color:'rgba(255,255,255,0.05)'}},y:{ticks:{color:'#8890BB'},grid:{color:'rgba(255,255,255,0.05)'}}}}
    });

    // Speed distribution chart
    const speeds=ttsAnalytics.speed_distribution;
    new Chart(document.getElementById('speedChart'),{
      type:'bar',
      data:{labels:speeds.map(s=>s.speed_range),datasets:[{label:'Quantidade',data:speeds.map(s=>s.count),backgroundColor:[COLORS.teal,COLORS.purple,COLORS.pink,COLORS.amber],borderRadius:6}]},
      options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{labels:{color:'#8890BB'}}},scales:{x:{ticks:{color:'#8890BB'},grid:{color:'rgba(255,255,255,0.05)'}},y:{ticks:{color:'#8890BB'},grid:{color:'rgba(255,255,255,0.05)'}}}}
    });

    // Recent table
    const tbody=document.getElementById('recent-table');
    tbody.innerHTML=overview.recent_transcriptions.map(t=>`
      <tr>
        <td>${t.title}</td>
        <td><span class="${badgeClass(t.status)}">${t.status}</span></td>
        <td>${t.word_count}</td>
        <td>${formatDuration(t.duration_seconds)}</td>
        <td>${formatDate(t.created_at)}</td>
      </tr>
    `).join('');

  }catch(e){console.error('Dashboard load error:',e);}
}

// Init
if(token){showDashboard();loadDashboard();}else{showAuth();}
</script>
</body>
</html>"""


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_view():
    """Serve the analytics dashboard HTML page."""
    return DASHBOARD_HTML
