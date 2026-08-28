"""
css.py — RAVAN X CLOUD design system
═════════════════════════════════════
Company-level UI: glass cards, gradients, smooth motion.
"""

CSS = """
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{
/* ── BACKGROUNDS ── */
--bg:#070B14;--bg2:#0B1020;--bg3:#0F172A;
--card:#0F172A;--card2:#111827;--card3:#1A2338;
--line:rgba(148,163,184,.15);--line2:rgba(124,58,237,.50);

/* ── TEXT ── */
--txt:#F8FAFC;--dim:#CBD5E1;--dim2:#94A3B8;--dim3:#64748B;

/* ── BRAND: purple ── */
--acc:#7C3AED;--acc2:#5B21B6;--acc3:#8B5CF6;--acc4:#A78BFA;

/* ── NEON ── */
--cy:#00E6FF;--cy2:#22D3EE;--cy3:#67E8F9;
--pk:#FF0080;--pk2:#EC4899;
--blu:#00E6FF;--blu2:#0891B2;--blu3:#22D3EE;
--pu:#8B5CF6;

/* ── STATUS ── */
--ok:#22C55E;--warn:#F59E0B;--err:#EF4444;--info:#38BDF8;

/* ── GLOW ── */
--glow:rgba(124,58,237,.25);
--bglow:rgba(0,230,255,.20);
--pglow:rgba(255,0,128,.18);

/* ── GRADIENTS ── */
--g1:linear-gradient(135deg,#7C3AED,#8B5CF6,#EC4899);
--g2:linear-gradient(135deg,#00E6FF,#7C3AED,#FF0080);
--g3:linear-gradient(135deg,#7C3AED,#00E6FF);

--r:16px;--r2:12px;--r3:9px;
--sh:0 4px 24px rgba(0,0,0,.45);
--sh2:0 12px 48px rgba(0,0,0,.6);
--shg:0 6px 28px rgba(124,58,237,.28);
--ease:cubic-bezier(.22,1,.36,1)}

html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--txt);line-height:1.62;
font-family:'Inter','Segoe UI',system-ui,-apple-system,sans-serif;
-webkit-font-smoothing:antialiased;overflow-x:hidden}
body::before{content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
background:
radial-gradient(760px 430px at 10% -10%,rgba(124,58,237,.20),transparent 62%),
radial-gradient(680px 400px at 92% 2%,rgba(0,230,255,.11),transparent 62%),
radial-gradient(520px 320px at 55% 108%,rgba(255,0,128,.08),transparent 62%)}
a{color:inherit;text-decoration:none}
button,input,select,textarea{font-family:inherit}
.wrap{max-width:1280px;margin:0 auto;padding:0 22px;position:relative;z-index:1}
svg.i{flex-shrink:0;vertical-align:-3px}

/* LOGO */
.lg{display:inline-flex;align-items:center;gap:10px}
.licon{border-radius:9px;object-fit:cover;
filter:drop-shadow(0 3px 12px var(--glow));transition:.4s var(--ease)}
.lg:hover .licon{transform:rotate(-6deg) scale(1.07)}
.achart{width:100%;height:auto;display:block}
.bgb{transition:opacity .2s}
.bgb:hover{opacity:1!important}
.linkbox2{background:var(--bg2);border:1px solid var(--acc);
border-radius:8px;padding:9px 12px;font-family:monospace;font-size:11.5px;
color:var(--acc3);word-break:break-all}
.lgnd{display:flex;gap:16px;justify-content:center;margin-top:8px;
flex-wrap:wrap}
.lgi{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--dim)}
.lgi i{width:9px;height:3px;border-radius:2px;display:block}
.lgi b{color:var(--txt);font-variant-numeric:tabular-nums}
.lmark{filter:drop-shadow(0 3px 12px var(--glow));transition:.4s var(--ease)}
.lg:hover .lmark{transform:rotate(-8deg) scale(1.06)}
.ltx{display:flex;align-items:baseline;gap:3px;font-size:19px;
font-weight:800;letter-spacing:-.4px;line-height:1}
.ltx b{color:var(--txt)}
.ltx em{font-style:normal;
background:linear-gradient(135deg,var(--acc3),var(--cy));
-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.lsub{font-size:8.5px;letter-spacing:2.4px;color:var(--dim2);
font-weight:700;margin-left:4px;align-self:flex-end;padding-bottom:2px}

/* NAV */
nav{position:sticky;top:0;z-index:200;
background:rgba(7,11,20,.86);backdrop-filter:blur(22px) saturate(180%);
border-bottom:1px solid var(--line);position:sticky}
nav::after{content:'';position:absolute;left:0;right:0;bottom:-1px;height:1px;
background:linear-gradient(90deg,transparent,rgba(124,58,237,.55),
rgba(0,230,255,.4),transparent)}
nav .wrap{display:flex;align-items:center;gap:8px;height:68px}
.nlinks{display:flex;gap:4px;margin-left:auto;align-items:center}
.nlinks>a{color:var(--dim);font-size:14px;font-weight:550;
padding:8px 14px;border-radius:var(--r3);transition:.2s var(--ease)}
.nlinks>a:hover{color:var(--txt);background:var(--card2);
box-shadow:inset 0 0 0 1px rgba(124,58,237,.28)}
.burger{display:none;margin-left:auto;background:none;border:0;
color:var(--txt);padding:8px;cursor:pointer;border-radius:8px}

/* BUTTON */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;
padding:11px 20px;border-radius:var(--r3);font-weight:650;font-size:14px;
cursor:pointer;border:1px solid transparent;transition:.22s var(--ease);
white-space:nowrap;position:relative;overflow:hidden}
.btn-p{background:var(--g1);background-size:200% auto;color:#fff;
box-shadow:0 3px 18px var(--glow),inset 0 1px 0 rgba(255,255,255,.22)}
.btn-p:hover{transform:translateY(-2px);background-position:right center;
box-shadow:0 10px 34px var(--glow),0 0 0 1px rgba(139,92,246,.4)}
.btn::after{content:'';position:absolute;top:0;left:-120%;width:60%;height:100%;
background:linear-gradient(90deg,transparent,rgba(255,255,255,.18),transparent);
transform:skewX(-20deg);transition:left .55s var(--ease);pointer-events:none}
.btn:hover::after{left:130%}
.btn-p:active{transform:translateY(0)}
.btn-g{background:var(--card2);color:var(--txt);border-color:var(--line2)}
.btn-g:hover{background:var(--card3);border-color:var(--acc);color:var(--acc4);
box-shadow:0 0 0 1px var(--glow),0 4px 18px var(--glow)}
.btn-c{background:linear-gradient(135deg,rgba(0,230,255,.14),rgba(0,230,255,.05));
color:var(--cy);border-color:rgba(0,230,255,.34)}
.btn-c:hover{box-shadow:0 4px 20px var(--bglow);border-color:var(--cy)}
.btn-d{background:rgba(239,68,68,.1);color:#FF6B8A;
border-color:rgba(239,68,68,.28)}
.btn-d:hover{background:rgba(239,68,68,.18)}
.btn-ok{background:rgba(34,197,94,.12);color:#22C55E;
border-color:rgba(34,197,94,.3)}
.btn-sm{padding:7px 13px;font-size:12.8px;border-radius:8px}
.btn-lg{padding:14px 28px;font-size:15.5px;border-radius:11px}
.btn-b{width:100%}

/* HERO */
.hero{padding:62px 0 76px;text-align:center;position:relative}
.herologo{margin-bottom:24px;display:flex;justify-content:center}
.lbig{border-radius:50%;animation:lfloat 5s ease-in-out infinite;
filter:drop-shadow(0 0 44px rgba(124,58,237,.5))
       drop-shadow(0 0 78px rgba(0,230,255,.22))}
@keyframes lfloat{
0%,100%{transform:translateY(0) scale(1)}
50%{transform:translateY(-11px) scale(1.02)}}
.licon{border-radius:50%;
filter:drop-shadow(0 2px 11px rgba(124,58,237,.55))}
.hero h1{font-size:clamp(34px,6.2vw,64px);font-weight:850;line-height:1.08;
letter-spacing:-2px}
.hero h1 .gr{background:linear-gradient(120deg,#00E6FF,#7C3AED 38%,
#EC4899 68%,#00E6FF);-webkit-background-clip:text;
-webkit-text-fill-color:transparent;background-size:200% auto;
animation:shine 5s linear infinite}
@keyframes shine{to{background-position:200% center}}
.hero .lead{color:var(--dim);font-size:clamp(15px,2vw,19px);max-width:620px;
margin:22px auto 34px}
.hero .cta{display:flex;gap:13px;justify-content:center;flex-wrap:wrap}
.pill{display:inline-flex;align-items:center;gap:9px;padding:7px 17px;
background:linear-gradient(135deg,var(--card2),var(--card));
border:1px solid var(--line2);border-radius:99px;font-size:12.8px;
color:var(--dim);margin-bottom:26px;box-shadow:var(--sh)}
.dot{width:7px;height:7px;border-radius:50%;background:var(--ok);
box-shadow:0 0 0 3px rgba(34,197,94,.16);animation:bp 2.4s infinite}
@keyframes bp{0%,100%{opacity:1}50%{opacity:.4}}
.trust{display:flex;gap:32px;justify-content:center;flex-wrap:wrap;
margin-top:44px;color:var(--dim2);font-size:12.5px;font-weight:600;
letter-spacing:.8px;text-transform:uppercase}
.trust span{display:flex;align-items:center;gap:7px}

.oldu{display:flex;justify-content:space-between;align-items:center;
font-family:ui-monospace,monospace;font-size:11px;color:var(--dim2);
padding:4px 8px;margin-top:3px;border-radius:6px;
background:rgba(255,255,255,.03);border-left:2px solid rgba(245,158,11,.5)}
.oldu span{color:var(--warn);font-size:10px;white-space:nowrap}
.botwel{display:flex;align-items:center;gap:12px;padding:13px 15px;
border-radius:12px;margin-bottom:16px;
background:linear-gradient(135deg,rgba(0,230,255,.12),rgba(124,58,237,.1));
border:1px solid rgba(0,230,255,.3)}
.botwel .bwi{width:38px;height:38px;border-radius:10px;display:grid;
place-items:center;background:rgba(0,230,255,.16);color:var(--cy);
flex-shrink:0;animation:bwp 2.4s ease-in-out infinite}
@keyframes bwp{0%,100%{box-shadow:0 0 0 0 rgba(0,230,255,.4)}
50%{box-shadow:0 0 0 8px rgba(0,230,255,0)}}
.botwel b{display:block;font-size:14.5px}
.botwel span{font-size:12.5px;color:var(--dim)}

/* 🔧 CODE DOCTOR */
.cdoc{border-color:rgba(0,230,255,.25)}
.cdbeta{font-size:9px;letter-spacing:1.2px;padding:2px 7px;border-radius:6px;
background:var(--g3);color:#fff;font-weight:800;margin-left:7px;
vertical-align:middle}
.cdbtns{display:flex;gap:7px;flex-wrap:wrap}
.bosshead{display:flex;justify-content:space-between;align-items:center;
gap:16px;flex-wrap:wrap;padding:18px 20px;margin-bottom:20px;border-radius:16px;
border:1px solid rgba(148,163,184,.15);
background:linear-gradient(135deg,#7C3AED22,#00E6FF11,#FF008011)}
.bhleft{display:flex;align-items:center;gap:14px}
.bhicon{width:52px;height:52px;border-radius:14px;display:flex;
align-items:center;justify-content:center;color:#F8FAFC;
background:linear-gradient(135deg,#7C3AED,#8B5CF6,#EC4899);
box-shadow:0 0 26px rgba(124,58,237,.45)}
.bosshead h2{margin:0;font-size:19px;letter-spacing:2px}
.bhright{display:flex;gap:10px;flex-wrap:wrap}
.bstat{text-align:center;padding:8px 14px;border-radius:11px;
background:rgba(11,16,32,.6);border:1px solid rgba(148,163,184,.15);min-width:74px}
.bstat b{display:block;font-size:16px;color:#00E6FF}
.bstat i{font-size:9.5px;color:#94A3B8;font-style:normal;letter-spacing:.4px}
.bstat.on b{color:#22C55E} .bstat.off b{color:#64748B}
.bchips{display:flex;gap:6px;flex-wrap:wrap}
.bchip{padding:6px 12px;border-radius:20px;font-size:11.5px;cursor:pointer;
background:rgba(11,16,32,.6);color:#94A3B8;
border:1px solid rgba(148,163,184,.15);transition:.15s}
.bchip:hover{border-color:rgba(124,58,237,.5);color:#CBD5E1}
.bchip.on{background:linear-gradient(135deg,#7C3AED,#8B5CF6);
color:#F8FAFC;border-color:transparent}
.binput{width:100%;padding:13px;border-radius:12px;font-size:13.5px;
background:rgba(7,11,20,.8);color:#F8FAFC;resize:vertical;
border:1px solid rgba(148,163,184,.15);font-family:inherit}
.binput:focus{outline:none;border-color:rgba(124,58,237,.5)}
.bteam{font-size:12px;color:#94A3B8;display:flex;align-items:center;gap:7px;
cursor:pointer}
.bout{display:none;margin-top:14px;padding:14px;border-radius:12px;
background:rgba(11,16,32,.75);border:1px solid rgba(148,163,184,.15)}
.bout.on{display:block}
.bout.ok{border-color:rgba(34,197,94,.4)}
.bout.warn{border-color:rgba(245,158,11,.45)}
.bout.err{border-color:rgba(239,68,68,.45)}
.bmeta{display:flex;gap:8px;flex-wrap:wrap;font-size:10.5px;color:#64748B;
margin-bottom:10px;align-items:center}
.bjob{padding:3px 9px;border-radius:7px;color:#F8FAFC;
background:linear-gradient(135deg,#7C3AED,#EC4899);letter-spacing:.5px}
.bteamtag{padding:3px 9px;border-radius:7px;background:rgba(0,230,255,.15);
color:#00E6FF;border:1px solid rgba(0,230,255,.3)}
.bans{font-size:13.5px;line-height:1.68;color:#F8FAFC;white-space:pre-wrap;
word-break:break-word}
.btried{margin-top:12px;padding-top:11px;font-size:10.5px;color:#64748B;
border-top:1px solid rgba(148,163,184,.12);display:flex;gap:7px;flex-wrap:wrap;
align-items:center}
.btried b{color:#94A3B8;margin-right:4px}
.btried span{padding:2px 8px;border-radius:6px;background:rgba(7,11,20,.7)}
.btried .ok{color:#22C55E} .btried .no{color:#EF4444}
.bboard{margin-top:12px;overflow-x:auto}
.mnav{width:100%;border-collapse:collapse;font-size:11.5px}
.mnav th{text-align:left;padding:8px 9px;color:#64748B;font-weight:600;
font-size:10px;letter-spacing:.7px;border-bottom:1px solid rgba(148,163,184,.15)}
.mnav td{padding:8px 9px;color:#CBD5E1;border-bottom:1px solid rgba(148,163,184,.07)}
.mnav tr:hover td{background:rgba(124,58,237,.06)}
.mnav .bm{color:#F8FAFC;font-weight:600}
.brep{display:inline-block;padding:2px 8px;border-radius:6px;font-size:10.5px;
color:#F8FAFC;background:linear-gradient(90deg,#22C55E var(--w),rgba(100,116,139,.2) var(--w))}
/* ✨ AUTH ANIMATION */
.auth{position:relative;overflow:hidden}
.afx{position:absolute;inset:0;pointer-events:none;z-index:0}
.afxgrid{position:absolute;inset:-50%;opacity:.4;
background-image:linear-gradient(rgba(124,58,237,.09) 1px,transparent 1px),
linear-gradient(90deg,rgba(0,230,255,.07) 1px,transparent 1px);
background-size:46px 46px;animation:afxdrift 24s linear infinite}
@keyframes afxdrift{to{transform:translate(46px,46px)}}
.afxp{position:absolute;width:4px;height:4px;border-radius:50%;
background:#7C3AED;box-shadow:0 0 12px 3px rgba(124,58,237,.7);
animation:afxfloat 13s ease-in-out infinite}
.afxp.p1{left:8%;top:22%;animation-delay:0s}
.afxp.p2{left:88%;top:16%;background:#00E6FF;
box-shadow:0 0 12px 3px rgba(0,230,255,.7);animation-delay:2.1s}
.afxp.p3{left:16%;top:78%;background:#EC4899;
box-shadow:0 0 12px 3px rgba(236,72,153,.6);animation-delay:4.3s}
.afxp.p4{left:78%;top:70%;animation-delay:6.2s}
.afxp.p5{left:50%;top:9%;background:#00E6FF;
box-shadow:0 0 10px 3px rgba(0,230,255,.6);animation-delay:8.4s}
.afxp.p6{left:34%;top:88%;background:#EC4899;
box-shadow:0 0 10px 3px rgba(236,72,153,.5);animation-delay:10.5s}
@keyframes afxfloat{0%,100%{transform:translate(0,0);opacity:.25}
25%{transform:translate(22px,-26px);opacity:.9}
50%{transform:translate(-16px,-42px);opacity:.55}
75%{transform:translate(-26px,-14px);opacity:.85}}
.afxscan{position:absolute;left:0;right:0;height:2px;top:-2px;
background:linear-gradient(90deg,transparent,rgba(0,230,255,.55),transparent);
animation:afxscan 6.5s ease-in-out infinite}
@keyframes afxscan{0%{top:-2px;opacity:0}8%{opacity:1}
92%{opacity:1}100%{top:100%;opacity:0}}
.afxtype{position:relative;z-index:2;text-align:center;
margin:0 auto 16px;font-size:13px;color:#94A3B8;min-height:20px;
letter-spacing:.4px;font-family:ui-monospace,monospace}
.afxtype span{color:#00E6FF}
.afxcur{display:inline-block;width:2px;height:14px;margin-left:2px;
background:#7C3AED;vertical-align:-2px;animation:afxblink 1s step-end infinite}
@keyframes afxblink{50%{opacity:0}}
.authin{position:relative;z-index:2;
animation:afxin .55s cubic-bezier(.2,.9,.3,1.2) both}
@keyframes afxin{from{opacity:0;transform:translateY(22px) scale(.97)}
to{opacity:1;transform:none}}
.authin .fld{animation:afxfld .5s ease both}
.authin .fld:nth-child(1){animation-delay:.10s}
.authin .fld:nth-child(2){animation-delay:.18s}
.authin .fld:nth-child(3){animation-delay:.26s}
.authin .fld:nth-child(4){animation-delay:.34s}
@keyframes afxfld{from{opacity:0;transform:translateX(-12px)}to{opacity:1;transform:none}}
.authin input{transition:border-color .2s,box-shadow .2s}
.authin input:focus{box-shadow:0 0 0 3px rgba(124,58,237,.16)}
.authin.go{animation:afxout .4s ease forwards}
@keyframes afxout{to{opacity:.35;transform:scale(.985)}}
#afxbtn{position:relative;overflow:hidden}
#afxbtn::after{content:"";position:absolute;top:0;left:-120%;width:60%;
height:100%;background:linear-gradient(90deg,transparent,
rgba(255,255,255,.22),transparent);animation:afxshine 3.2s ease-in-out infinite}
@keyframes afxshine{0%{left:-120%}55%,100%{left:130%}}
#afxbtn.load{opacity:.75;cursor:wait}
#afxbtn.load::after{animation-duration:.85s}
/* 💬 BOSS CHAT */
.chatcard{border-color:rgba(124,58,237,.28)}
.viptag{display:inline-flex;align-items:center;gap:5px;padding:4px 11px;
border-radius:20px;font-size:10px;font-weight:700;letter-spacing:1.2px;
color:var(--c);background:color-mix(in srgb,var(--c) 14%,transparent);
border:1px solid color-mix(in srgb,var(--c) 42%,transparent);
box-shadow:0 0 14px -4px var(--c)}
.bmlim{margin-bottom:10px;font-size:11.5px;color:#F59E0B;line-height:1.5}
.bmlim:empty{display:none}
.bmlim a{color:#00E6FF;text-decoration:underline}
.bmlim b{color:#F8FAFC}
.chatwrap{position:relative;border-radius:13px;overflow:hidden;
background:rgba(7,11,20,.62);border:1px solid rgba(148,163,184,.13)}
.chatbox{height:330px;overflow-y:auto;padding:14px;display:flex;
flex-direction:column;gap:11px;scroll-behavior:smooth}
.chatbox::-webkit-scrollbar{width:6px}
.chatbox::-webkit-scrollbar-thumb{background:rgba(124,58,237,.35);
border-radius:3px}
.cmsg{display:flex;gap:9px;align-items:flex-start;max-width:88%;
animation:cmin .3s cubic-bezier(.2,.9,.3,1.15) both}
@keyframes cmin{from{opacity:0;transform:translateY(9px)}to{opacity:1;transform:none}}
.cmsg.me{align-self:flex-end;flex-direction:row-reverse}
.cav{width:29px;height:29px;flex:0 0 29px;border-radius:9px;display:flex;
align-items:center;justify-content:center;font-size:14px;color:#F8FAFC;
background:linear-gradient(135deg,#7C3AED,#8B5CF6)}
.cmsg.me .cav{background:linear-gradient(135deg,#00E6FF,#22D3EE);color:#070B14}
.cbub{padding:10px 13px;border-radius:13px;font-size:13px;line-height:1.62;
color:#F8FAFC;background:rgba(17,24,39,.9);
border:1px solid rgba(148,163,184,.13);word-break:break-word}
.cmsg.me .cbub{background:linear-gradient(135deg,rgba(0,230,255,.13),
rgba(124,58,237,.13));border-color:rgba(0,230,255,.28)}
.cmsg.warn .cbub{border-color:rgba(245,158,11,.42);background:rgba(245,158,11,.08)}
.cbub b{color:#00E6FF}
.cbub code{padding:1px 6px;border-radius:5px;font-size:11.5px;color:#00E6FF;
background:rgba(0,230,255,.09)}
.ccode{margin:8px 0 0;padding:11px;border-radius:9px;font-size:11.5px;
line-height:1.55;overflow-x:auto;color:#CBD5E1;background:rgba(7,11,20,.9);
border:1px solid rgba(148,163,184,.13);white-space:pre}
.cmeta{display:flex;gap:6px;flex-wrap:wrap;font-size:9.5px;color:#64748B;
margin-bottom:7px;align-items:center}
.ctype{display:inline-flex;gap:4px;align-items:center}
.ctype i{width:6px;height:6px;border-radius:50%;background:#7C3AED;
animation:ctb 1.3s ease-in-out infinite}
.ctype i:nth-child(2){animation-delay:.18s;background:#00E6FF}
.ctype i:nth-child(3){animation-delay:.36s;background:#EC4899}
@keyframes ctb{0%,60%,100%{transform:translateY(0);opacity:.4}
30%{transform:translateY(-6px);opacity:1}}
.cswap{margin-bottom:8px;padding:7px 10px;border-radius:8px;font-size:11px;
color:#F59E0B;background:rgba(245,158,11,.09);
border:1px solid rgba(245,158,11,.28)}
.chatbar{display:flex;gap:8px;align-items:flex-end}
.cmsel{padding:11px 9px;border-radius:11px;font-size:11.5px;max-width:185px;
background:rgba(7,11,20,.85);color:#CBD5E1;font-family:inherit;
border:1px solid rgba(148,163,184,.15);cursor:pointer}
.cmsel:focus{outline:none;border-color:rgba(124,58,237,.55)}
.cminput{flex:1;min-height:44px;max-height:130px;padding:12px 14px;
border-radius:12px;font-size:13.5px;line-height:1.5;resize:none;
background:rgba(7,11,20,.85);color:#F8FAFC;font-family:inherit;
border:1px solid rgba(148,163,184,.15)}
.cminput:focus{outline:none;border-color:rgba(124,58,237,.55);
box-shadow:0 0 0 3px rgba(124,58,237,.13)}
.cmsend{width:46px;height:46px;flex:0 0 46px;border-radius:12px;border:0;
display:flex;align-items:center;justify-content:center;cursor:pointer;
color:#F8FAFC;background:linear-gradient(135deg,#7C3AED,#8B5CF6,#EC4899);
box-shadow:0 0 20px -6px rgba(124,58,237,.85);transition:.18s}
.cmsend:hover{transform:translateY(-2px) scale(1.05);
box-shadow:0 0 26px -4px rgba(124,58,237,1)}
.cmsend:active{transform:scale(.94)}
.cmsend.busy{opacity:.6;cursor:wait;animation:cmspin 1s linear infinite}
@keyframes cmspin{to{transform:rotate(360deg)}}
.chatfoot{font-size:11px}
@media(max-width:640px){.chatbar{flex-wrap:wrap}
.cmsel{max-width:none;width:100%;order:3}
.cminput{min-width:0}.chatbox{height:280px}.cmsg{max-width:95%}}
.agentcard{border-color:rgba(0,230,255,.25)}
.agsteps{display:flex;gap:7px;flex-wrap:wrap}
.agsteps span{padding:5px 10px;border-radius:8px;font-size:10.5px;
color:#94A3B8;background:rgba(11,16,32,.6);
border:1px solid rgba(148,163,184,.12)}
.agsteps b{color:#00E6FF}
.agrow{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.agsel,.aginp{padding:10px 12px;border-radius:10px;font-size:12.5px;
background:rgba(7,11,20,.8);color:#F8FAFC;font-family:inherit;
border:1px solid rgba(148,163,184,.15)}
.agsel{min-width:150px} .aginp{flex:1;min-width:190px}
.agsel:focus,.aginp:focus{outline:none;border-color:rgba(0,230,255,.5)}
.agout{display:none;margin-top:14px;padding:14px;border-radius:12px;
background:rgba(11,16,32,.75);border:1px solid rgba(148,163,184,.15)}
.agout.on{display:block}
.agout.ok{border-color:rgba(34,197,94,.4)}
.agout.warn{border-color:rgba(245,158,11,.45)}
.agout.err{border-color:rgba(239,68,68,.45)}
.agsay{font-size:13.5px;line-height:1.6;color:#F8FAFC;margin-bottom:12px}
.agfiles{display:flex;flex-direction:column;gap:7px}
.agf{padding:9px 12px;border-radius:10px;background:rgba(7,11,20,.65);
border-left:3px solid rgba(148,163,184,.3)}
.agf b{display:block;font-size:12.5px;color:#F8FAFC}
.agf i{display:block;font-size:11px;color:#94A3B8;font-style:normal;
margin-top:3px;line-height:1.5}
.agf u{display:inline-block;font-size:9.5px;color:#64748B;
text-decoration:none;margin-top:5px;padding:2px 7px;border-radius:5px;
background:rgba(124,58,237,.13)}
.agf.ok{border-left-color:#22C55E} .agf.ok b{color:#22C55E}
.agf.bad{border-left-color:#F59E0B} .agf.bad b{color:#F59E0B}
.agf.warn{border-left-color:#EF4444} .agf.warn b{color:#EF4444}
.agmeta{margin-top:10px;font-size:10.5px;color:#64748B}
.agask{margin-top:13px;padding:13px;border-radius:11px;
background:linear-gradient(135deg,rgba(124,58,237,.14),rgba(0,230,255,.07));
border:1px solid rgba(124,58,237,.35)}
.agask b{display:block;font-size:13.5px;color:#F8FAFC;margin-bottom:10px}
.agbtns{display:flex;gap:8px;flex-wrap:wrap}
@media(max-width:640px){.agrow{flex-direction:column;align-items:stretch}
.agsel,.aginp{width:100%}}
.bosslock{text-align:center;padding:34px 24px}
.bltop{width:74px;height:74px;margin:0 auto 16px;border-radius:20px;
display:flex;align-items:center;justify-content:center;color:#F8FAFC;
background:linear-gradient(135deg,#7C3AED,#8B5CF6,#EC4899);
box-shadow:0 0 38px rgba(124,58,237,.5)}
.bosslock h2{font-size:22px;letter-spacing:3px;margin:0}
.bosslock p{max-width:520px;margin:0 auto}
.blgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;
max-width:460px;margin:18px auto 0}
.blgrid div{padding:12px 6px;border-radius:11px;background:rgba(11,16,32,.6);
border:1px solid rgba(148,163,184,.15)}
.blgrid b{display:block;font-size:19px;color:#00E6FF}
.blgrid i{font-size:9.5px;color:#94A3B8;font-style:normal}
.blwarn{padding:11px 15px;border-radius:11px;font-size:12.5px;color:#F59E0B;
background:rgba(245,158,11,.09);border:1px solid rgba(245,158,11,.3);
display:inline-flex;align-items:center;gap:8px}
.blperks{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;
max-width:620px;margin:0 auto}
.blperks div{display:flex;align-items:center;gap:9px;padding:10px 12px;
border-radius:11px;text-align:left;background:rgba(11,16,32,.6);
border:1px solid rgba(148,163,184,.13)}
.blperks b{font-size:17px;line-height:1}
.blperks span{font-size:11px;color:#CBD5E1;line-height:1.4}
@media(max-width:640px){.blperks{grid-template-columns:1fr}}
.bltab{width:100%;max-width:530px;margin:0 auto;border-collapse:collapse;
font-size:12px}
.bltab th{padding:8px;color:#64748B;font-size:10px;letter-spacing:.7px;
border-bottom:1px solid rgba(148,163,184,.15)}
.bltab td{padding:8px;color:#CBD5E1;text-align:center;
border-bottom:1px solid rgba(148,163,184,.07)}
.bltab td:first-child{text-align:left;color:#F8FAFC}
.bltab .no{color:#EF4444} .bltab .ye{color:#22C55E}
.bltab tr.hl td{background:rgba(124,58,237,.12)}
@media(max-width:640px){.blgrid{grid-template-columns:repeat(2,1fr)}
.bosshead{flex-direction:column;align-items:flex-start}}
.afbox{padding:13px;border-radius:12px;border:1px solid rgba(148,163,184,.15);
background:linear-gradient(135deg,rgba(124,58,237,.07),rgba(0,230,255,.04))}
.afbox:hover{border-color:rgba(124,58,237,.50)}
.afrow{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}
.afrow b{font-size:13px;color:#F8FAFC;display:flex;align-items:center;gap:6px}
.afrow p{margin:5px 0 0;line-height:1.55;max-width:430px}
.afout{display:none;margin-top:11px;padding:11px 13px;border-radius:10px;
font-size:12px;line-height:1.6;background:rgba(11,16,32,.75);
border:1px solid rgba(148,163,184,.15)}
.afout.on{display:block}
.afout.ok{border-color:rgba(34,197,94,.45);background:rgba(34,197,94,.07)}
.afout.warn{border-color:rgba(245,158,11,.45);background:rgba(245,158,11,.07)}
.afout.err{border-color:rgba(239,68,68,.45);background:rgba(239,68,68,.07)}
.cdout{display:none;margin-top:14px;padding:14px;border-radius:12px;
background:rgba(0,0,0,.28);border:1px solid var(--line);animation:cdin .3s}
.cdout.on,.cdout:not(:empty){display:block}
@keyframes cdin{from{opacity:0;transform:translateY(-6px)}}
.cdload{display:flex;align-items:center;gap:8px;color:var(--dim);
font-size:13px;padding:6px 0}
.cdload i{width:7px;height:7px;border-radius:50%;background:var(--cy);
animation:cdb 1.1s ease-in-out infinite}
.cdload i:nth-child(2){background:var(--acc);animation-delay:.16s}
.cdload i:nth-child(3){background:var(--pk);animation-delay:.32s}
@keyframes cdb{0%,100%{opacity:.25;transform:scale(.7)}
50%{opacity:1;transform:scale(1)}}
.cdhead{display:flex;align-items:center;gap:10px;padding:10px 12px;
border-radius:10px;margin-bottom:9px}
.cdhead b{flex:1;font-size:13.5px;line-height:1.5}
.cdhead.good{background:rgba(34,197,94,.1);
border-left:3px solid var(--ok)}
.cdhead.warn{background:rgba(245,158,11,.1);
border-left:3px solid var(--warn)}
.cdhead.bad{background:rgba(239,68,68,.1);border-left:3px solid var(--err)}
.cdsev,.cdscore{font-size:10px;letter-spacing:1px;font-weight:800;
padding:3px 8px;border-radius:6px;background:rgba(255,255,255,.08);
white-space:nowrap}
.cdwhy{font-size:12.5px;color:var(--dim);margin-bottom:9px;line-height:1.6}
.cdv{font-size:13px;color:var(--dim);margin-bottom:10px}
.cdfix{padding:9px 12px;border-radius:9px;font-size:13px;
background:rgba(0,230,255,.07);border-left:2px solid var(--cy);
color:var(--txt);line-height:1.6}
.cdcode{margin-top:10px;padding:12px;border-radius:10px;font-size:11.5px;
background:rgba(0,0,0,.45);border:1px solid var(--line);overflow-x:auto;
max-height:270px;overflow-y:auto;color:#9fe8ff;line-height:1.55;
font-family:ui-monospace,monospace;white-space:pre}
.cdiss{display:flex;flex-direction:column;gap:5px;margin-top:4px}
.cdi{display:flex;align-items:flex-start;gap:8px;padding:8px 10px;
border-radius:9px;font-size:12.3px;background:rgba(255,255,255,.03);
line-height:1.5}
.cdi.high{border-left:2px solid var(--err)}
.cdi.medium{border-left:2px solid var(--warn)}
.cdi.low{border-left:2px solid var(--dim3)}
.cdt{font-size:9.5px;letter-spacing:.9px;font-weight:800;padding:2px 6px;
border-radius:5px;background:rgba(124,58,237,.22);color:var(--acc4);
text-transform:uppercase;white-space:nowrap;flex-shrink:0}
.cdi i{font-style:normal;font-size:10px;color:var(--dim3);
margin-left:auto;white-space:nowrap}
.cdok{padding:10px 12px;border-radius:9px;font-size:13px;
background:rgba(34,197,94,.1);border-left:3px solid var(--ok);
color:var(--txt)}
.cderr{padding:10px 12px;border-radius:9px;font-size:13px;
background:rgba(239,68,68,.1);border-left:3px solid var(--err);
color:var(--txt)}

/* 🤖 JARVIS link */
.jvlink{width:38px;height:38px;border-radius:10px;display:grid;
place-items:center;color:var(--cy);position:relative;
background:linear-gradient(160deg,rgba(0,230,255,.12),rgba(124,58,237,.08));
border:1px solid rgba(0,230,255,.3);transition:.24s var(--ease)}
.jvlink:hover{border-color:var(--cy);box-shadow:0 0 20px var(--bglow);
transform:translateY(-1px)}
.jvlink::after{content:'';position:absolute;top:-2px;right:-2px;width:6px;
height:6px;border-radius:50%;background:#22C55E;box-shadow:0 0 7px #22C55E;
animation:bp 2.2s infinite}

/* ⋮ THREE-DOT MENU */
.dmwrap{position:relative;display:inline-flex}
.dmbtn{width:38px;height:38px;border-radius:10px;cursor:pointer;
display:flex;flex-direction:column;align-items:center;justify-content:center;
gap:3.5px;background:linear-gradient(160deg,var(--card),var(--bg2));
border:1px solid var(--line);transition:.24s var(--ease)}
.dmbtn i{width:4px;height:4px;border-radius:50%;background:var(--dim);
display:block;transition:.24s var(--ease)}
.dmbtn:hover{border-color:var(--line2);box-shadow:0 0 20px var(--glow)}
.dmbtn:hover i{background:var(--acc4)}
.dmbtn:hover i:nth-child(1){transform:translateY(-1px)}
.dmbtn:hover i:nth-child(3){transform:translateY(1px)}
.dmbtn.on{background:var(--g1);border-color:transparent;
box-shadow:0 4px 22px var(--glow)}
.dmbtn.on i{background:#fff}
.dmbtn.on i:nth-child(1){transform:translateY(7.5px) rotate(45deg);
width:16px;height:2px;border-radius:2px}
.dmbtn.on i:nth-child(2){opacity:0;transform:scale(0)}
.dmbtn.on i:nth-child(3){transform:translateY(-7.5px) rotate(-45deg);
width:16px;height:2px;border-radius:2px}

.dmback{position:fixed;inset:0;z-index:490;background:rgba(7,11,20,.72);
backdrop-filter:blur(5px);opacity:0;pointer-events:none;transition:.28s}
.dmback.on{opacity:1;pointer-events:auto}

/* ⚠️ position:absolute tha — parent nav ke hisaab se lagta tha.
   Phone pe agar browser "Desktop site" mode me ho (jo user
   aksar on kar leta hai) to viewport 1000px+ ho jata hai,
   media query lagti hi nahi, aur panel screen se BAHAR chala
   jata hai — teesra column kat jata hai ("Depl...", "Code...").
   Screenshot me yahi dikha tha.

   Ab position:fixed — hamesha asli screen ke andar. */
.dmpanel{position:fixed;top:58px;right:12px;
width:min(420px,calc(100vw - 24px));
max-height:min(74vh,620px);z-index:500;border-radius:16px;overflow:hidden;
background:linear-gradient(165deg,var(--card),var(--bg2));
border:1px solid var(--line2);box-shadow:var(--sh2),0 0 50px var(--glow);
opacity:0;transform:translateY(-10px) scale(.96);pointer-events:none;
transition:.28s var(--ease);display:flex;flex-direction:column}
.dmpanel.on{opacity:1;transform:none;pointer-events:auto}
.dmpanel::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;
background:linear-gradient(90deg,transparent,rgba(0,230,255,.6),
rgba(124,58,237,.6),rgba(255,0,128,.4),transparent)}

.dmtop{display:flex;align-items:center;justify-content:space-between;
padding:13px 16px;border-bottom:1px solid var(--line);background:var(--bg2);
flex-shrink:0}
.dmtop b{display:flex;align-items:center;gap:8px;font-size:13.5px}
.dmtop svg{color:var(--acc4)}
.dmx{background:none;border:0;color:var(--dim2);cursor:pointer;padding:4px;
border-radius:7px;display:flex}
.dmx:hover{color:var(--txt);background:var(--card2)}

.dmbody{overflow-y:auto;padding:8px 10px 4px;flex:1}
.dmbody::-webkit-scrollbar{width:5px}
.dmbody::-webkit-scrollbar-thumb{background:var(--line2);border-radius:9px}
.dmg{margin-bottom:9px}
.dmh{font-size:9.5px;letter-spacing:1.6px;color:var(--dim3);font-weight:800;
padding:7px 8px 5px}
/* ⚠️ repeat(3,1fr) fix tha — chhote panel me teen column
   thuns jate the aur naam kat jate the. Ab auto-fit:
   jitni jagah hai utne column banenge, apne aap. */
.dmr{display:grid;
grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:5px}
.dmi{display:flex;align-items:center;gap:9px;padding:9px 10px;
border-radius:10px;transition:.18s var(--ease);border:1px solid transparent}
.dmi:hover{background:var(--card2);border-color:rgba(124,58,237,.28)}
.dmi.on{background:linear-gradient(90deg,rgba(124,58,237,.18),
rgba(0,230,255,.06));border-color:rgba(124,58,237,.4)}
.dmic{width:30px;height:30px;border-radius:9px;flex-shrink:0;display:grid;
place-items:center;color:var(--acc4);
background:linear-gradient(135deg,rgba(124,58,237,.2),rgba(0,230,255,.1))}
.dmi.on .dmic{background:var(--g3);color:#fff}
.dmt{display:flex;flex-direction:column;min-width:0;gap:1px}
.dmt b{font-size:12.8px;font-weight:640;color:var(--txt);
white-space:normal;overflow-wrap:anywhere;line-height:1.25}
.dmt i{font-style:normal;font-size:10.5px;color:var(--dim2);
white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

.dmf{display:flex;align-items:center;gap:9px;padding:11px 14px;
border-top:1px solid var(--line);background:var(--bg2);flex-shrink:0}
.dmf .dim{margin-left:auto;overflow:hidden;text-overflow:ellipsis;
white-space:nowrap}
/* Chhoti screen pe bottom-sheet — neeche se upar aata hai.
   ⚠️ 560px kam tha: "Desktop site" mode me viewport bada ho
   jata hai. Ab 820px — dono haalat me sahi. */
@media(max-width:820px){
.dmpanel{position:fixed;top:auto;bottom:0;right:0;left:0;width:100%;
max-height:82vh;border-radius:18px 18px 0 0;
transform:translateY(100%) scale(1)}
.dmpanel.on{transform:none}
.dmr{grid-template-columns:1fr 1fr}}

/* Bahut chhota — ek hi column, kuch na kate */
@media(max-width:400px){.dmr{grid-template-columns:1fr}}

/* LIVE BAR — har dashboard page par */
.livebar{display:grid;grid-template-columns:repeat(5,1fr);gap:1px;
background:var(--line);border:1px solid var(--line);
border-radius:var(--r2);overflow:hidden;margin-bottom:20px;
position:relative}
.livebar::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;
background:linear-gradient(90deg,transparent,rgba(0,230,255,.6),
rgba(124,58,237,.6),rgba(255,0,128,.4),transparent);z-index:2;
animation:lbsweep 4s linear infinite}
@keyframes lbsweep{0%{opacity:.3}50%{opacity:1}100%{opacity:.3}}
.lvc{background:linear-gradient(160deg,var(--card),var(--bg2));
padding:11px 14px;display:flex;flex-direction:column;gap:5px}
.lvt{display:flex;align-items:center;gap:6px;font-size:10px;
letter-spacing:1.1px;color:var(--dim2);font-weight:700}
.lvt svg{color:var(--acc3)}
.lvv{display:flex;align-items:baseline;gap:4px}
.lvv b{font-size:19px;font-weight:800;letter-spacing:-.5px;
font-variant-numeric:tabular-nums;color:var(--txt)}
.lvv i{font-style:normal;font-size:10.5px;color:var(--dim2)}
.lvn{font-size:10.5px;color:var(--dim2);font-variant-numeric:tabular-nums}
.lvn b{color:var(--dim);font-weight:700}
.lvb{height:4px;background:rgba(255,255,255,.06);border-radius:99px;
overflow:hidden;margin-top:2px}
.lvb i{display:block;height:100%;border-radius:99px;
transition:width .6s var(--ease);box-shadow:0 0 8px currentColor}
.lvb.y i{background:var(--warn)!important}
.lvb.r i{background:var(--err)!important}
@media(max-width:900px){.livebar{grid-template-columns:repeat(2,1fr)}
.lvend{grid-column:span 2}}

/* CARD */
.card{background:linear-gradient(160deg,var(--card),var(--bg2));
border:1px solid var(--line);border-radius:var(--r);padding:24px;
transition:.28s var(--ease);position:relative;overflow:hidden}
.card::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;
background:linear-gradient(90deg,transparent,rgba(124,58,237,.55),
rgba(0,230,255,.45),transparent);opacity:0;transition:.32s var(--ease)}
.card:hover::before{opacity:1}
.card:hover{border-color:var(--line2);transform:translateY(-3px);
box-shadow:var(--sh2),0 0 34px rgba(124,58,237,.14)}
.card.flat:hover{transform:none;box-shadow:none}
.card.glow{border-color:rgba(124,58,237,.45);
box-shadow:0 0 50px rgba(124,58,237,.16),inset 0 1px 0 rgba(139,92,246,.14)}
.card.glow::before{opacity:1}
.card.cy{border-color:rgba(0,230,255,.3)}
.card.cy::before{background:linear-gradient(90deg,transparent,
rgba(0,230,255,.6),transparent);opacity:1}
.grid{display:grid;gap:18px}
.g2{grid-template-columns:repeat(2,1fr)}
.g3{grid-template-columns:repeat(3,1fr)}
.g4{grid-template-columns:repeat(4,1fr)}
.g23{grid-template-columns:2fr 1fr}
.g32{grid-template-columns:1fr 2fr}

/* STAT */
.stat{background:linear-gradient(160deg,var(--card),var(--bg3));
border:1px solid var(--line);border-radius:var(--r);padding:20px;
transition:.28s var(--ease);overflow:hidden;position:relative}
.stat:hover{border-color:var(--line2);transform:translateY(-3px);
box-shadow:var(--sh)}
.stat .top{display:flex;align-items:center;justify-content:space-between;
margin-bottom:10px}
.stat .lbl{color:var(--dim2);font-size:11px;font-weight:750;
letter-spacing:1.1px;text-transform:uppercase}
.stat .ib{width:32px;height:32px;border-radius:9px;display:grid;
place-items:center;background:rgba(124,58,237,.11);color:var(--acc3)}
.stat .ib.g{background:rgba(34,197,94,.11);color:#22C55E}
.stat .ib.y{background:rgba(245,158,11,.11);color:#8B5CF6}
.stat .ib.p{background:rgba(139,92,246,.11);color:var(--pu)}
.stat .ib.c{background:rgba(0,230,255,.11);color:var(--cy)}
.stat .val{font-size:31px;font-weight:820;letter-spacing:-1.1px;line-height:1.1}
.stat .sub{color:var(--dim);font-size:12.5px;margin-top:3px;
display:flex;align-items:center;gap:5px}
.stat .chart{margin-top:10px;margin-bottom:-6px;opacity:.9}
.up{color:#22C55E}.down{color:#FF6B8A}

/* CHARTS */
.spark,.mbars{display:block;width:100%}
.donut{position:relative;display:inline-grid;place-items:center}
.dctr{position:absolute;text-align:center;line-height:1.16}
.dctr b{font-size:23px;font-weight:820;display:block;letter-spacing:-.6px}
.dctr span{font-size:10.5px;color:var(--dim2);text-transform:uppercase;
letter-spacing:1px;font-weight:700}
.dring{transition:stroke-dashoffset 1s var(--ease)}
.gauge{display:block;margin:0 auto}
.bar{height:7px;background:var(--bg2);border-radius:99px;overflow:hidden;
margin:8px 0}
.bar i{display:block;height:100%;border-radius:99px;
background:linear-gradient(90deg,var(--acc),var(--cy));
transition:width .9s var(--ease)}
.bar i{box-shadow:0 0 10px currentColor}
.bar.y i{background:linear-gradient(90deg,var(--warn),#FBBF24)}
.bar.r i{background:linear-gradient(90deg,var(--err),#FF6B8A)}
.bar.sm{height:5px}

/* SECTION */
.sec{padding:80px 0;position:relative}
.sec.alt{background:linear-gradient(180deg,transparent,var(--bg2) 18%,
var(--bg2) 82%,transparent)}
.shead{text-align:center;margin-bottom:52px}
.stag{display:inline-block;padding:5px 14px;border-radius:99px;
background:rgba(124,58,237,.1);border:1px solid rgba(124,58,237,.24);
color:var(--acc3);font-size:11.5px;font-weight:750;letter-spacing:1.2px;
text-transform:uppercase;margin-bottom:16px}
.shead h2{font-size:clamp(26px,4.2vw,40px);font-weight:830;
letter-spacing:-1.2px;line-height:1.16}
.shead p{color:var(--dim);margin:13px auto 0;max-width:560px;font-size:16px}

/* FEATURE */
.feat{background:linear-gradient(160deg,var(--card),var(--bg3));
border:1px solid var(--line);border-radius:var(--r);padding:24px;
transition:.28s var(--ease)}
.feat:hover{transform:translateY(-4px);border-color:var(--line2);
box-shadow:var(--sh)}
.feat .fi{width:44px;height:44px;border-radius:12px;display:grid;
place-items:center;margin-bottom:15px;
background:linear-gradient(135deg,rgba(124,58,237,.16),rgba(0,230,255,.08));
border:1px solid rgba(124,58,237,.2);color:var(--acc3)}
.feat h3{font-size:16.5px;font-weight:720;margin-bottom:7px}
.feat p{color:var(--dim);font-size:14px;line-height:1.62}

/* PRICING */
.plan{background:linear-gradient(165deg,var(--card),var(--bg3));
border:1px solid var(--line);border-radius:19px;padding:30px 24px;
position:relative;transition:.3s var(--ease)}
.plan:hover{transform:translateY(-6px);border-color:var(--line2);
box-shadow:var(--sh2)}
.plan.hot{border-color:rgba(124,58,237,.5);
background:linear-gradient(165deg,rgba(124,58,237,.07),var(--bg3));
box-shadow:0 0 50px rgba(124,58,237,.11)}
.plan .tag{position:absolute;top:-11px;left:50%;transform:translateX(-50%);
background:linear-gradient(135deg,var(--acc3),var(--acc2));color:#fff;
padding:5px 15px;border-radius:99px;font-size:10.5px;font-weight:820;
letter-spacing:1.1px;box-shadow:0 3px 14px var(--glow);white-space:nowrap}
.plan h3{font-size:17px;font-weight:750}
.plan .pr{font-size:40px;font-weight:850;letter-spacing:-1.8px;
margin:12px 0 2px;line-height:1}
.plan .pr small{font-size:14px;color:var(--dim);font-weight:500;
letter-spacing:0}
.plan .spec{color:var(--dim2);font-size:12.8px;margin-bottom:18px}
.plan ul{list-style:none;margin:18px 0 22px}
.plan li{padding:6.5px 0;color:var(--dim);font-size:13.8px;
display:flex;align-items:center;gap:9px}
.plan li svg{color:var(--acc);flex-shrink:0}
.plan li.no{opacity:.42}
.plan li.no svg{color:var(--dim2)}

/* FORM */
.auth{min-height:calc(100vh - 68px);display:grid;place-items:center;
padding:44px 20px}
.box{background:linear-gradient(165deg,var(--card),var(--bg3));
border:1px solid var(--line);border-radius:20px;padding:38px;width:100%;
max-width:440px;box-shadow:var(--sh2)}
.box .bh{text-align:center;margin-bottom:26px}
.box h2{font-size:25px;font-weight:800;margin:14px 0 5px;letter-spacing:-.6px}
.box .s{color:var(--dim);font-size:14px}
.fld{margin-bottom:15px}
.fld label{display:block;font-size:12.5px;color:var(--dim);margin-bottom:7px;
font-weight:650;letter-spacing:.2px}
.fld input,.fld select,.fld textarea{width:100%;padding:12px 14px;
background:var(--bg2);border:1px solid var(--line2);border-radius:var(--r3);
color:var(--txt);font-size:14.5px;transition:.2s}
.fld input:focus,.fld select:focus,.fld textarea:focus{outline:0;
border-color:var(--acc);box-shadow:0 0 0 3px rgba(124,58,237,.13);
background:var(--bg3)}
.fld input::placeholder,.fld textarea::placeholder{color:var(--dim2)}
.fld textarea{resize:vertical;min-height:110px;line-height:1.6}
.fld .hint{font-size:12px;color:var(--dim2);margin-top:5px}
.msg{padding:13px 16px;border-radius:var(--r2);margin-bottom:18px;
font-size:13.8px;display:flex;gap:10px;align-items:flex-start;line-height:1.55}
.msg svg{flex-shrink:0;margin-top:2px}
.msg.err{background:rgba(239,68,68,.09);border:1px solid rgba(239,68,68,.26);
color:#FF8FA8}
.msg.ok{background:rgba(34,197,94,.09);border:1px solid rgba(34,197,94,.26);
color:#4ADE80}
.msg.warn{background:rgba(245,158,11,.09);border:1px solid rgba(245,158,11,.26);
color:#A78BFA}
.msg.info{background:rgba(124,58,237,.08);border:1px solid rgba(124,58,237,.24);
color:var(--acc4)}

/* DASHBOARD */
/* ⚠️ Drawer ka "Menu ✕" header DESKTOP pe nahi dikhna chahiye.
   Pehle ye sirf mobile media-query me define tha, isliye desktop
   pe browser ne default (visible) le liya aur sidebar ke upar
   "Menu ✕" chipak gaya. Screenshot dekh kar hi pakda —
   automated test me nahi dikha tha. */
.sdclose{display:none}
.sdim{display:none}
.dash{display:grid;grid-template-columns:246px 1fr;
min-height:calc(100vh - 68px)}
.side{background:var(--bg2);border-right:1px solid var(--line);
padding:18px 0 30px;position:sticky;top:68px;height:calc(100vh - 68px);
overflow-y:auto}
.side::-webkit-scrollbar{width:5px}
.side::-webkit-scrollbar-thumb{background:var(--line2);border-radius:9px}
.side a{display:flex;align-items:center;gap:11px;padding:10px 20px;
margin:1px 10px;border-radius:var(--r3);color:var(--dim);font-size:14px;
font-weight:550;transition:.18s var(--ease)}
.side a:hover{background:var(--card2);color:var(--txt)}
.side a.on{background:linear-gradient(90deg,rgba(124,58,237,.16),
rgba(124,58,237,.05));color:var(--acc3);font-weight:650}
.side a.on svg{color:var(--acc4)}
.side a.on{position:relative}
.side a.on::before{content:'';position:absolute;left:0;top:6px;bottom:6px;
width:3px;border-radius:0 3px 3px 0;background:var(--g3);
box-shadow:0 0 12px var(--glow)}
.side .hd{padding:16px 22px 7px;font-size:10.5px;color:var(--dim2);
text-transform:uppercase;letter-spacing:1.3px;font-weight:780}
.side .bal{margin:12px 14px 4px;padding:14px;border-radius:var(--r2);
background:linear-gradient(140deg,rgba(124,58,237,.14),rgba(0,230,255,.05));
border:1px solid rgba(124,58,237,.22)}
.side .bal .l{font-size:10.5px;color:var(--dim);letter-spacing:1px;
text-transform:uppercase;font-weight:700}
.side .bal .v{font-size:24px;font-weight:830;letter-spacing:-.8px;
margin:2px 0 8px}
.main{padding:28px 32px 56px;min-width:0}
.ph{display:flex;align-items:flex-start;justify-content:space-between;
margin-bottom:24px;flex-wrap:wrap;gap:14px}
.ph h1{font-size:25px;font-weight:800;letter-spacing:-.7px;
display:flex;align-items:center;gap:11px}
.ph p{color:var(--dim);font-size:14px;margin-top:3px}

/* TABLE */
.tbl{background:linear-gradient(160deg,var(--card),var(--bg3));
border:1px solid var(--line);border-radius:var(--r);overflow:hidden}
.tbl .th{padding:18px 20px;border-bottom:1px solid var(--line);
display:flex;align-items:center;justify-content:space-between;gap:12px}
.tbl .th h3{font-size:15.5px;font-weight:720;display:flex;
align-items:center;gap:9px}
table{width:100%;border-collapse:collapse;font-size:14px}
th{text-align:left;padding:11px 18px;color:var(--dim2);font-size:11px;
text-transform:uppercase;letter-spacing:.9px;font-weight:750;
border-bottom:1px solid var(--line);background:rgba(0,0,0,.14)}
td{padding:14px 18px;border-bottom:1px solid var(--line)}
tbody tr:last-child td{border-bottom:0}
tbody tr{transition:.15s}
tbody tr:hover{background:rgba(124,58,237,.035)}

/* BADGE */
.bdg{display:inline-flex;align-items:center;gap:6px;padding:4px 11px;
border-radius:7px;font-size:11.5px;font-weight:720;letter-spacing:.2px}
.bdg::before{content:'';width:6px;height:6px;border-radius:50%;
background:currentColor}
.bdg.on{background:rgba(34,197,94,.13);color:#22C55E}
.bdg.on::before{animation:bp 2s infinite;
box-shadow:0 0 0 3px rgba(34,197,94,.14)}
.bdg.off{background:rgba(148,165,189,.11);color:var(--dim)}
.bdg.err{background:rgba(239,68,68,.13);color:#FF6B8A}
.bdg.wait{background:rgba(245,158,11,.13);color:#8B5CF6}
.bdg.info{background:rgba(124,58,237,.13);color:var(--acc3)}
.bdg.vip{background:rgba(139,92,246,.13);color:var(--pu)}
.bdg.nd::before{display:none}

/* CONSOLE */
.console{background:#050810;border:1px solid var(--line);
border-radius:var(--r2);padding:15px 17px;
font-family:'JetBrains Mono','Cascadia Code',Consolas,monospace;
font-size:12.6px;line-height:1.75;height:440px;overflow-y:auto}
.console::-webkit-scrollbar{width:9px}
.console::-webkit-scrollbar-track{background:#050a13}
.console::-webkit-scrollbar-thumb{background:#1f2c40;border-radius:9px}
.console::-webkit-scrollbar-thumb:hover{background:#2a3a52}
.cl{display:flex;gap:10px;padding:1px 0;animation:fin .22s var(--ease)}
@keyframes fin{from{opacity:0;transform:translateY(3px)}}
.cl .ts{color:#3a4d69;flex-shrink:0;font-size:11px;
padding-top:1px;user-select:none}
.cl .tx{white-space:pre-wrap;word-break:break-word;flex:1}
.cl.out .tx{color:#CBD5E1}
.cl.ok .tx{color:#22C55E;font-weight:600}
.cl.err .tx{color:#FF6B8A}
.cl.warn .tx{color:#8B5CF6}
.cl.cmd .tx{color:var(--acc3);font-weight:700}
.live{display:inline-flex;align-items:center;gap:7px;font-size:11.5px;
color:#22C55E;font-weight:650}
.live i{width:6px;height:6px;border-radius:50%;background:#22C55E;
animation:bp 1.5s infinite;display:block;
box-shadow:0 0 0 3px rgba(34,197,94,.16)}
.cin{display:flex;gap:9px;margin-top:12px}
.cin input{flex:1;padding:11px 15px;background:#050810;
border:1px solid var(--line2);border-radius:var(--r3);color:var(--acc4);
font-family:'JetBrains Mono',monospace;font-size:13px}
.cin input:focus{outline:0;border-color:var(--acc);
box-shadow:0 0 0 3px rgba(124,58,237,.12)}

/* UPLOAD */
.drop{border:2px dashed var(--line2);border-radius:var(--r);padding:38px 20px;
text-align:center;transition:.26s var(--ease);cursor:pointer;
background:var(--bg2);display:block}
.drop:hover,.drop.over{border-color:var(--acc);
background:rgba(124,58,237,.055);transform:scale(1.008)}
.drop .di{width:56px;height:56px;border-radius:16px;margin:0 auto 13px;
display:grid;place-items:center;color:var(--acc3);
background:linear-gradient(135deg,rgba(124,58,237,.15),rgba(0,230,255,.06));
border:1px solid rgba(124,58,237,.22)}
.drop b{font-size:15px;display:block;margin-bottom:5px}

/* FILE ROW */
.fr{display:flex;align-items:center;gap:12px;padding:11px 18px;
border-bottom:1px solid var(--line);transition:.15s}
.fr:hover{background:rgba(124,58,237,.035)}
.fr:last-child{border-bottom:0}
.fr .fi2{color:var(--dim);flex-shrink:0}
.fr .nm{flex:1;font-size:13.8px;word-break:break-all}
.fr .nm:hover{color:var(--acc3)}
.fr .sz{color:var(--dim2);font-size:12px;font-variant-numeric:tabular-nums}

/* STEPS */
.steps{display:flex;flex-direction:column;gap:2px}
.step{display:flex;gap:14px;padding:13px 0;align-items:flex-start;
position:relative}
.step:not(:last-child)::after{content:'';position:absolute;left:15px;top:42px;
bottom:-2px;width:1.5px;background:var(--line)}
.step.done:not(:last-child)::after{background:var(--acc)}
.step .n{width:31px;height:31px;border-radius:50%;background:var(--card2);
display:grid;place-items:center;font-weight:800;font-size:13px;flex-shrink:0;
border:1.5px solid var(--line2);color:var(--dim);z-index:1;
transition:.3s var(--ease)}
.step.done .n{background:linear-gradient(135deg,var(--acc3),var(--acc2));
color:#fff;border-color:var(--acc);box-shadow:0 0 0 4px rgba(124,58,237,.13)}
.step.now .n{border-color:var(--acc);color:var(--acc3);
box-shadow:0 0 0 4px rgba(124,58,237,.1);animation:bp 2.2s infinite}
.step .sc b{font-size:14.5px;font-weight:680}
.step .sc p{color:var(--dim);font-size:13px;margin-top:2px}

/* MISC */
.empty{text-align:center;padding:60px 24px}
.empty .ei{width:66px;height:66px;border-radius:19px;margin:0 auto 16px;
display:grid;place-items:center;color:var(--dim2);background:var(--card2);
border:1px solid var(--line)}
.empty h3{font-size:18px;font-weight:720;margin-bottom:6px}
.empty p{color:var(--dim);margin-bottom:20px;font-size:14.5px}
code{background:var(--bg2);padding:2.5px 8px;border-radius:6px;
font-size:12.6px;color:var(--acc3);font-family:'JetBrains Mono',monospace;
border:1px solid var(--line)}
.flex{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.between{justify-content:space-between}
.mt{margin-top:20px}.mt2{margin-top:12px}.mb{margin-bottom:20px}
.mb2{margin-bottom:12px}
.tc{text-align:center}.dim{color:var(--dim)}.dim2{color:var(--dim2)}
.sm{font-size:12.8px}.xs{font-size:11.8px}
.big{font-size:30px;font-weight:830;letter-spacing:-1px;line-height:1.12}
.tab{display:flex;gap:6px;flex-wrap:wrap;padding:5px;background:var(--bg2);
border:1px solid var(--line);border-radius:var(--r2);margin-bottom:20px}
.tab a{padding:8px 15px;border-radius:8px;font-size:13.2px;color:var(--dim);
font-weight:600;transition:.18s;display:flex;align-items:center;gap:7px}
.tab a:hover{color:var(--txt);background:var(--card2)}
.tab a.on{background:linear-gradient(135deg,var(--acc3),var(--acc2));
color:#fff;box-shadow:0 2px 10px var(--glow)}
.acc{border:1px solid var(--line);border-radius:var(--r2);
margin-bottom:10px;overflow:hidden;background:var(--card)}
.acc summary{padding:17px 20px;cursor:pointer;font-weight:650;font-size:15px;
list-style:none;display:flex;justify-content:space-between;
align-items:center;transition:.18s}
.acc summary::-webkit-details-marker{display:none}
.acc summary:hover{background:var(--card2)}
.acc summary::after{content:'+';font-size:21px;color:var(--acc);
font-weight:400;transition:.28s var(--ease)}
.acc[open] summary::after{transform:rotate(45deg)}
.acc .ac{padding:0 20px 18px;color:var(--dim);font-size:14.2px;line-height:1.7}
.split{display:grid;grid-template-columns:1fr 1fr;gap:0;
border:1px solid var(--line);border-radius:var(--r);overflow:hidden}
.split>div{padding:24px}
.split>div:first-child{border-right:1px solid var(--line)}

/* FOOTER */
footer{border-top:1px solid var(--line);padding:52px 0 28px;margin-top:70px;
background:var(--bg2)}
.fg{display:grid;grid-template-columns:2.2fr 1fr 1fr 1fr;gap:38px;
margin-bottom:36px}
.fg h4{font-size:13px;margin-bottom:15px;font-weight:750;
letter-spacing:.4px}
.fg a,.fg p{display:block;color:var(--dim);font-size:13.8px;
margin-bottom:9px;transition:.18s}
.fg a:hover{color:var(--acc3);transform:translateX(2px)}
.fbot{display:flex;justify-content:space-between;align-items:center;
color:var(--dim2);font-size:12.8px;padding-top:24px;
border-top:1px solid var(--line);flex-wrap:wrap;gap:12px}

/* ═══════════════════════════════════════════════════════
   📱 MOBILE — asli app jaisa
   ═══════════════════════════════════════════════════════

   ⚠️ PEHLE KYA GALAT THA (user ki shikayat: "desktop mode pe
      hi sab dikhta hai"):

      • .side (16 links wala sidebar) 1080px pe display:none
        ho jata tha — par uska koi replacement nahi tha
      • .nlinks (burger menu) me sirf 5 link the aur wo bhi
        720px se neeche hi dikhta tha
      • Matlab 720-1080px ke beech NA sidebar, NA burger —
        user sirf ⋮ menu se hi kahin ja sakta tha
      • Free Server, Wallet, Storage, Analytics, Profile —
        ye sab mobile pe pahunch se BAAHAR the

   ✅ AB:
      • Sidebar ek DRAWER ban jata hai (baayein se aata hai)
      • Neeche ek BOTTOM BAR — 5 sabse zaroori kaam, hamesha
      • Table apne aap card ban jaati hai (kata hua nahi)
      • Har button kam se kam 44px — ungli se dabaने layak
   ═══════════════════════════════════════════════════════ */

@media(max-width:1080px){
.g4{grid-template-columns:repeat(2,1fr)}
.g23,.g32{grid-template-columns:1fr}
.dash{grid-template-columns:1fr}

/* Sidebar ab DRAWER — gayab nahi hota, chhup jata hai */
/* ⚠️ z-index nav (100) se ZYADA hona chahiye, warna drawer ka
   "Menu ✕" header nav ke peeche chhup jata hai. Screenshot me
   yahi dikha tha. */
.side{position:fixed;top:0;left:0;bottom:0;width:276px;z-index:1200;
height:100vh;padding-top:14px;transform:translateX(-102%);
transition:transform .26s var(--ease);box-shadow:0 0 40px rgba(0,0,0,.6);
border-right:1px solid var(--line2)}
.side.open{transform:translateX(0)}
.sdim{display:none;position:fixed;inset:0;z-index:1150;
background:rgba(0,0,0,.6);backdrop-filter:blur(3px)}
.sdim.open{display:block}
.sdclose{display:flex;align-items:center;justify-content:space-between;
padding:10px 18px 14px;margin-bottom:6px;
border-bottom:1px solid var(--line);
padding-top:calc(10px + env(safe-area-inset-top))}
.sdclose b{font-size:14px;color:var(--txt)}
.sdclose button{background:var(--card2);border:1px solid var(--line);
color:var(--dim);width:34px;height:34px;border-radius:10px;
display:grid;place-items:center;cursor:pointer}

.main{padding:18px 14px 96px}
.fg{grid-template-columns:1fr 1fr}}

@media(max-width:900px){
.g4{grid-template-columns:1fr 1fr}}

@media(max-width:720px){
.g2,.g3,.g4{grid-template-columns:1fr}
.nlinks{display:none}.burger{display:block}
.nlinks.open{display:flex;position:absolute;top:68px;left:0;right:0;
flex-direction:column;background:var(--bg2);padding:14px;gap:5px;
border-bottom:1px solid var(--line);box-shadow:var(--sh2);align-items:stretch}
.nlinks.open>a{padding:12px 15px}
.fg,.split{grid-template-columns:1fr}
.split>div:first-child{border-right:0;border-bottom:1px solid var(--line)}
.box{padding:24px 18px}
.hero{padding:52px 0 44px}

/* ── PAGE HEADER — title aur button upar-neeche ── */
.ph{flex-direction:column;align-items:flex-start;gap:12px}
.ph h1{font-size:20px;line-height:1.25}
.ph .flex{width:100%;flex-wrap:wrap}
.ph .flex .btn{flex:1 1 auto;justify-content:center;min-height:44px}

/* ── TABLE → CARD ──
   Mobile pe table daayein-baayein khisakti thi aur aadhi
   kat jaati thi. Ab har row ek card ban jaati hai. */
.tbl{overflow:visible}
.tbl table,.tbl thead,.tbl tbody,.tbl th,.tbl td,.tbl tr{display:block}
.tbl thead{position:absolute;left:-9999px}
.tbl tr{background:var(--card2);border:1px solid var(--line);
border-radius:14px;margin:0 12px 10px;padding:6px 2px}
.tbl td{border:0;padding:9px 14px;display:flex;justify-content:space-between;
align-items:center;gap:14px;text-align:right;font-size:13.5px}
.tbl td:before{content:attr(data-l);color:var(--dim2);font-size:11.5px;
font-weight:650;text-transform:uppercase;letter-spacing:.4px;
text-align:left;flex:0 0 auto}
.tbl td:not(:last-child){border-bottom:1px solid rgba(255,255,255,.045)}

/* jo table card nahi ban sakti, kam se kam scroll ho */
.bboard,.scrollx{overflow-x:auto;-webkit-overflow-scrolling:touch}

/* ── Ungli se dabane layak ── */
.btn{min-height:44px}
.btn-sm{min-height:38px}
input,select,textarea{font-size:16px;min-height:46px}

.fbot{justify-content:center;text-align:center}}

/* ═══ 📱 BOTTOM BAR — sirf mobile, sirf logged-in ═══
   5 sabse zaroori kaam hamesha ungli ke paas.
   Ye asli app jaisa feel deta hai. */
.mnav{display:none}
@media(max-width:1080px){
.mnav{display:grid;grid-template-columns:repeat(5,1fr);
position:fixed;left:0;right:0;bottom:0;z-index:118;
background:rgba(11,16,32,.97);backdrop-filter:blur(16px);
border-top:1px solid var(--line);
padding:6px 2px calc(6px + env(safe-area-inset-bottom))}
.mnav a{display:flex;flex-direction:column;align-items:center;gap:3px;
padding:7px 2px;color:var(--dim2);font-size:10px;font-weight:600;
border-radius:12px;transition:.16s}
.mnav a.on{color:var(--acc3)}
.mnav a.on svg{color:var(--acc4)}
.mnav a:active{background:var(--card2)}
.mnav .bt{font-size:9.5px;letter-spacing:.2px}}

@media(max-width:560px){
.g4{grid-template-columns:1fr}
.hero h1{font-size:30px}
.wrap{padding-left:14px;padding-right:14px}}

/* ═══ 💬 BOSS AGENT CHAT ═══
   Malik ka hukum: "chat board jaisa rahega, usse hum baat
   kar sake". Mobile pe bhi poora fit. */
.agchat{background:var(--bg);border:1px solid var(--line);
border-radius:14px;padding:12px;margin-top:12px;
max-height:400px;overflow-y:auto;
display:flex;flex-direction:column;gap:9px}
.agchat::-webkit-scrollbar{width:5px}
.agchat::-webkit-scrollbar-thumb{background:var(--line2);
border-radius:9px}
.agcode{background:#05080f;border:1px solid var(--line2);
border-radius:9px;padding:11px 12px;margin:9px 0 3px;
font-family:ui-monospace,Menlo,monospace;font-size:11.5px;
line-height:1.6;color:#CBD5E1;overflow-x:auto;
white-space:pre;-webkit-overflow-scrolling:touch}
.agmeta{margin-top:8px;font-size:10.5px;color:var(--dim3);
border-top:1px solid var(--line);padding-top:6px}
.agfix{margin-top:10px;padding:11px;border-radius:11px;
background:linear-gradient(135deg,rgba(34,197,94,.12),
rgba(0,230,255,.05));border:1px solid rgba(34,197,94,.3);
display:flex;flex-wrap:wrap;align-items:center;gap:8px}
.agfix b{color:#22C55E;font-size:12.5px}
.agfix span{font-family:ui-monospace,monospace;font-size:11px;
color:var(--dim2);overflow:hidden;text-overflow:ellipsis;
max-width:100%}
.agfix .btn{margin-left:auto}
.agdots{display:inline-flex;gap:3px;vertical-align:middle}
.agdots i{width:5px;height:5px;border-radius:50%;
background:var(--acc4);animation:agp 1.1s infinite}
.agdots i:nth-child(2){animation-delay:.15s}
.agdots i:nth-child(3){animation-delay:.3s}
@keyframes agp{0%,60%,100%{opacity:.3}30%{opacity:1}}

/* 📱 Mobile — chat + agent row */
@media(max-width:720px){
/* ⚠️ Boss ka leaderboard table mobile pe kat rahi thi
   (screenshot me "#  MODEL  COMPANY  KAAM" ke neeche sab
   thusa hua tha). Ab har row ek card. */
.bboard table,.bboard thead,.bboard tbody,
.bboard th,.bboard td,.bboard tr{display:block}
.bboard thead{position:absolute;left:-9999px}
.bboard tr{background:var(--card2);border:1px solid var(--line);
border-radius:12px;margin-bottom:8px;padding:4px 2px}
.bboard td{border:0;padding:7px 12px;display:flex;
justify-content:space-between;gap:12px;text-align:right;
font-size:12.5px;align-items:center}
.bboard td:before{content:attr(data-l);color:var(--dim2);
font-size:10.5px;font-weight:700;text-transform:uppercase;
letter-spacing:.4px;text-align:left;flex:0 0 auto}
.bboard td:not(:last-child){border-bottom:1px solid
rgba(255,255,255,.045)}
.bboard .bm{word-break:break-all;text-align:right}
/* ⚠️ 330px bahut chhota tha — screenshot me code aadha
   dikh raha tha aur user ko scroll karna padta tha.
   Ab screen ki height ke hisaab se. */
.agchat{max-height:min(60vh,480px);padding:10px}
.agcode{font-size:10.5px;padding:9px 10px;max-height:300px;
overflow:auto}
.agrow{flex-direction:column;align-items:stretch;gap:8px}
.agrow .agsel,.agrow .aginp{width:100%}
.agrow .btn{width:100%;justify-content:center}
.agfix{flex-direction:column;align-items:flex-start}
.agfix .btn{margin-left:0;width:100%;justify-content:center}
.agsteps{flex-wrap:wrap}}


/* ═══ 🌐 DOMAIN CHIP — logo ke saath, sabse upar ═══
   Sirf admin ko dikhta hai. Ek tap = domain daalne ka box. */
.dchip{display:inline-flex;align-items:center;gap:6px;
margin-left:12px;padding:6px 11px;border-radius:99px;
background:var(--card2);border:1px dashed var(--line2);
color:var(--dim2);font-size:11.5px;font-weight:650;
cursor:pointer;transition:.18s var(--ease);flex-shrink:0}
.dchip:hover{border-color:var(--acc);color:var(--txt);
background:rgba(124,58,237,.12)}
.dchip svg{color:var(--acc4);flex-shrink:0}
.dchip span{white-space:nowrap;overflow:hidden;
text-overflow:ellipsis;max-width:150px}
.dchip.live{border-style:solid;
border-color:rgba(34,197,94,.4);color:#22C55E;
background:rgba(34,197,94,.08)}
.dchip.live svg{color:#22C55E}

.dombg{position:fixed;inset:0;z-index:1400;
background:rgba(7,11,20,.75);backdrop-filter:blur(4px);
opacity:0;pointer-events:none;transition:.24s}
.dombg.on{opacity:1;pointer-events:auto}
.dombox{position:fixed;top:50%;left:50%;z-index:1401;
transform:translate(-50%,-50%) scale(.95);
width:min(420px,calc(100vw - 28px));border-radius:16px;
background:linear-gradient(165deg,var(--card),var(--bg2));
border:1px solid var(--line2);box-shadow:var(--sh2),0 0 60px var(--glow);
opacity:0;pointer-events:none;transition:.24s var(--ease);
overflow:hidden}
.dombox.on{opacity:1;pointer-events:auto;
transform:translate(-50%,-50%) scale(1)}
.domh{display:flex;align-items:center;gap:9px;padding:15px 17px;
border-bottom:1px solid var(--line);background:var(--bg2);
font-size:14.5px}
.domh svg{color:var(--acc4)}
.domh button{margin-left:auto;background:none;border:0;
color:var(--dim2);cursor:pointer;padding:4px;display:flex;
border-radius:7px}
.domh button:hover{color:var(--txt);background:var(--card2)}
.domb{padding:17px}
.dominp{width:100%;margin-top:11px;padding:13px 14px;
border-radius:11px;background:var(--bg);border:1px solid var(--line2);
color:var(--txt);font-size:15px;font-family:ui-monospace,monospace}
.dominp:focus{outline:0;border-color:var(--acc);
box-shadow:0 0 0 3px rgba(124,58,237,.15)}
.domb .btn{width:100%;justify-content:center}

/* 📱 Mobile — chip chhota, box neeche se */
@media(max-width:720px){
.dchip{margin-left:8px;padding:5px 9px;font-size:10.5px}
.dchip span{max-width:74px}
/* ⚠️ desktop wala rule `top:50%; transform:translate(-50%,-50%)`
   hai. Mobile pe sirf top/bottom badalne se `left:50%` reh
   jata tha aur box upar khisak kar aadha kat jata tha
   (screenshot me "Save karo" upar kat gaya tha).
   Ab left/transform dono saaf reset kar rahe hain. */
/* ⚠️ Desktop rule me `top:50%` hai. `top:auto` dene par
   browser ne use theek se reset nahi kiya aur box upar
   chala gaya (top=-247, save button screen se bahar).
   Ab `inset` se poora position ek saath likh rahe hain —
   koi purani value bachti hi nahi. */
.dombox{inset:auto 0 0 0;
width:100%;max-height:88vh;overflow-y:auto;
transform:translateY(100%);border-radius:18px 18px 0 0}
.dombox.on{transform:translateY(0)}}

@media(max-width:400px){.dchip span{display:none}
.dchip{padding:7px 9px;margin-left:6px}}


/* 🔒 Domain lock ho chuka */
.domlock{text-align:center;padding:8px 0}
.domlock>svg{color:#22C55E;margin-bottom:10px}
.domlock b{display:block;font-size:15px;margin-bottom:10px}
.domval{font-family:ui-monospace,monospace;font-size:14px;
color:var(--acc4);background:var(--bg);padding:11px 14px;
border-radius:10px;border:1px solid rgba(34,197,94,.3);
margin-bottom:12px;word-break:break-all}
.domlock p{margin-bottom:8px}
.domlock code{background:var(--bg);padding:2px 6px;border-radius:5px;
font-size:11px;color:var(--dim)}


.agfix.agwarn{background:linear-gradient(135deg,rgba(245,158,11,.12),
rgba(245,158,11,.04));border-color:rgba(245,158,11,.35);
flex-direction:column;align-items:flex-start}
.agfix.agwarn b{color:#F59E0B}

"""