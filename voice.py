"""
voice.py — J.A.R.V.I.S. ki ASLI AWAAZ (browser me)
═══════════════════════════════════════════════════

Termux me awaaz nahi aa sakti (Termux:API Play Store par nahi chalti).
PAR browser me aa sakti hai — Web Speech API har browser me built-in hai.
Koi install nahi, koi API key nahi, koi paisa nahi.

Kahan bolta hai:
  • Login / Signup ke baad swagat
  • Admin panel khulne par
  • Server start / stop
  • Payment approve
  • Server ka RAM/CPU 90% paar

User band kar sakta hai — setting cookie me yaad rehti hai.
"""

from theme import ico


# ═══════════════════════════════════════════════
#   ENGINE — har page me jata hai
# ═══════════════════════════════════════════════

def engine():
    """JS engine — speechSynthesis wrapper + toggle button."""
    return """<script>
(function(){
 if(window.__jv) return; window.__jv=1;
 var SS=window.speechSynthesis;
 var ON=(localStorage.getItem('rx_voice')||'1')==='1';
 var V=null, ready=false;

 function pick(){
  if(!SS) return;
  var vs=SS.getVoices();
  if(!vs.length) return;
  // Indian English pehle, phir koi bhi English, phir default
  V = vs.find(function(v){return /en[-_]IN/i.test(v.lang)})
   || vs.find(function(v){return /en[-_]GB/i.test(v.lang)})
   || vs.find(function(v){return /^en/i.test(v.lang)})
   || vs[0];
  ready=true;
 }
 if(SS){ pick(); SS.onvoiceschanged=pick; }

 var AU=null;          // abhi baj raha audio
 var AI=true;          // server wali asli awaaz try karo?

 function browserSay(txt,opt){
  opt=opt||{};
  if(!SS) return;
  try{
   if(opt.stop!==false) SS.cancel();
   var u=new SpeechSynthesisUtterance(txt);
   if(V) u.voice=V;
   u.lang=(V&&V.lang)||'en-IN';
   u.rate=opt.rate||0.94;
   u.pitch=opt.pitch||0.82;
   u.volume=opt.vol||1;
   SS.speak(u);
  }catch(e){}
 }

 window.jarvis=function(txt,opt){
  opt=opt||{};
  if(!ON||!txt) return;
  // chhoti cheezein ("Yes sir?") browser se — turant chahiye
  if(!AI || opt.quick || txt.length<12){ browserSay(txt,opt); return; }
  try{ if(AU){AU.pause();AU=null;} if(SS) SS.cancel(); }catch(e){}
  fetch('/api/jarvis/tts',{method:'POST',
   headers:{'Content-Type':'application/json'},
   body:JSON.stringify({text:txt})})
  .then(function(r){
    if(!r.ok) throw 0;
    return r.blob();
  })
  .then(function(b){
    var url=URL.createObjectURL(b);
    AU=new Audio(url);
    AU.volume=opt.vol||1;
    AU.onended=function(){URL.revokeObjectURL(url);AU=null};
    return AU.play();
  })
  .catch(function(){ AI=false; browserSay(txt,opt);
    setTimeout(function(){AI=true},60000); });
 };

 window.jarvisOn=function(){return ON};

 window.jarvisToggle=function(){
  ON=!ON;
  localStorage.setItem('rx_voice',ON?'1':'0');
  document.querySelectorAll('.vbtn').forEach(function(b){
   b.classList.toggle('off',!ON);
   b.title=ON?'JARVIS ki awaaz ON':'Awaaz OFF';
  });
  if(ON) window.jarvis('Voice on. JARVIS ready.');
  else if(SS) SS.cancel();
 };

 // pehla click/tap — browser autoplay policy ke liye unlock
 var unlocked=false;
 function unlock(){
  if(unlocked||!SS) return; unlocked=true;
  try{ var u=new SpeechSynthesisUtterance(' ');u.volume=0;SS.speak(u); }
  catch(e){}
  var q=window.__jq;
  if(q&&q.length){ q.forEach(function(t){window.jarvis(t,{stop:false})});
   window.__jq=[]; }
 }
 document.addEventListener('click',unlock,{once:true});
 document.addEventListener('keydown',unlock,{once:true});
 document.addEventListener('touchstart',unlock,{once:true});

 // page load par bolna ho to queue
 window.jarvisSay=function(txt){
  if(!ON) return;
  if(unlocked) window.jarvis(txt);
  else { window.__jq=window.__jq||[]; window.__jq.push(txt); }
 };

 // button state
 document.addEventListener('DOMContentLoaded',function(){
  document.querySelectorAll('.vbtn').forEach(function(b){
   b.classList.toggle('off',!ON);
  });
 });
})();
</script>"""


def button():
    """🔊 Awaaz on/off button — navbar me."""
    return (f'<button class="vbtn" onclick="jarvisToggle()" '
            f'title="JARVIS ki awaaz" aria-label="Voice">'
            f'<span class="von">{ico("speaker", 15)}</span>'
            f'<span class="voff">{ico("mute", 15)}</span>'
            f'<i class="vwave"><b></b><b></b><b></b></i>'
            f'</button>')


def speak(txt, delay=400):
    """Page khulte hi bolna."""
    t = txt.replace('"', "'").replace("\n", " ")
    return (f'<script>setTimeout(function(){{'
            f'if(window.jarvisSay)window.jarvisSay("{t}")}},{delay});'
            f'</script>')


# ═══════════════════════════════════════════════
#   🎤 MIC — JARVIS sunta hai
# ═══════════════════════════════════════════════

def mic_button():
    """🎤 Mic button — dabao, bolo."""
    return (f'<button class="mbtn" id="mbtn" onclick="jvMic()" '
            f'title="JARVIS se bolo" aria-label="Voice command">'
            f'{ico("mic", 16)}'
            f'<i class="mring"></i></button>')


def mic_engine():
    """
    🎤 SpeechRecognition — do mode:
      TAP  : button dabao, phir bolo
      AUTO : hamesha sunta hai, "Jarvis" bolte hi jaag jata hai
    Khatarnak command par pehle poochta hai — galti se kuch nahi hoga.
    """
    return """<script>
(function(){
 if(window.__jvm) return; window.__jvm=1;
 var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
 var rec=null, listening=false, awake=false, pending='', wakeT=null;
 var AUTO=(localStorage.getItem('rx_wake')||'0')==='1';
 var WAKE=/\b(jarvis|jervis|jaarvis|jarwis|jarvish|jervez|service)\b/i;

 function ui(state,txt,st){
  var b=document.getElementById('mbtn'),p=document.getElementById('mpanel'),
      t=document.getElementById('mtxt'),s=document.getElementById('mstat'),
      w=document.getElementById('mwake');
  if(b) b.className='mbtn'+(state?' '+state:'')+(AUTO?' auto':'');
  if(p) p.classList.toggle('on',!!state);
  if(t&&txt!==undefined) t.textContent=txt;
  if(s) s.textContent=st!==undefined?st:({
   listening:'Sun raha hoon…',wake:'"Jarvis" boliye…',
   working:'Kaam kar raha hoon…',ask:'Haan ya nahi?',
   done:'Ho gaya',err:'Samajh nahi aaya'}[state]||'');
  if(w) w.classList.toggle('on',AUTO);
 }

 function speak(t,o){ if(window.jarvis) window.jarvis(t,o); }

 // ── AUTO MODE toggle ──
 window.jvWake=function(){
  AUTO=!AUTO;
  localStorage.setItem('rx_wake',AUTO?'1':'0');
  if(AUTO){ speak('Always listening. Bas Jarvis boliye.');
   ui('wake','','"Jarvis" boliye…'); start(true); }
  else { speak('Always listening off.'); stop(); ui(''); }
  var w=document.getElementById('mwake');
  if(w){w.classList.toggle('on',AUTO);
   w.title=AUTO?'Hamesha sun raha hai':'Wake word OFF';}
 };

 function stop(){ listening=false; awake=false;
  try{ if(rec){rec.onend=null;rec.abort();} }catch(e){} rec=null; }

 function start(cont){
  if(!SR){ return; }
  if(listening){ return; }
  rec=new SR();
  rec.lang='en-IN'; rec.interimResults=true;
  rec.continuous=!!cont; rec.maxAlternatives=2;
  listening=true;

  rec.onresult=function(e){
   var fin='', part='';
   for(var i=e.resultIndex;i<e.results.length;i++){
    var r=e.results[i];
    if(r.isFinal) fin+=r[0].transcript; else part+=r[0].transcript;
   }
   var live=(fin||part).trim();

   if(AUTO && !awake && !pending){
    // wake word ka intezaar
    if(WAKE.test(live)){
     awake=true;
     ui('listening',live,'Ji sir…');
     speak('Yes sir?',{rate:1.12});
     clearTimeout(wakeT);
     wakeT=setTimeout(function(){ awake=false; ui('wake','',''); },9000);
    } else {
     ui('wake','','"Jarvis" boliye…');
    }
    if(!awake) return;
   }

   if(live) ui(pending?'ask':'listening',live);

   if(fin.trim()){
    clearTimeout(wakeT);
    var say=fin.trim();
    if(AUTO && !awake && !pending) return;
    // wake word ke saath hi command aayi?
    ui('working',say);
    send(say);
    awake=false;
    if(!cont){ listening=false; }
   }
  };

  rec.onerror=function(e){
   listening=false;
   if(e.error==='not-allowed'){
    AUTO=false; localStorage.setItem('rx_wake','0');
    ui('err','','Mic ki permission chahiye');
    setTimeout(function(){ui('')},3000); return;
   }
   if(AUTO){ setTimeout(function(){start(true)},700); }
   else { ui('err','','Sunayi nahi diya');
    setTimeout(function(){ui('')},2400); }
  };

  rec.onend=function(){
   listening=false;
   if(AUTO){ setTimeout(function(){start(true)},350); }
   else if(!pending){ ui(''); }
  };

  try{ rec.start(); }catch(e){ listening=false; }
 }

 // ── TAP mode ──
 window.jvMic=function(){
  if(!SR){ alert('Aapka browser voice support nahi karta.\\n'+
   'Chrome ya Edge use kariye.'); return; }
  if(AUTO){ awake=true; ui('listening','','Ji sir…');
   speak('Yes sir?',{rate:1.12}); return; }
  if(listening){ stop(); ui(''); return; }
  ui('listening','');
  speak('Yes?',{rate:1.12});
  start(false);
 };

 // ── server se baat ──
 function send(txt){
  fetch('/api/jarvis',{method:'POST',
   headers:{'Content-Type':'application/json'},
   body:JSON.stringify({text:txt,pending:pending})})
  .then(function(r){return r.json()})
  .then(function(d){
   if(d.confirm){
    pending=d.pending;
    ui('ask',d.shown,'Boliye — haan ya nahi');
    speak(d.say);
    if(!AUTO) setTimeout(function(){start(false)},900);
    // 15 sec me jawab nahi -> cancel
    clearTimeout(wakeT);
    wakeT=setTimeout(function(){
     if(pending){ pending=''; ui('','',''); }
    },15000);
    return;
   }
   pending='';
   ui(d.ok?'done':'err', d.shown||txt);
   if(d.say) speak(d.say);
   if(d.reload) setTimeout(function(){location.reload()},2600);
   else setTimeout(function(){ AUTO?ui('wake','',''):ui(''); },3600);
  }).catch(function(){
   pending='';
   ui('err','','Server se baat nahi ho paayi');
   setTimeout(function(){ AUTO?ui('wake','',''):ui(''); },2600);
  });
 }

 // Ctrl+Space
 document.addEventListener('keydown',function(e){
  if(e.ctrlKey&&e.code==='Space'){e.preventDefault();window.jvMic();}
 });

 // auto mode on tha to shuru karo (pehle click ke baad)
 if(AUTO){
  var go=function(){ ui('wake','',''); start(true);
   document.removeEventListener('click',go); };
  document.addEventListener('click',go,{once:true});
 }
})();
</script>"""


def wake_button():
    """♾️ Always-listening toggle."""
    return (f'<button class="wbtn" id="mwake" onclick="jvWake()" '
            f'title="Hamesha sunta rahe" aria-label="Wake word">'
            f'{ico("bolt", 14)}</button>')


def mic_panel():
    """Panel jo bolte waqt dikhta hai."""
    return (
        '<div class="mpanel" id="mpanel">'
        '<div class="mwave"><b></b><b></b><b></b><b></b><b></b>'
        '<b></b><b></b></div>'
        '<div class="mtxt" id="mtxt"></div>'
        '<div class="mstat" id="mstat"></div>'
        '</div>')


def css():
    return """
.vbtn{position:relative;width:38px;height:38px;border-radius:10px;
cursor:pointer;display:grid;place-items:center;
background:linear-gradient(160deg,var(--card),var(--bg2));
border:1px solid var(--line);color:var(--acc4);
transition:.24s var(--ease);overflow:hidden}
.vbtn:hover{border-color:var(--line2);box-shadow:0 0 20px var(--glow)}
.vbtn .voff{display:none}
.vbtn.off{color:var(--dim3)}
.vbtn.off .von{display:none}
.vbtn.off .voff{display:block}
.vbtn .vwave{position:absolute;bottom:4px;left:0;right:0;height:8px;
display:flex;align-items:flex-end;justify-content:center;gap:2px;
opacity:0;transition:.2s}
.vbtn:not(.off):hover .vwave{opacity:.85}
.vbtn .vwave b{width:2px;background:var(--cy);border-radius:1px;
animation:vw 1s ease-in-out infinite}
.vbtn .vwave b:nth-child(1){height:4px;animation-delay:0s}
.vbtn .vwave b:nth-child(2){height:8px;animation-delay:.16s}
.vbtn .vwave b:nth-child(3){height:5px;animation-delay:.32s}
@keyframes vw{0%,100%{transform:scaleY(.4)}50%{transform:scaleY(1)}}

/* 🎤 MIC */
.mbtn{position:relative;width:38px;height:38px;border-radius:10px;
cursor:pointer;display:grid;place-items:center;
background:linear-gradient(160deg,var(--card),var(--bg2));
border:1px solid var(--line);color:var(--cy);transition:.24s var(--ease)}
.mbtn:hover{border-color:var(--cy);box-shadow:0 0 20px var(--bglow)}
.mbtn .mring{position:absolute;inset:-3px;border-radius:12px;
border:2px solid var(--cy);opacity:0;pointer-events:none}
.mbtn.listening{background:linear-gradient(135deg,#00E6FF,#7C3AED);
color:#fff;border-color:transparent}
.mbtn.listening .mring{opacity:1;animation:mr 1.3s ease-out infinite}
@keyframes mr{0%{inset:-3px;opacity:.9}100%{inset:-13px;opacity:0}}
.mbtn.working{background:var(--g1);color:#fff;border-color:transparent}
.mbtn.working .mring{opacity:1;border-color:var(--pk);
animation:mr .9s ease-out infinite}
.mbtn.done{background:rgba(34,197,94,.2);color:var(--ok);
border-color:var(--ok)}
.mbtn.err{background:rgba(239,68,68,.18);color:var(--err);
border-color:var(--err)}

.mpanel{position:fixed;left:50%;bottom:26px;transform:translateX(-50%)
translateY(24px);z-index:800;min-width:min(430px,calc(100vw - 32px));
max-width:calc(100vw - 32px);padding:16px 20px;border-radius:16px;
background:linear-gradient(165deg,var(--card),var(--bg2));
border:1px solid var(--line2);box-shadow:var(--sh2),0 0 46px var(--bglow);
opacity:0;pointer-events:none;transition:.3s var(--ease);text-align:center}
.mpanel.on{opacity:1;transform:translateX(-50%);pointer-events:auto}
.mwave{display:flex;align-items:center;justify-content:center;gap:4px;
height:26px;margin-bottom:10px}
.mwave b{width:3px;border-radius:2px;background:var(--cy);
animation:mw 1.05s ease-in-out infinite}
.mwave b:nth-child(1){height:8px;animation-delay:0s}
.mwave b:nth-child(2){height:16px;animation-delay:.1s;background:#22D3EE}
.mwave b:nth-child(3){height:24px;animation-delay:.2s;background:#7C3AED}
.mwave b:nth-child(4){height:26px;animation-delay:.3s;background:#8B5CF6}
.mwave b:nth-child(5){height:24px;animation-delay:.4s;background:#EC4899}
.mwave b:nth-child(6){height:16px;animation-delay:.5s;background:#7C3AED}
.mwave b:nth-child(7){height:8px;animation-delay:.6s}
@keyframes mw{0%,100%{transform:scaleY(.28)}50%{transform:scaleY(1)}}
.mtxt{font-size:15px;font-weight:600;color:var(--txt);min-height:20px;
word-break:break-word}
.mstat{font-size:11.5px;color:var(--dim2);margin-top:5px;letter-spacing:.6px}
.mbtn.ask{background:linear-gradient(135deg,#F59E0B,#EC4899);color:#fff;
border-color:transparent}
.mbtn.ask .mring{opacity:1;border-color:var(--warn);
animation:mr 1.1s ease-out infinite}
.mbtn.auto{border-color:rgba(0,230,255,.45)}
.mbtn.auto::before{content:'';position:absolute;top:-2px;right:-2px;
width:7px;height:7px;border-radius:50%;background:#22C55E;
box-shadow:0 0 8px #22C55E;animation:bp 1.8s infinite}
.mbtn.wake{background:rgba(0,230,255,.1)}
.mpanel.ask{border-color:rgba(245,158,11,.5);
box-shadow:var(--sh2),0 0 46px rgba(245,158,11,.22)}

/* ♾️ WAKE toggle */
.wbtn{width:38px;height:38px;border-radius:10px;cursor:pointer;
display:grid;place-items:center;position:relative;
background:linear-gradient(160deg,var(--card),var(--bg2));
border:1px solid var(--line);color:var(--dim3);transition:.24s var(--ease)}
.wbtn:hover{border-color:var(--line2);color:var(--acc4)}
.wbtn.on{background:linear-gradient(135deg,rgba(0,230,255,.2),
rgba(124,58,237,.15));border-color:var(--cy);color:var(--cy)}
.wbtn.on::after{content:'';position:absolute;inset:-3px;border-radius:12px;
border:1.5px solid var(--cy);opacity:.5;animation:mr 2.2s ease-out infinite}
"""
