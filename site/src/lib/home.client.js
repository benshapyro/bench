const PAGE = 650;

const JOB = Object.fromEntries(JOBS.map(j=>[j.id,j]));
const MODEL = Object.fromEntries(DATA.models.map(m=>[m.id,m]));
const LEFT_REASON = {
  business:{'claude-fable-5-1':'only scored on an older version of the test'},
  software:{'claude-opus-5-5':'its score is still being checked'},
};
const state = {job:'business', volume:DEFAULTS.volume, offered:'claude-sonnet-5-5', bar:DEFAULTS.bar, caching:DEFAULTS.caching, task:{}, showAll:false};
JOBS.forEach(j=>state.task[j.id]={pin:j.pin,pout:j.pout});

/* ---------- engine (spec §5) ---------- */
function levelMult(lv){
  const s=(lv||'').toLowerCase();
  if(s.includes('none'))return 0; if(s.includes('minimal'))return .25;
  if(s.includes('xhigh'))return 3; if(s.includes('max'))return 4;
  if(s.includes('high'))return 2; if(s.includes('medium'))return 1; if(s.includes('low'))return .5;
  return 2;
}
function levelText(lv){
  const s=(lv||'').toLowerCase();
  if(!lv||s==='not stated')return '';
  if(s.includes('highest'))return 'at its highest thinking setting';
  if(s.includes('max at any'))return 'at max thinking';
  return 'at '+lv.replace(/ reasoning/i,'').replace('Adaptive/','').toLowerCase()+' thinking';
}
function cachingCounts(job){ return job.within || (22*8*60)/state.volume<=5; }
function costOf(mid, lv, jobId){
  const m=MODEL[mid], job=JOB[jobId], t=state.task[jobId];
  const inT=t.pin*PAGE, outT=t.pout*PAGE, thT=outT*levelMult(lv);
  const useCache=state.caching&&cachingCounts(job), rep=useCache?job.rep:0;
  const read=inT*m.in/1e6, save=inT*rep*(m.in-m.cr)/1e6, write=outT*m.out/1e6, think=thT*m.out/1e6;
  const task=read-save+write+think;
  return {inT,outT,thT,read,save,write,think,task,month:task*state.volume,useCache};
}
const same=(a,b)=>a&&b&&a.m===b.m&&a.lv===b.lv;
function compute(){
  const job=JOB[state.job];
  const rows=DATA.results.filter(r=>r.j===state.job&&!r.fp).map(r=>{const c=costOf(r.m,r.lv,state.job);return {...r,model:MODEL[r.m],mult:levelMult(r.lv),cost:c,month:c.month};});
  let leader=null; rows.forEach(r=>{ if(!leader||r.s>leader.s||(r.s===leader.s&&r.month<leader.month))leader=r; });
  rows.forEach(r=>{ r.pct=r.s/leader.s*100; r.clears=r.pct>=state.bar-1e-9; });
  let bv=null; rows.filter(r=>r.clears).forEach(r=>{ if(!bv||r.month<bv.month-1e-12||(Math.abs(r.month-bv.month)<1e-12&&r.s>bv.s))bv=r; });
  const offRows=rows.filter(r=>r.m===state.offered).sort((a,b)=>a.mult-b.mult);
  const off=state.offered?(offRows[offRows.length-1]||null):null;
  const ids=new Set(rows.map(r=>r.m));
  const left=DATA.models.filter(m=>!ids.has(m.id)).map(m=>({m,reason:(LEFT_REASON[state.job]||{})[m.id]||'no score on this test'}));
  const byModel={}; rows.forEach(r=>(byModel[r.m]=byModel[r.m]||[]).push(r));
  const picks=Object.values(byModel).map(list=>{const ok=list.filter(r=>r.clears).sort((a,b)=>a.month-b.month);return ok[0]||list.slice().sort((a,b)=>b.s-a.s)[0];})
    .sort((a,b)=>b.pct-a.pct||a.month-b.month);
  const fullPass={}; DATA.results.filter(r=>r.j===state.job&&r.fp).forEach(r=>fullPass[r.m+'|'+r.lv]=r.s);
  return {job,rows,leader,bv,off,left,picks,n:ids.size,fullPass,offeredGiven:!!state.offered};
}

/* ---------- formatting ---------- */
function sig2(v){ if(!isFinite(v)||v<=0)return '0'; const d=Math.floor(Math.log10(v)),p=Math.pow(10,d-1),r=Math.round(v/p)*p;
  if(r>=100)return Math.round(r).toLocaleString('en-US'); return r.toFixed(Math.max(0,1-d)); }
const usd=v=>{ const s=sig2(v); return '$'+(/\.\d$/.test(s)?s+'0':s); };
const usdTask=v=>'$'+(v<0.01?v.toFixed(4):v<1?v.toFixed(3):v.toFixed(2));
const pct=v=>Math.round(v)+'%';
const nf=v=>Math.round(v).toLocaleString('en-US');
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const pages=v=>{const n=Math.round(v*100)/100; return n+(n===1?' page':' pages');};

/* ---------- controls ---------- */
function fillControls(){
  const fj=document.getElementById('f-job'); fj.innerHTML=JOBS.map(j=>`<option value="${j.id}">${esc(j.long)}</option>`).join('');
  const fb=document.getElementById('f-bar'); fb.innerHTML=[50,55,60,65,70,75,80,85,90,95,100].map(v=>`<option value="${v}">${v}%</option>`).join('');
  const fo=document.getElementById('f-off');
  const labs=[...new Set(DATA.models.map(m=>m.open?'Open-weight':m.lab))];
  fo.innerHTML=`<option value="">nothing yet</option>`+labs.map(l=>`<optgroup label="${esc(l)}">`+DATA.models.filter(m=>(m.open?'Open-weight':m.lab)===l).map(m=>`<option value="${m.id}">${esc(m.name)}</option>`).join('')+`</optgroup>`).join('');
  fj.addEventListener('change',()=>{state.job=fj.value; state.showAll=false; render();});
  fb.addEventListener('change',()=>{state.bar=+fb.value; render();});
  fo.addEventListener('change',()=>{state.offered=fo.value; render();});
  const fv=document.getElementById('f-vol');
  fv.addEventListener('input',()=>{const v=parseFloat(fv.value); if(v>0){state.volume=v; render(fv);} sizeFields();});
}
let _cv;
function measure(text,el){ _cv=_cv||document.createElement('canvas'); const ctx=_cv.getContext('2d'); const cs=getComputedStyle(el); ctx.font=`${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`; return Math.ceil(ctx.measureText(text).width); }
function sizeFields(){
  ['f-job','f-off','f-bar'].forEach(id=>{const s=document.getElementById(id); const t=s.options[s.selectedIndex]?.text||''; s.style.width=(measure(t,s)+4)+'px';});
  const fv=document.getElementById('f-vol'); fv.style.width=(measure(fv.value||'0',fv)+18)+'px';
}
function syncControls(except){
  const set=(id,v)=>{const el=document.getElementById(id); if(el!==except)el.value=v;};
  set('f-job',state.job); set('f-off',state.offered); set('f-bar',state.bar); set('f-vol',state.volume);
  document.getElementById('f-unit').textContent=JOB[state.job].units;
  sizeFields();
}

/* ---------- verdict ---------- */
function renderVerdict(C){
  const {bv,leader,off,job}=C;
  const mo=v=>`<span class="num">${usd(v)}</span>`;
  let head, sub;
  if(off && same(off,bv)){
    head=`Stick with <em>${esc(off.model.name)}</em>.`;
    sub=`It's the cheapest model that is at least ${state.bar}% as good as the best at ${esc(job.ex)}. Expect about <b>${mo(off.month)} a month</b> for ${nf(state.volume)} ${esc(job.units)}.`;
  } else if(off){
    head=`Use <em>${esc(bv.model.name)}</em>.`;
    const cheaper=bv.month<off.month;
    sub=`It would cost about <b>${mo(bv.month)} a month</b> instead of ${mo(off.month)} for ${esc(off.model.name)}, and it's ${pct(bv.pct)} as good as the best model on this job${off.pct>bv.pct?` (${esc(off.model.name)} is ${pct(off.pct)})`:''}.`;
    if(!cheaper) sub=`It costs more than ${esc(off.model.name)}, about <b>${mo(bv.month)} a month</b> instead of ${mo(off.month)}, but ${esc(off.model.name)} doesn't reach your bar (${pct(off.pct)} of the best).`;
  } else {
    head=`Use <em>${esc(bv.model.name)}</em>.`;
    sub = same(bv,leader)
      ? `It's the best model at ${esc(job.ex)}, and nothing cheaper reaches ${state.bar}% of it. Expect about <b>${mo(bv.month)} a month</b> for ${nf(state.volume)} ${esc(job.units)}.`
      : `It's the cheapest model that is at least ${state.bar}% as good as the best. Expect about <b>${mo(bv.month)} a month</b> for ${nf(state.volume)} ${esc(job.units)}.`;
  }
  if(C.offeredGiven && !off){
    sub += ` Bench has no like-for-like score for ${esc(MODEL[state.offered].name)} on this job, so it can't compare it.`;
  }
  // the pair of figures: recommendation vs the comparison that matters
  const other = (off && !same(off,bv)) ? {r:off, role:'what you were offered'} : (!same(leader,bv) ? {r:leader, role:'the best overall'} : null);
  const maxM = Math.max(bv.month, other?other.r.month:0);
  const fig=(r,role,hot)=>`<div class="fig ${hot?'hot':''}"><span class="n num">${usd(r.month)}<small>a month</small></span>
      <div class="costbar" aria-hidden="true"><i style="width:${Math.max(2,r.month/maxM*100)}%"></i></div>
      <span class="l"><b>${esc(r.model.name)}</b>, ${role}. ${pct(r.pct)} as good as the best.</span></div>`;
  const extra = (other && other.role!=='the best overall' && !same(leader,bv) && !same(leader,off))
    ? `<span>The best overall is ${esc(leader.model.name)}, at about ${usd(leader.month)} a month.</span>` : '';
  const el=document.getElementById('verdict');
  el.innerHTML=`<h1 class="v-head">${head}</h1><p class="v-sub">${sub}</p>
    <div class="pair">${fig(bv,'our pick',true)}${other?fig(other.r,other.role,false):''}</div>
    <p class="next"><b>Before you decide,</b> test both on 20 of your own real tasks. A test score isn't a direct measure of quality on your work.</p>
    <p class="fine"><span>Compared ${C.n} of 15 models</span><span>Costs are estimates</span>${extra}</p>`;
  el.classList.remove('fade'); void el.offsetWidth; el.classList.add('fade');
}

/* ---------- drawers ---------- */
function renderField(C){
  const list = state.showAll ? C.picks : C.picks.slice(0,6);
  document.getElementById('h-field').textContent=`${C.n} models`;
  document.getElementById('b-field').innerHTML=`
    <p>Each model at its cheapest thinking setting that clears your bar. Bars show how good it is compared with the best; the dashed line is your bar.</p>
    <div>${list.map(r=>{
      const t=[same(r,C.bv)&&'<span class="tg">Our pick</span>',same(r,C.leader)&&!same(r,C.bv)&&'<span class="tg">Best</span>',same(r,C.off)&&'<span class="tg o">Offered</span>'].filter(Boolean).join('');
      return `<div class="row ${r.clears?'':'below'} ${same(r,C.bv)?'hot':''}"><span class="nm">${esc(r.model.name)}${t}</span>
        <span class="tr" role="img" aria-label="${pct(r.pct)} of the best${r.clears?'':', below your bar'}"><i style="width:${r.pct}%"></i><s style="left:${state.bar}%"></s></span>
        <span class="c num">${usd(r.month)}</span></div>`; }).join('')}</div>
    ${C.picks.length>6?`<button class="more" type="button" id="more">${state.showAll?'Show fewer':`Show all ${C.picks.length}`}</button>`:''}
    ${C.left.length?`<p class="left">Not compared: ${C.left.map(l=>esc(l.m.name)+' ('+l.reason+')').join(', ')}.</p>`:''}`;
  const mb=document.getElementById('more'); if(mb) mb.addEventListener('click',()=>{state.showAll=!state.showAll; renderField(compute());});
}
function renderBill(C){
  const r=C.bv, c=r.cost, job=C.job, t=state.task[state.job], v=state.volume;
  document.getElementById('h-bill').textContent=`${usd(c.month)} for ${r.model.name}`;
  const cacheNote = !state.caching ? 'Turned off.' :
    c.useCache ? (job.within?`Most of what it reads repeats within one ${job.unit}, and labs charge less for repeated text.`:`Tasks arrive often enough to reuse repeated text.`) :
    `At this volume a ${job.unit} arrives about every ${Math.round(22*8*60/v)} minutes, and the lab only keeps repeated text for 5, so this wouldn't save much.`;
  const el=document.getElementById('b-bill');
  const focused=document.activeElement&&el.contains(document.activeElement)?document.activeElement.id:null;
  el.innerHTML=`
    <p>A typical ${esc(job.unit)}, priced at ${esc(r.model.name)}'s list prices. Change the size to match your work; the answer above updates.</p>
    <div class="edit">
      <label>Reads <input type="number" id="e-pin" min="0.25" step="0.5" value="${t.pin}"> pages</label>
      <label>Writes <input type="number" id="e-pout" min="0.25" step="0.25" value="${t.pout}"> pages</label>
      <label><input type="checkbox" id="e-cache" ${state.caching?'checked':''}> Count savings from repeated text</label>
    </div>
    <div class="bill">
      <div class="li"><span class="k">Text it reads</span><span class="v num">${usd(c.read*v)}</span><span class="d">${pages(t.pin)} per ${esc(job.unit)}, about ${nf(c.inT)} tokens</span></div>
      <div class="li"><span class="k">Text it writes</span><span class="v num">${usd(c.write*v)}</span><span class="d">${pages(t.pout)} per ${esc(job.unit)}</span></div>
      <div class="li"><span class="k">Thinking before it answers</span><span class="v num">${usd(c.think*v)}</span><span class="d">Charged like written text. Estimated for now; Bench will measure it for each model.</span></div>
      <div class="li"><span class="k">Savings from repeated text</span><span class="v num">${c.save*v>0?'−'+usd(c.save*v):'$0'}</span><span class="d">${cacheNote}</span></div>
      <div class="li tot"><span class="k">About a month</span><span class="v num">${usd(c.month)}</span><span class="d">${usdTask(c.task)} per ${esc(job.unit)} × ${nf(v)}</span></div>
    </div>`;
  const pin=el.querySelector('#e-pin'), pout=el.querySelector('#e-pout');
  pin.addEventListener('change',()=>{const x=parseFloat(pin.value); if(x>0){state.task[state.job].pin=x; render();}});
  pout.addEventListener('change',()=>{const x=parseFloat(pout.value); if(x>0){state.task[state.job].pout=x; render();}});
  el.querySelector('#e-cache').addEventListener('change',e=>{state.caching=e.target.checked; render();});
  if(focused){const f=document.getElementById(focused); f&&f.focus();}
}
function renderSrc(C){
  const job=C.job, r=C.bv;
  const labels=[...new Set(C.rows.map(x=>x.lab))];
  document.getElementById('h-src').textContent=labels.join(' and ');
  const fp=C.fullPass[r.m+'|'+r.lv];
  document.getElementById('b-src').innerHTML=`<div class="src">
    <dl>
      <dt>The test</dt><dd><a href="${job.benchUrl}" target="_blank" rel="noopener">${esc(job.bench)}</a>. ${esc(job.what)}</dd>
      <dt>${esc(r.model.name)}</dt><dd><span class="badge">${esc(r.lab)}</span>scored ${r.s}%${levelText(r.lv)?' '+esc(levelText(r.lv)):''}${fp!=null?`, and fully finished ${Math.round(fp)} of 100 tasks`:''}. Source: ${esc(r.src)}${r.u?' (not yet checked against the original page)':''}.</dd>
      <dt>Prices</dt><dd>Each lab's published list price, checked ${esc(PRICES_CHECKED)}. ${r.model.open?'Open-weight model: price from its maker.':''}</dd>
      <dt>Fair comparison</dt><dd>Only scores measured under the same conditions can pick a winner. ${C.left.length} of 15 models don't have one for this job yet.</dd>
    </dl></div>`;
}

function render(except){
  syncControls(except);
  const C=compute();
  renderVerdict(C); renderField(C); renderBill(C); renderSrc(C);
}

/* theme: sunrise / sunset wipe (brand signature), instant when reduced motion */
document.getElementById('theme').addEventListener('click',()=>{
  const root=document.documentElement;
  const cur=root.dataset.theme || (matchMedia('(prefers-color-scheme: light)').matches?'light':'dark');
  const next=cur==='dark'?'light':'dark';
  const apply=()=>{root.dataset.theme=next;};
  if(!document.startViewTransition||matchMedia('(prefers-reduced-motion: reduce)').matches){apply();return;}
  const vt=document.startViewTransition(apply);
  vt.ready.then(()=>root.animate({clipPath:[next==='light'?'inset(100% 0 0 0)':'inset(0 0 100% 0)','inset(0)']},{duration:700,easing:'cubic-bezier(.25,.1,.25,1)',pseudoElement:'::view-transition-new(root)'}));
});

fillControls();
render();
if(document.fonts&&document.fonts.ready)document.fonts.ready.then(sizeFields);
