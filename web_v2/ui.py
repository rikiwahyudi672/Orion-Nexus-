"""web_v2/ui.py - HTML + CSS + JS untuk web dashboard (TANPA EMOJI)"""
import base64
from pathlib import Path
import sys

BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE))
import core


def get_logo():
    p = Path(core.P["base"]) / "orion.ico"
    if p.exists():
        b64 = base64.b64encode(p.read_bytes()).decode()
        return f"data:image/x-icon;base64,{b64}"
    return ""


HTML = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="theme-color" content="#050816">
<title>ORION v3.0</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
:root{--bg:#050816;--card:rgba(20,30,60,.7);--border:rgba(100,181,246,.25);--primary:#64b5f6;--text:#e0e6ff;--dim:#90a4ae;--ok:#66bb6a;--bad:#ef5350}
html,body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Tahoma,sans-serif;background:var(--bg);color:var(--text);min-height:100vh;overflow-x:hidden}
body::before{content:'';position:fixed;top:0;left:0;width:100%;height:100%;background:radial-gradient(2px 2px at 20% 30%,#64b5f6,transparent),radial-gradient(2px 2px at 60% 70%,#9575cd,transparent),radial-gradient(1px 1px at 50% 50%,#fff,transparent);background-size:200% 200%;animation:stars 60s linear infinite;z-index:-1;opacity:.5}
@keyframes stars{from{background-position:0 0}to{background-position:100% 100%}}
.header{position:sticky;top:0;z-index:100;background:rgba(5,8,22,.85);backdrop-filter:blur(20px);border-bottom:1px solid var(--border);padding:12px 16px;display:flex;align-items:center;justify-content:space-between}
.header-title{font-size:1.2em;font-weight:800;letter-spacing:3px;background:linear-gradient(90deg,#64b5f6,#9575cd);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.header-status{display:flex;align-items:center;gap:6px;font-size:.75em;color:var(--dim)}
.status-dot{width:8px;height:8px;border-radius:50%;background:var(--ok);box-shadow:0 0 8px var(--ok);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
.content{padding:16px;padding-bottom:100px;max-width:800px;margin:0 auto}
.tab{display:none;animation:fade .3s}
.tab.active{display:block}
@keyframes fade{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.status-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:16px}
.status-card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:12px 8px;text-align:center}
.status-card .label{font-size:.65em;color:var(--dim);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px}
.status-card .value{font-size:1.1em;color:var(--primary);font-weight:700}
.card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:16px;margin-bottom:12px}
.card-title{font-size:.85em;color:var(--dim);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:12px;font-weight:600}
.quick-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.btn{background:linear-gradient(135deg,rgba(30,40,70,.8),rgba(20,30,60,.8));border:1px solid var(--border);border-radius:14px;padding:16px 8px;text-align:center;cursor:pointer;transition:all .2s;color:var(--text);font-family:inherit;font-size:.75em;font-weight:600;display:flex;flex-direction:column;align-items:center;gap:6px}
.btn:active{transform:scale(.95);border-color:var(--primary)}
.btn svg{color:var(--primary)}
.btn-full{width:100%;margin-top:8px}
.chat-box{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:12px;height:calc(100vh - 300px);min-height:280px;max-height:500px;overflow-y:auto;margin-bottom:12px}
.msg{margin-bottom:12px}
.msg .who{font-size:.7em;color:var(--dim);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px}
.msg .txt{display:inline-block;padding:10px 14px;border-radius:16px;font-size:.9em;line-height:1.4;max-width:85%;word-wrap:break-word}
.msg.user{text-align:right}
.msg.user .txt{background:linear-gradient(135deg,#64b5f6,#42a5f5);color:#fff;border-bottom-right-radius:4px}
.msg.orion .txt{background:rgba(30,40,70,.9);border:1px solid var(--border);color:var(--text);border-bottom-left-radius:4px;white-space:pre-wrap}
.chat-row{display:flex;gap:8px;align-items:center}
.chat-row input{flex:1;background:var(--card);border:1px solid var(--border);border-radius:24px;padding:12px 18px;color:var(--text);font-family:inherit;font-size:.9em;outline:none}
.chat-row input:focus{border-color:var(--primary)}
.chat-row button{width:46px;height:46px;border-radius:50%;border:none;background:linear-gradient(135deg,#64b5f6,#9575cd);color:#fff;cursor:pointer;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:1.1em}
.chat-row button:active{transform:scale(.9)}
.chat-row button.mic{background:linear-gradient(135deg,#ef5350,#c62828)}
.input-row{display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap}
.input-row input,.input-row select{flex:1;min-width:80px;background:var(--card);border:1px solid var(--border);border-radius:12px;padding:10px 14px;color:var(--text);font-family:inherit;font-size:.9em;outline:none}
.input-row input:focus{border-color:var(--primary)}
.input-row button{background:linear-gradient(135deg,#64b5f6,#9575cd);border:none;border-radius:12px;padding:10px 18px;color:#fff;font-family:inherit;font-size:.85em;font-weight:600;cursor:pointer}
.result{background:rgba(30,40,70,.5);border-radius:12px;padding:12px;margin-top:8px;font-size:.9em;line-height:1.8}
.bar{display:inline-block;height:8px;background:linear-gradient(90deg,#64b5f6,#9575cd);border-radius:4px;margin-right:8px;vertical-align:middle}
.know-list{max-height:400px;overflow-y:auto}
.know-item{background:rgba(30,40,70,.5);border-radius:10px;padding:10px 14px;margin-bottom:8px;font-size:.85em;display:flex;justify-content:space-between;align-items:center;gap:10px}
.know-item .k{color:var(--primary);font-weight:600;flex-shrink:0}
.know-item .v{color:var(--text);text-align:right;word-break:break-word}
.bottom-nav{position:fixed;bottom:0;left:0;right:0;background:rgba(5,8,22,.95);backdrop-filter:blur(20px);border-top:1px solid var(--border);display:flex;justify-content:space-around;padding:8px 0 max(8px,env(safe-area-inset-bottom));z-index:100}
.nav-btn{flex:1;background:none;border:none;color:var(--dim);font-family:inherit;font-size:.65em;cursor:pointer;padding:6px 4px;display:flex;flex-direction:column;align-items:center;gap:2px}
.nav-btn svg{width:24px;height:24px}
.nav-btn.active{color:var(--primary)}
.toast{position:fixed;bottom:90px;left:50%;transform:translateX(-50%) translateY(100px);background:linear-gradient(135deg,#64b5f6,#9575cd);color:#fff;padding:12px 24px;border-radius:24px;font-weight:600;font-size:.85em;opacity:0;transition:all .4s;pointer-events:none;z-index:1000;max-width:90%;text-align:center}
.toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
@media(min-width:768px){.content{padding:24px;padding-bottom:100px}.quick-grid{grid-template-columns:repeat(6,1fr)}}
</style>
</head>
<body>

<div class="header">
<div class="header-title">ORION</div>
<div class="header-status"><div class="status-dot"></div><span>Online</span></div>
</div>

<div class="content">

<div class="tab active" id="tab-home">
<div class="status-grid">
<div class="status-card"><div class="label">CPU</div><div class="value" id="s-cpu">--</div></div>
<div class="status-card"><div class="label">RAM</div><div class="value" id="s-ram">--</div></div>
<div class="status-card"><div class="label">Disk</div><div class="value" id="s-disk">--</div></div>
<div class="status-card"><div class="label">Baterai</div><div class="value" id="s-bat">--</div></div>
</div>
<div class="card">
<div class="card-title">AKSI CEPAT</div>
<div class="quick-grid">
<button class="btn" onclick="aksi('screenshot')">[S] Screenshot</button>
<button class="btn" onclick="aksi('lock')">[L] Lock PC</button>
<button class="btn" onclick="aksi('notepad')">[N] Notepad</button>
<button class="btn" onclick="aksi('browser')">[B] Browser</button>
<button class="btn" onclick="aksi('volume_up')">[V+] Vol +</button>
<button class="btn" onclick="aksi('volume_down')">[V-] Vol -</button>
</div>
</div>
</div>

<div class="tab" id="tab-chat">
<div class="chat-box" id="chat-box">
<div class="msg orion"><div class="who">Orion</div><div class="txt">Halo bos! Ketik atau tekan tombol mic buat ngomong.</div></div>
</div>
<div class="chat-row">
<input type="text" id="chat-input" placeholder="Ketik pesan..." autocomplete="off">
<button class="mic" id="mic-btn" onclick="toggleMic()">MIC</button>
<button onclick="kirimChat()">KIRIM</button>
</div>
</div>

<div class="tab" id="tab-prediksi">
<div class="card">
<div class="card-title">PREDIKSI AKTIVITAS</div>
<div class="input-row">
<input type="number" id="pred-jam" placeholder="Jam" min="0" max="23" step="0.5" value="8">
<button onclick="prediksi()">Prediksi</button>
</div>
<div id="pred-hasil"></div>
</div>
<div class="card">
<div class="card-title">TOP 3 PREDIKSI</div>
<div class="input-row">
<input type="number" id="top-jam" placeholder="Jam" min="0" max="23" step="0.5" value="19">
<button onclick="topN()">Lihat</button>
</div>
<div id="top-hasil"></div>
</div>
<div class="card">
<div class="card-title">PER HARI</div>
<div class="input-row">
<select id="hari-pilih"><option>Senin</option><option>Selasa</option><option>Rabu</option><option>Kamis</option><option>Jumat</option><option>Sabtu</option><option>Minggu</option></select>
<input type="number" id="hari-jam" placeholder="Jam" min="0" max="23" step="0.5" value="8">
<button onclick="perHari()">Lihat</button>
</div>
<div id="hari-hasil"></div>
</div>
</div>

<div class="tab" id="tab-knowledge">
<div class="card">
<div class="card-title">INGAT FAKTA</div>
<div class="input-row">
<input type="text" id="fakta-key" placeholder="Key">
<input type="text" id="fakta-val" placeholder="Value">
<button onclick="simpanFakta()">Simpan</button>
</div>
</div>
<div class="card">
<div class="card-title">DAFTAR FAKTA</div>
<div class="know-list" id="fakta-list"></div>
<button class="btn btn-full" onclick="muatFakta()">Refresh</button>
</div>
<div class="card">
<div class="card-title">CATAT NOTE</div>
<div class="input-row">
<input type="text" id="note-isi" placeholder="Isi catatan...">
<button onclick="simpanNote()">Catat</button>
</div>
</div>
<div class="card">
<div class="card-title">REMINDER</div>
<div class="input-row">
<input type="time" id="rem-jam">
<input type="text" id="rem-pesan" placeholder="Pesan">
<button onclick="simpanReminder()">Set</button>
</div>
<div id="rem-list" style="margin-top:12px"></div>
</div>
</div>

<div class="tab" id="tab-fitur">
<div class="card">
<div class="card-title">CUACA</div>
<div class="input-row">
<input type="text" id="cuaca-kota" placeholder="Kota (default Jakarta)">
<button onclick="muatCuaca()">Cek</button>
</div>
<div id="cuaca-hasil"></div>
</div>
<div class="card">
<div class="card-title">BERITA</div>
<div class="input-row">
<select id="berita-sumber"><option value="detik">Detik</option><option value="kompas">Kompas</option><option value="cnn">CNN</option><option value="tempo">Tempo</option></select>
<button onclick="muatBerita()">Ambil</button>
</div>
<div id="berita-hasil" class="know-list"></div>
</div>
<div class="card">
<div class="card-title">SAHAM</div>
<div class="input-row">
<input type="text" id="saham-kode" placeholder="BBCA.JK" value="BBCA.JK">
<button onclick="muatSaham()">Cek</button>
</div>
<div id="saham-hasil"></div>
</div>
<div class="card">
<div class="card-title">KURS</div>
<button class="btn btn-full" onclick="muatKurs()">Cek Kurs</button>
<div id="kurs-hasil"></div>
</div>
<div class="card">
<div class="card-title">LOG & GRAFIK</div>
<button class="btn btn-full" onclick="muatLog()">Lihat Log</button>
<button class="btn btn-full" onclick="muatGrafik()">Lihat Grafik</button>
<div id="log-hasil"></div>
</div>
</div>

<div class="tab" id="tab-settings">
<div class="card">
<div class="card-title">INFO OTAK</div>
<div id="info-otak">Loading...</div>
</div>
<div class="card">
<div class="card-title">BACKUP</div>
<button class="btn btn-full" onclick="lihatBackup()">Lihat Backup</button>
<div id="backup-list" style="margin-top:12px"></div>
</div>
<div class="card">
<div class="card-title">TENTANG</div>
<div style="font-size:.85em;line-height:1.8;color:var(--dim)">
<div><strong style="color:var(--primary)">ORION</strong> v3.0</div>
<div>Personal AI Assistant</div>
<div>by Riki Wahyudi</div>
<div style="margin-top:8px">Whisper: tiny (offline)</div>
<div>TTS: Supertonic F1</div>
</div>
</div>
</div>

</div>

<div class="bottom-nav">
<button class="nav-btn active" onclick="switchTab('home',this)">Home</button>
<button class="nav-btn" onclick="switchTab('chat',this)">Chat</button>
<button class="nav-btn" onclick="switchTab('prediksi',this)">Prediksi</button>
<button class="nav-btn" onclick="switchTab('knowledge',this)">Ingat</button>
<button class="nav-btn" onclick="switchTab('fitur',this)">Fitur</button>
<button class="nav-btn" onclick="switchTab('settings',this)">Setting</button>
</div>

<div class="toast" id="toast"></div>

<script>
function switchTab(n,b){document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));document.getElementById('tab-'+n).classList.add('active');document.querySelectorAll('.nav-btn').forEach(x=>x.classList.remove('active'));b.classList.add('active');if(n==='knowledge'){muatFakta();muatReminder()}if(n==='settings'){muatInfoOtak()}}
function toast(m){const t=document.getElementById('toast');t.textContent=m;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2500)}
async function updateStatus(){try{const r=await fetch('/api/status');const d=await r.json();document.getElementById('s-cpu').textContent=d.cpu+'%';document.getElementById('s-ram').textContent=d.ram+'%';document.getElementById('s-disk').textContent=d.disk+'%';document.getElementById('s-bat').textContent=d.baterai+'%'}catch(e){}}
async function aksi(c){try{const r=await fetch('/api/'+c,{method:'POST'});const d=await r.json();toast(d.message||'OK')}catch(e){toast('Error')}}
async function kirimChat(){const i=document.getElementById('chat-input');const t=i.value.trim();if(!t)return;i.value='';addMsg('user',t);try{const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pesan:t})});const d=await r.json();addMsg('orion',d.balasan);putarTTS(d.balasan)}catch(e){addMsg('orion','Error')}}
function addMsg(w,t){const b=document.getElementById('chat-box');const d=document.createElement('div');d.className='msg '+w;d.innerHTML='<div class="who">'+(w==='user'?'Lo':'Orion')+'</div><div class="txt">'+esc(t)+'</div>';b.appendChild(d);b.scrollTop=b.scrollHeight}
function esc(s){return s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
document.getElementById('chat-input').addEventListener('keypress',e=>{if(e.key==='Enter')kirimChat()});
let mr=null,chunks=[],rec=false;
async function toggleMic(){const b=document.getElementById('mic-btn');if(!rec){try{const s=await navigator.mediaDevices.getUserMedia({audio:true});mr=new MediaRecorder(s);chunks=[];mr.ondataavailable=e=>chunks.push(e.data);mr.onstop=async()=>{s.getTracks().forEach(t=>t.stop());const bl=new Blob(chunks,{type:'audio/webm'});await kirimVoice(bl)};mr.start();rec=true;b.textContent='STOP';toast('Merekam... tekan lagi')}catch(e){toast('Mic error')}}else{mr.stop();rec=false;b.textContent='MIC';toast('Transkrip...')}}
async function kirimVoice(bl){try{const fd=new FormData();fd.append('audio',bl,'v.webm');const r=await fetch('/api/voice',{method:'POST',body:fd});const d=await r.json();if(d.teks){addMsg('user','Voice: '+d.teks);addMsg('orion',d.balasan);putarTTS(d.balasan)}else toast('Gagal transkrip')}catch(e){toast('Error')}}
function putarTTS(t){try{const a=new Audio('/api/tts?teks='+encodeURIComponent(t)+'&voice=F1');a.play().catch(()=>{})}catch(e){}}
async function prediksi(){const j=document.getElementById('pred-jam').value;const r=await fetch('/api/prediksi?jam='+j,{method:'POST'});const d=await r.json();document.getElementById('pred-hasil').innerHTML='<div class="result">'+d.message+'</div>'}
async function topN(){const j=document.getElementById('top-jam').value;const r=await fetch('/api/topn?jam='+j+'&n=3');const d=await r.json();let h='<div class="result">';d.hasil.forEach((x,i)=>{const w=Math.max(2,x.conf*100);h+='<div><span class="bar" style="width:'+w+'%"></span>'+(i+1)+'. <strong>'+x.aktivitas+'</strong> ('+(x.conf*100).toFixed(1)+'%)</div>'});h+='</div>';document.getElementById('top-hasil').innerHTML=h}
async function perHari(){const h=document.getElementById('hari-pilih').value;const j=document.getElementById('hari-jam').value;const r=await fetch('/api/perhari?hari='+h+'&jam='+j);const d=await r.json();document.getElementById('hari-hasil').innerHTML='<div class="result">'+d.message+'</div>'}
async function simpanFakta(){const k=document.getElementById('fakta-key').value.trim();const v=document.getElementById('fakta-val').value.trim();if(!k||!v)return toast('Isi key & value');await fetch('/api/fakta',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key:k,value:v})});document.getElementById('fakta-key').value='';document.getElementById('fakta-val').value='';toast('Diingat: '+k);muatFakta()}
async function muatFakta(){const r=await fetch('/api/fakta');const d=await r.json();const l=document.getElementById('fakta-list');if(!d.fakta.length){l.innerHTML='<div style="color:var(--dim);text-align:center;padding:12px">(belum ada)</div>';return}l.innerHTML=d.fakta.map(f=>'<div class="know-item"><span class="k">'+esc(f.key)+'</span><span class="v">'+esc(f.value)+'</span></div>').join('')}
async function simpanNote(){const i=document.getElementById('note-isi').value.trim();if(!i)return toast('Isi dulu');await fetch('/api/note',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({isi:i})});document.getElementById('note-isi').value='';toast('Tercatat')}
async function simpanReminder(){const j=document.getElementById('rem-jam').value;const p=document.getElementById('rem-pesan').value.trim();if(!j||!p)return toast('Isi jam & pesan');await fetch('/api/reminder',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({jam:j,pesan:p})});document.getElementById('rem-pesan').value='';toast('Set: '+j);muatReminder()}
async function muatReminder(){const r=await fetch('/api/reminder');const d=await r.json();const e=document.getElementById('rem-list');if(!d.reminder.length){e.innerHTML='<div style="color:var(--dim);text-align:center">(belum ada)</div>';return}e.innerHTML=d.reminder.map(x=>'<div class="know-item"><span class="k">'+x.jam+'</span><span class="v">'+esc(x.pesan)+'</span></div>').join('')}
async function muatInfoOtak(){const r=await fetch('/api/info-otak');const d=await r.json();const e=document.getElementById('info-otak');if(d.status==='ada'){e.innerHTML='<div style="font-size:.85em;line-height:1.8"><div>Status: <span style="color:var(--ok)">Aktif</span></div><div>Ukuran: '+d.size+' bytes</div><div>Titik data: '+d.titik+'</div><div>Aktivitas: '+d.aktivitas.join(', ')+'</div></div>'}else{e.innerHTML='<div style="color:var(--bad)">Model belum dilatih</div>'}}
async function lihatBackup(){const r=await fetch('/api/backup');const d=await r.json();const e=document.getElementById('backup-list');if(!d.backup.length){e.innerHTML='<div style="color:var(--dim);text-align:center">(belum ada)</div>';return}e.innerHTML=d.backup.map(b=>'<div class="know-item"><span class="k">'+b.nama.slice(0,30)+'</span><span class="v">'+b.size+' B</span></div>').join('')}
async function muatCuaca(){const k=document.getElementById('cuaca-kota').value.trim();const r=await fetch('/api/cuaca'+(k?'?kota='+k:''));const d=await r.json();const e=document.getElementById('cuaca-hasil');if(d.error){e.innerHTML='<div class="result">Error: '+d.error+'</div>';return}e.innerHTML='<div class="result"><strong>'+d.kota+'</strong><br>Suhu: '+d.suhu+' C<br>Cuaca: '+d.cuaca+'<br>Kelembapan: '+d.kelembapan+'%<br>Angin: '+d.angin+' m/s</div>'}
async function muatBerita(){const s=document.getElementById('berita-sumber').value;const r=await fetch('/api/berita?sumber='+s);const d=await r.json();const e=document.getElementById('berita-hasil');if(d.error){e.innerHTML='<div class="result">Error: '+d.error+'</div>';return}e.innerHTML=d.berita.map(b=>'<div class="know-item"><a href="'+b.link+'" target="_blank" style="color:var(--text);text-decoration:none;font-size:.85em">'+b.judul+'</a></div>').join('')}
async function muatSaham(){const k=document.getElementById('saham-kode').value.trim();const r=await fetch('/api/saham?kode='+k);const d=await r.json();const e=document.getElementById('saham-hasil');if(d.error){e.innerHTML='<div class="result">Error: '+d.error+'</div>';return}const w=d.naik?'var(--ok)':'var(--bad)';e.innerHTML='<div class="result"><strong>'+d.kode+'</strong><br>Harga: Rp '+d.harga.toLocaleString()+'<br><span style="color:'+w+'">'+d.perubahan.toFixed(0)+' ('+d.persen.toFixed(2)+'%)</span></div>'}
async function muatKurs(){const r=await fetch('/api/kurs');const d=await r.json();const e=document.getElementById('kurs-hasil');if(d.error){e.innerHTML='<div class="result">Error: '+d.error+'</div>';return}let h='<div class="result">';for(const[k,v]of Object.entries(d)){h+='<div>1 '+k+' = Rp '+v.toLocaleString(undefined,{maximumFractionDigits:0})+'</div>'}h+='</div>';e.innerHTML=h}
async function muatLog(){const r=await fetch('/api/log');const d=await r.json();const e=document.getElementById('log-hasil');if(!d.log.length){e.innerHTML='<div class="result">(kosong)</div>';return}e.innerHTML='<div class="know-list">'+d.log.map(x=>'<div class="know-item"><span class="k">'+x.waktu+'</span><span class="v">'+x.aksi+'</span></div>').join('')+'</div>'}
async function muatGrafik(){const r=await fetch('/api/grafik');const d=await r.json();const e=document.getElementById('log-hasil');if(!d.grafik.length){e.innerHTML='<div class="result">(kosong)</div>';return}let h='<div class="result">';d.grafik.forEach(x=>{const w=Math.min(100,x.count*10);h+='<div>'+x.jam+' <span class="bar" style="width:'+w+'%"></span> '+x.count+'</div>'});h+='</div>';e.innerHTML=h}
updateStatus();setInterval(updateStatus,3000);
</script>
</body>
</html>
"""


def get_html():
    return HTML.replace("__LOGO__", get_logo())