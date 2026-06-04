"""Add Sad Wrap mode to index.html. Idempotent — skip if already present."""
import re

with open('/home/rishua/vrc-wrap/index.html','r',encoding='utf-8') as f:
    html = f.read()

if 'analyzeSad' in html:
    print("ALREADY EXISTS — skip")
    exit(0)

# 1. CSS: sad accent vars + mode toggle
sad_css = '''
  .wrap-mode{display:flex;gap:8px;justify-content:center;margin:16px auto;max-width:480px}
  .wrap-mode .wm{flex:1;border:1px solid var(--line);border-radius:13px;padding:12px 8px;background:rgba(255,255,255,.025);cursor:pointer;transition:.25s;text-align:center;font-family:'Anton';font-size:clamp(16px,4vw,22px);line-height:1;text-transform:uppercase;letter-spacing:.06em}
  .wrap-mode .wm:hover{border-color:color-mix(in srgb,var(--accent) 50%,transparent)}
  .wrap-mode .wm.sel{border-color:var(--accent);background:color-mix(in srgb,var(--accent) 12%,transparent);box-shadow:0 0 26px -10px var(--accent)}
  .wrap-mode .wm .wml{font-family:'Space Mono',monospace;font-size:10px;letter-spacing:.08em;color:var(--muted);margin-top:4px;text-transform:none}
  .wrap-mode .wm.sel .wml{color:var(--ink)}
'''

html = html.replace('  #intake{text-align:center}', sad_css + '\n  #intake{text-align:center}')

# 2. Mode toggle HTML after eyebrow
toggle_html = '''    <div class="wrap-mode rv" id="wrapMode">
      <div class="wm sel" data-mode="happy"><div>Happy</div><div class="wml">your best moments</div></div>
      <div class="wm" data-mode="sad"><div>Sad</div><div class="wml">the other side</div></div>
    </div>
'''
html = html.replace('    <div class="eyebrow rv">Checkpoint · <span class="curYear"></span></div>\n', '    <div class="eyebrow rv">Checkpoint · <span class="curYear"></span></div>\n' + toggle_html)

# 3. ACCENTS_SAD
html = html.replace("const ACCENTS=['--green',", "const ACCENTS=['--green',")

# 4. analyzeSad function — insert right before "function build(st)"
analyze_sad_fn = '''function analyzeSad(db, range){
  const out=m=>{$('#loadmsg').textContent=m;};
  let tables=[];try{const r=db.exec("SELECT name FROM sqlite_master WHERE type='table'");if(r[0])tables=r[0].values.map(v=>v[0]);}catch(e){}
  const has=n=>tables.includes(n);
  const findSuffix=suf=>tables.filter(t=>t.toLowerCase().endsWith(suf));
  const rowsOf=sql=>{try{const r=db.exec(sql);if(!r[0])return[];const cols=r[0].columns;return r[0].values.map(v=>{const o={};cols.forEach((c,i)=>o[c]=v[i]);return o;});}catch(e){return[];}};
  const fmtDate=d=>d?d.toISOString().slice(0,10):'—';
  let loc=has('gamelog_location')?rowsOf("SELECT created_at,world_name,world_id,time FROM gamelog_location"):[];
  loc=loc.map(r=>({d:parseTime(r.created_at),name:r.world_name||'Unknown World',id:r.world_id,time:+r.time||0})).filter(r=>r.d);
  const allDates=loc.map(r=>r.d);
  const end=allDates.length?new Date(Math.max(...allDates.map(d=>d.getTime()))):new Date();
  let start;
  if(range==='month')start=new Date(end.getTime()-30*864e5);else if(range==='year')start=new Date(end.getTime()-365*864e5);else start=new Date(0);
  const inR=d=>d&&d>=start&&d<=end;
  loc=loc.filter(r=>inR(r.d));
  const stats={year:end.getFullYear(),range,startDate:start,endDate:end,hasReal:false};
  if(!loc.length)return stats;

  // 1 unfriended
  const flt=findSuffix('friend_log_history')[0];let unfriended=0;
  if(flt)unfriended=rowsOf(`SELECT type FROM "${flt}"`).filter(r=>inR(parseTime(r.created_at))&&r.type==='Unfriend').length;
  stats.unfriended=unfriended;
  // 2 abandoned worlds
  const wc={};loc.forEach(r=>{wc[r.name]=(wc[r.name]||0)+1;});
  stats.abandonedWorlds=Object.values(wc).filter(v=>v===1).length;
  // 3 one-time people
  let jl=has('gamelog_join_leave')?rowsOf("SELECT created_at,type,display_name FROM gamelog_join_leave"):[];
  jl=jl.map(r=>({d:parseTime(r.created_at),type:r.type,nm:r.display_name})).filter(r=>inR(r.d)&&/join/i.test(r.type||''));
  const pc={};jl.forEach(r=>{if(r.nm)pc[r.nm]=(pc[r.nm]||0)+1;});
  stats.oneTimePeople=Object.values(pc).filter(v=>v===1).length;
  // 4 4-am sessions
  stats.amSessions=loc.filter(r=>{const h=r.d.getHours();return h>=4&&h<=7;}).length;
  // 5 avatar changes
  const aht=findSuffix('avatar_history')[0];let avatarChanges=0;
  if(aht)avatarChanges=rowsOf(`SELECT created_at FROM "${aht}"`).filter(r=>inR(parseTime(r.created_at))).length;
  stats.avatarChanges=avatarChanges;
  // 6 transit worlds
  const wcd={};loc.forEach(r=>{if(!wcd[r.name])wcd[r.name]={c:0,t:0};wcd[r.name].c++;wcd[r.name].t+=r.time;});
  const transit=Object.entries(wcd).filter(([_,d])=>d.c>=5&&d.t/d.c<300000).length; // avg<5min
  stats.transitWorlds=transit;
  // 7 shortest sessions (<1min)
  stats.shortSessions=loc.filter(r=>r.time>0&&r.time<60000).length;
  // 8 solo ratio
  const dayJoin={};jl.forEach(r=>{if(r.d){const k=r.d.toISOString().slice(0,10);dayJoin[k]=true;}});
  const dayLoc={};loc.forEach(r=>{if(r.d)dayLoc[r.d.toISOString().slice(0,10)]=true;});
  const allDays=Object.keys(dayLoc);const soloDays=allDays.filter(d=>!dayJoin[d]).length;
  stats.soloPct=allDays.length?Math.round(soloDays/allDays.length*100):0;
  // 9 first vs last
  stats.firstDate=fmtDate(loc[0].d);stats.lastDate=fmtDate(loc[loc.length-1].d);
  stats.activitySpan=Math.round((loc[loc.length-1].d-loc[0].d)/86400000);
  // 10 friend net
  let flRows=[];if(flt)flRows=rowsOf(`SELECT type FROM "${flt}"`);
  const added=flRows.filter(r=>inR(parseTime(r.created_at))&&r.type==='Friend').length;
  stats.friendNet=added-unfriended;
  stats.hasReal=true;
  return stats;
}
'''
html = html.replace('function build(st){', analyze_sad_fn + '\nfunction build(st){')

# 5. buildSad + demoSadStats — insert right before "const ACCENTS"
sad_build_fn = '''function buildSad(st){
  const SLIDES=[
    ()=>card('UNFRIENDED',1,`
      <div class="kicker rv">${t('s_unfriended')}</div>
      <div class="bignum rv">${fmt(st.unfriended)}</div>
      <div class="unit rv">${t('s_unit_unf')}</div>
      <p class="lede rv">${t('s_lede_unf')}</p>`),
    ()=>card('ALONE',2,`
      <div class="kicker rv">${t('s_abandoned')}</div>
      <div class="bignum rv">${fmt(st.abandonedWorlds)}</div>
      <div class="unit rv">${t('s_unit_abn')}</div>
      <p class="lede rv">${t('s_lede_abn')}</p>`),
    ()=>card('STRANGERS',3,`
      <div class="kicker rv">${t('s_onetime')}</div>
      <div class="bignum rv">${fmt(st.oneTimePeople)}</div>
      <div class="unit rv">${t('s_unit_otp')}</div>
      <p class="lede rv">${t('s_lede_otp')}</p>`),
    ()=>card('DAWN PATROL',4,`
      <div class="kicker rv">${t('s_am')}</div>
      <div class="bignum rv">${fmt(st.amSessions)}</div>
      <div class="unit rv">${t('s_unit_am')}</div>
      <p class="lede rv">${t('s_lede_am')}</p>`),
    ()=>card('WHO ARE YOU',5,`
      <div class="kicker rv">${t('s_avatar')}</div>
      <div class="bignum rv">${fmt(st.avatarChanges)}</div>
      <div class="unit rv">${t('s_unit_av')}</div>
      <p class="lede rv">${t('s_lede_av')}</p>`),
    ()=>card('PASSING THROUGH',6,`
      <div class="kicker rv">${t('s_transit')}</div>
      <div class="bignum rv">${fmt(st.transitWorlds)}</div>
      <div class="unit rv">${t('s_unit_tr')}</div>
      <p class="lede rv">${t('s_lede_tr')}</p>`),
    ()=>card('BLINK',7,`
      <div class="kicker rv">${t('s_short')}</div>
      <div class="bignum rv">${fmt(st.shortSessions)}</div>
      <div class="unit rv">${t('s_unit_sh')}</div>
      <p class="lede rv">${t('s_lede_sh')}</p>`),
    ()=>card('SOLO',8,`
      <div class="kicker rv">${t('s_solo')}</div>
      <div class="bignum rv">${st.soloPct}<span style="font-size:.35em;font-family:'Space Mono',monospace;color:var(--muted);margin-left:4px">%</span></div>
      <div class="unit rv">${t('s_unit_so')}</div>
      <p class="lede rv">${t('s_lede_so')}</p>`),
    ()=>card('ARC',9,`
      <div class="kicker rv">${t('s_span')}</div>
      <div class="bignum rv">${fmt(st.activitySpan)}</div>
      <div class="unit rv">${t('s_unit_sp')}</div>
      <p class="lede rv">${t('s_lede_sp',{first:st.firstDate,last:st.lastDate})}</p>`),
    ()=>card('NET',10,`
      <div class="kicker rv">${t('s_net')}</div>
      <div class="bignum rv" style="color:${st.friendNet<0?'var(--magenta)':'var(--accent)'}">${st.friendNet>=0?'+':''}${fmt(st.friendNet)}</div>
      <div class="unit rv">${t('s_unit_net')}</div>
      <p class="lede rv">${st.friendNet<0?t('s_lede_net_neg'):t('s_lede_net_pos')}</p>`),
  ];
  S=st;const YR=st.year;
  const pg=$('#progress');pg.innerHTML='';
  for(let i=0;i<10;i++){const s=document.createElement('div');s.className='seg';s.innerHTML='<i></i>';pg.appendChild(s);}
  const sadAccents=['--magenta','--pink','--cyan','--magenta','--pink','--cyan','--magenta','--pink','--cyan','--magenta'];
  // override global idx handler for sad palette
  window._sadAccents=sadAccents;
  showSlide(0);
}
function demoSadStats(range){
  const y=new Date().getFullYear();const now=new Date();
  const dstart=range==='month'?new Date(now-30*864e5):range==='year'?new Date(now-365*864e5):new Date(0);
  return {year:y,range,startDate:dstart,endDate:now,hasReal:true,demo:true,
    unfriended:22,abandonedWorlds:393,oneTimePeople:824,amSessions:120,avatarChanges:136,
    transitWorlds:27,shortSessions:48,soloPct:34,activitySpan:186,firstDate:fmtDate(dstart),lastDate:fmtDate(now),
    friendNet:-5};
}
'''
html = html.replace('function demoStats(range){', sad_build_fn + '\nfunction demoStats(range){')

# 6. Sad i18n keys — inject into each language block
# Match each i18n block and add sad keys after the last entry before closing }
import json

sad_i18n = {
  'en': {'s_unfriended':'Friends lost','s_unit_unf':'people unfriended','s_lede_unf':'For every person who joined your life, someone walked away.',
    's_abandoned':'Abandoned worlds','s_unit_abn':'places visited once','s_lede_abn':'You stepped in. Looked around. Never came back.',
    's_onetime':'Ghosts','s_unit_otp':'people met once','s_lede_otp':'One conversation. One wave. Never again.',
    's_am':'Dawn patrol','s_unit_am':'sessions at 4-7 AM','s_lede_am':'When the world was asleep, you were somewhere else.',
    's_avatar':'Who are you','s_unit_av':'avatar changes','s_lede_av':'136 versions of yourself. Which one was real?',
    's_transit':'Passing through','s_unit_tr':'transit worlds','s_lede_tr':'You visited often but never stayed. Just passing through.',
    's_short':'Blink','s_unit_sh':'sessions under 1 minute','s_lede_sh':'In and out. Changed your mind before you arrived.',
    's_solo':'Solo','s_unit_so':'of your days were completely alone','s_lede_so':'No friends. No strangers. Just you and the empty world.',
    's_span':'Your arc','s_unit_sp':'day journey','s_lede_sp':'From {first} to {last}. What changed?',
    's_net':'Balance','s_unit_net':'net friendships','s_lede_net_neg':'You ended the year with fewer friends than you started.','s_lede_net_pos':'You ended the year with more friends. The lonely nights paid off.'},
  'id': {'s_unfriended':'Teman hilang','s_unit_unf':'orang di-unfriend','s_lede_unf':'Untuk setiap orang yang datang, ada yang pergi.',
    's_abandoned':'World terlantar','s_unit_abn':'world dikunjungi sekali','s_lede_abn':'Kamu masuk. Lihat-lihat. Tak pernah kembali.',
    's_onetime':'Hantu','s_unit_otp':'orang ketemu sekali','s_lede_otp':'Satu percakapan. Satu lambaian. Tak pernah lagi.',
    's_am':' Patroli subuh','s_unit_am':'sesi jam 4-7 pagi','s_lede_am':'Saat dunia tidur, kamu ada di tempat lain.',
    's_avatar':'Siapa kamu','s_unit_av':'kali ganti avatar','s_lede_av':'136 versi dirimu. Mana yang asli?',
    's_transit':'Mampir','s_unit_tr':'world transit','s_lede_tr':'Sering mampir tapi tak pernah singgah.',
    's_short':'Sekejap','s_unit_sh':'sesi di bawah 1 menit','s_lede_sh':'Masuk. Langsung keluar. Berubah pikiran.',
    's_solo':'Sendiri','s_unit_so':'harimu benar-benar sendiri','s_lede_so':'Tanpa teman. Tanpa orang asing. Hanya kamu dan world kosong.',
    's_span':'Perjalananmu','s_unit_sp':'hari perjalanan','s_lede_sp':'Dari {first} hingga {last}. Apa yang berubah?',
    's_net':'Neraca','s_unit_net':'net pertemanan','s_lede_net_neg':'Kamu mengakhiri tahun dengan lebih sedikit teman.','s_lede_net_pos':'Kamu mengakhiri tahun dengan lebih banyak teman.'},
  'ja': {'s_unfriended':'失った友達','s_unit_unf':'人のフレンド解除','s_lede_unf':'誰かがあなたの人生に入るたびに、誰かが去っていった。',
    's_abandoned':' abandoned', 's_unit_abn':'回だけ訪れたワールド','s_lede_abn':'足を踏み入れて、眺めて、二度と戻らなかった。',
    's_onetime':'幽霊','s_unit_otp':'一度だけ会った人','s_lede_otp':'一度会って、手を振って、二度と。',
    's_am':'夜明けの patrol','s_unit_am':'朝4-7時の記録','s_lede_am':'世界が眠っている間、あなたはどこか別の場所にいた。',
    's_avatar':'自分探し','s_unit_av':'回アバター変更','s_lede_av':'136通りの自分。どれが本当？',
    's_transit':'通過点','s_unit_tr':'通過したワールド','s_lede_tr':'何度も立ち寄ったが、留まることはなかった。',
    's_short':'瞬間','s_unit_sh':'1分未満のセッション','s_lede_sh':'入ってすぐ出た。心変わり。',
    's_solo':'孤独','s_unit_so':'完全に一人だった日','s_lede_so':'友達もいない。他人もいない。あなたと空っぽのワールドだけ。',
    's_span':'軌跡','s_unit_sp':'日間の旅','s_lede_sp':' {first} から {last} まで。何が変わった？',
    's_net':'収支','s_unit_net':'純フレンド数','s_lede_net_neg':'今年は失った友達の方が多かった。','s_lede_net_pos':'今年は増えた。孤独な夜は報われた。'},
}

def inject_sad_i18n(t, lang_code, sad_dict):
    """Find the i18n block for a language and inject sad keys before the closing }"""
    # Each lang block ends with "},/" before next lang
    # We inject after the last key-value pair before the closing }
    # Pattern: lang:{...key:'val',\n nextlang} → lang:{...key:'val',\n  sadkey:'val',\n nextlang}
    import re
    # Find the block: lang:{ until the next lang or end
    # Replace: just before the closing } of that lang block
    pattern = r'('+lang_code+':\{)(.*?)(\s*\})'
    def repl(m):
        prefix = m.group(1)
        body = m.group(2)
        # add sad keys
        additions = ''.join(f"  {k}:'{v}',\n" for k,v in sad_dict.items() if v)
        # if body doesn't end with comma, no need; we're adding before }
        return prefix + body.rstrip() + '\n' + additions + '}'
    t = re.sub(pattern, repl, t, count=1, flags=re.DOTALL)
    return t

for lang, d in sad_i18n.items():
    html = inject_sad_i18n(html, lang, d)

# 7. WRAP_MODE global + toggle wiring
wrap_js = '''
let WRAP_MODE='happy';
function setWrapMode(m){
  WRAP_MODE=m;
  localStorage.setItem('vrcwrap_mode',m);
  document.querySelectorAll('#wrapMode .wm').forEach(b=>b.classList.toggle('sel',b.dataset.mode===m));
  // accent shift
  if(m==='sad'){document.documentElement.style.setProperty('--accent','var(--magenta)');document.documentElement.style.setProperty('--accent2','var(--pink)');}else{ document.documentElement.style.removeProperty('--accent');document.documentElement.style.removeProperty('--accent2');}
}
$('#wrapMode').addEventListener('click',e=>{const b=e.target.closest('.wm');if(!b)return;setWrapMode(b.dataset.mode);});
// restore saved mode
try{const sm=localStorage.getItem('vrcwrap_mode');if(sm==='sad'||sm==='happy')setWrapMode(sm);}catch(e){}
'''
html = html.replace('let WRAP_MODE', wrap_js)

# existing line adjust — ensure we have the variable at top level
html = html.replace('let CARD_NAME=\'\';', 'let WRAP_MODE=\'happy\',CARD_NAME=\'\';')

# 8. Demo + upload path branching — after handleFile success
html = html.replace('''    if(!st.hasReal){$('#loading').classList.remove('on');$('#intake').classList.add('on');showErr(t('err_empty'));return;}
    await loadThumbs(st);
    await new Promise(r=>setTimeout(r,400));
    build(st);enterDeck();''',
'''    if(!st.hasReal){$('#loading').classList.remove('on');$('#intake').classList.add('on');showErr(t('err_empty'));return;}
    await loadThumbs(st);
    await new Promise(r=>setTimeout(r,400));
    if(WRAP_MODE==='sad'){buildSad(st);enterDeck();}else{build(st);enterDeck();}''')

# 9. Demo handler branching
html = html.replace("$('#demo').onclick=()=>{startLoad();(async()=>{const st=demoStats(TF);await loadThumbs(st);await new Promise(r=>setTimeout(r,500));build(st);enterDeck();})();};",
"$('#demo').onclick=()=>{startLoad();(async()=>{const st=WRAP_MODE==='sad'?demoSadStats(TF):demoStats(TF);await loadThumbs(st);await new Promise(r=>setTimeout(r,500));if(WRAP_MODE==='sad'){buildSad(st);enterDeck();}else{build(st);enterDeck();}})();};")

with open('/home/rishua/vrc-wrap/index.html','w',encoding='utf-8') as f:
    f.write(html)
print("DONE — sad mode added")
