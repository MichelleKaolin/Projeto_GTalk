let isDark=true,isRec=false,recInterval=null,recSecs=0,isPlaying=false;

function goPage(id){document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));document.getElementById(id).classList.add('active');}
function goAuth(tab){goPage('auth');switchT(tab);}
function login(){goPage('dashboard');toast('🎉 Bem-vindo ao GTalk!');}
function switchT(t){
  document.getElementById('f-login').style.display=t==='login'?'block':'none';
  document.getElementById('f-signup').style.display=t==='signup'?'block':'none';
  document.getElementById('t-login').classList.toggle('active',t==='login');
  document.getElementById('t-signup').classList.toggle('active',t==='signup');
}
function toggleTheme(){isDark=!isDark;document.body.classList.toggle('light',!isDark);document.querySelectorAll('.theme-btn').forEach(b=>b.textContent=isDark?'🌙':'☀️');}
function sv(v){document.querySelectorAll('.view').forEach(d=>d.classList.remove('active'));document.querySelectorAll('.ni').forEach(n=>n.classList.remove('active'));document.getElementById('v-'+v).classList.add('active');}
function toggleRec(){
  isRec=!isRec;
  const btn=document.getElementById('recBtn');const status=document.getElementById('recStatus');
  if(isRec){btn.classList.add('recording');btn.textContent='⏹';status.textContent='Gravando...';
    recInterval=setInterval(()=>{recSecs++;document.getElementById('recTime').textContent=`${String(Math.floor(recSecs/60)).padStart(2,'0')}:${String(recSecs%60).padStart(2,'0')}`;updateWaveBig(true);},1000);}
  else{btn.classList.remove('recording');btn.textContent='🎙️';status.textContent='Transcrevendo...';
    clearInterval(recInterval);recSecs=0;document.getElementById('recTime').textContent='00:00';
    setTimeout(()=>{status.textContent='Clique para gravar';updateWaveBig(false);toast('✅ Transcrição concluída e salva!');},2000);}
}
function updateWaveBig(active){const c=document.getElementById('waveBig');c.innerHTML='';for(let i=0;i<24;i++){const b=document.createElement('div');b.className='wb'+(active?' active':'');const h=active?(Math.random()*35+8):8;b.style.cssText=`height:${h}px;--h:${h}px;animation-delay:${i*0.05}s`;c.appendChild(b);}}

function startTTS(){isPlaying=true;document.getElementById('playingInd').classList.add('visible');toast('🔊 Reproduzindo com GeniVoice...');}
function stopTTS(){isPlaying=false;document.getElementById('playingInd').classList.remove('visible');}

function toast(msg){const t=document.createElement('div');t.className='toast';t.textContent=msg;document.getElementById('toasts').appendChild(t);setTimeout(()=>t.remove(),3000);}

// Landing bars animation
function initBars(){const c=document.getElementById('landingBars');c.innerHTML='';for(let i=0;i<32;i++){const b=document.createElement('div');b.className='bar';const h=Math.floor(Math.random()*40)+8;b.style.cssText=`height:${h}px;--h:${h}px;animation-delay:${(i*0.08).toFixed(2)}s`;c.appendChild(b);}
const av=document.getElementById('authViz');if(av){av.innerHTML='';const colors=['#00D9B5','#8B5CF6','#FF4081','#FFB300','#00B4D8'];for(let i=0;i<16;i++){const b=document.createElement('div');b.className='av-bar';const h=Math.floor(Math.random()*60)+20;b.style.cssText=`height:${h}px;background:${colors[i%colors.length]};width:8px;border-radius:4px;animation-delay:${(i*0.1).toFixed(1)}s`;av.appendChild(b);}}}
initBars();document.getElementById('waveBig').innerHTML='';
document.querySelector('.speed-control input').addEventListener('input',function(){document.getElementById('speedVal').textContent=parseFloat(this.value).toFixed(1)+'x';});
