/** Parola v6 — pure Mahjong geometry and language-game logic. No DOM dependencies. */
export const LANGS = ['it','en','ar','ru'];
export const MODES = ['pair','listen','complete','compose','write'];
export function norm(text, lang='it') {
  let s=String(text).normalize('NFC').toLocaleLowerCase(lang).replace(/[’‘`]/g,"'");
  if(lang==='ar') s=s.replace(/[\u064B-\u065F\u0670\u0640]/g,'');
  // Preserve lexical letters and accents: Italian e != è; Russian е != ё.
  return s.replace(/[.,!?؟،؛:;…«»“”"()]/g,' ').replace(/\s+/g,' ').trim();
}
export function tokens(text) { return String(text).replace(/[.,!?؟،؛:;…«»“”"()]/g,' ').replace(/\s+/g,' ').trim().split(' ').filter(Boolean); }
export function rng(seed) { let a=seed>>>0;return ()=>{a+=0x6D2B79F5;let t=a;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return ((t^(t>>>14))>>>0)/4294967296;}; }
export function shuffled(a,random=Math.random){a=[...a];for(let i=a.length-1;i>0;i--){let j=Math.floor(random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
export function geometry(n, words=false){
 if(!Number.isInteger(n)||n<1||n>120)throw Error('Invalid tile count');
 const cols=words?5:4, top=n>=12?4:n>=8?2:0,base=n-top,out=[];
 for(let i=0;i<base;i++)out.push({id:i,x:i%cols,y:Math.floor(i/cols),z:0,gone:false});
 for(let i=0;i<top;i++)out.push({id:base+i,x:top===2?1:1+i%2,y:top===2?i:Math.floor(i/2),z:1,gone:false});
 return out;
}
export function free(t,board){
 if(!t||t.gone)return false;
 if(board.some(o=>!o.gone&&o.z>t.z&&Math.abs(o.x-t.x)<0.95&&Math.abs(o.y-t.y)<0.95))return false;
 const side=d=>board.some(o=>!o.gone&&o.z===t.z&&o.y===t.y&&Math.abs(o.x-(t.x+d))<0.05);
 return !side(-1)||!side(1);
}
export function freeTiles(board){return board.filter(t=>free(t,board));}
function pairPlan(positions,random){
 for(let attempt=0;attempt<160;attempt++){
  const work=positions.map(t=>({...t})),plan=[];
  while(work.some(t=>!t.gone)){
   const avail=shuffled(freeTiles(work),random);if(avail.length<2)break;
   const [a,b]=avail;plan.push([a.id,b.id]);a.gone=b.gone=true;
  }
  if(work.every(t=>t.gone))return plan;
 }
 throw Error('No geometric pair plan found');
}
export function makePairs(entries,target,support,random=Math.random,positions=null){
 if(target===support||!LANGS.includes(target)||!LANGS.includes(support))throw Error('Two distinct supported languages required');
 const board=(positions||geometry(entries.length*2)).map(t=>({...t}));
 const active=board.filter(t=>!t.gone);if(active.length!==entries.length*2)throw Error('Tile / entry mismatch');
 const plan=pairPlan(board,random),byId=new Map(board.map(t=>[t.id,t]));
 for(const [i,pair] of plan.entries()){
  const ent=entries[i];for(const [j,id] of shuffled(pair,random).entries())Object.assign(byId.get(id),{itemId:ent.id,pairKey:ent.id,type:j?'support':'target',lang:j?support:target,text:ent.text[j?support:target]});
 }
 return board;
}
export function pairHint(board){const a=freeTiles(board);for(let i=0;i<a.length;i++)for(let j=i+1;j<a.length;j++)if(a[i].pairKey===a[j].pairKey&&a[i].type!==a[j].type)return[a[i].id,a[j].id];return[];}
export function makeSequence(payloads,random=Math.random,positions=null){
 const board=(positions||geometry(payloads.length,true)).map(t=>({...t}));
 const work=board.map(t=>({...t})),byId=new Map(board.map(t=>[t.id,t]));
 if(work.filter(t=>!t.gone).length!==payloads.length)throw Error('Sequence tile mismatch');
 for(const p of payloads){const av=freeTiles(work);if(!av.length)throw Error('No free tile in sequence');const chosen=av[Math.floor(random()*av.length)];Object.assign(byId.get(chosen.id),p);chosen.gone=true;}
 return board;
}
export function payloadsFor(items,lang){return items.flatMap(item=>tokens(item.text[lang]).map((text,i)=>({text,lang,itemId:item.id,tokenIndex:i,type:'word'})));}
export function matchesText(item,text,lang){return (item.accepted?.[lang]||[item.text[lang]]).some(a=>norm(a,lang)===norm(text,lang));}
export function prefixMatch(words,phrase,lang){const ts=tokens(phrase);return words.length<=ts.length&&words.every((w,i)=>norm(w,lang)===norm(ts[i],lang));}
export function canSpell(words,board,lang){const counts=Object.create(null);for(const t of board.filter(t=>!t.gone)){const w=norm(t.text,lang);counts[w]=(counts[w]||0)+1;}for(const w0 of words){const w=norm(w0,lang);if(!counts[w])return false;counts[w]--;}return true;}
export function sentenceOptions(items,words,board,lang,exclude=[]){
 return items.filter(i=>!exclude.includes(i.id)).flatMap(item=>(item.accepted?.[lang]||[item.text[lang]]).filter(p=>prefixMatch(words,p,lang)&&canSpell(tokens(p).slice(words.length),board,lang)).map(text=>({item,text,remaining:tokens(text).slice(words.length)})));
}
export function sequenceHint(board,word,lang){return freeTiles(board).filter(t=>norm(t.text,lang)===norm(word,lang)).map(t=>t.id).slice(0,1);}
export function repairSequence(board,required,lang,random=Math.random){
 const remaining=board.filter(t=>!t.gone).map(t=>({text:t.text,lang:t.lang,itemId:t.itemId,tokenIndex:t.tokenIndex,type:t.type})),ordered=[];
 for(const word of required){const i=remaining.findIndex(t=>norm(t.text,lang)===norm(word,lang));if(i<0)throw Error('Required token missing');ordered.push(...remaining.splice(i,1));}
 return makeSequence([...ordered,...shuffled(remaining,random)],random,board);
}
export function routeKey(settings){if(!LANGS.includes(settings.target)||!LANGS.includes(settings.support)||settings.target===settings.support)throw Error('Invalid direction');return `${settings.support}>${settings.target}`;}
export function localDay(now=Date.now()){const d=new Date(now);return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;}
export function newProgress(){return{version:6,settings:{target:'it',support:'en',ui:'it',voice:'offline',effects:true,labels:true,large:false},missions:{},memory:{},seen:[],days:[],active:null};}
export function memoryKey(route,skill,item){return `${route}|${skill}|${item}`;}
export function updateMemory(prev,success,assisted,now=Date.now()) {
 if(!Number.isFinite(now)||now<0)throw Error('Invalid review timestamp');
 const p=prev||{stage:0,tries:0,independent:0,last:0,due:0};
 const sameDay=Boolean(p.last)&&localDay(p.last)===localDay(now);
 const eligible=!p.last||(!sameDay&&p.due<=now);
 let stage=p.stage;
 if(!success)stage=0;
 else if(!assisted&&eligible)stage=Math.min(5,stage+1);
 const interval=[0,1,3,7,14,30][stage];
 let due=p.due;
 if(!success||assisted)due=now+600000;
 else if(eligible)due=now+Math.max(1,interval)*86400000;
 // Successful EARLY practice must not postpone an existing review date.
 // `last` is the last scheduled assessment, not the last casual practice.
 const last=(!success||assisted||eligible)?now:p.last;
 return {stage,tries:p.tries+1,independent:p.independent+Number(success&&!assisted),last,due,assisted:Boolean(assisted),correct:Boolean(success)};
}
export function validateProgress(p){
 if(!p||![5,6].includes(p.version)||typeof p.missions!=='object'||!p.missions||Array.isArray(p.missions)||typeof p.memory!=='object'||!p.memory||Array.isArray(p.memory)||!Array.isArray(p.seen)||!Array.isArray(p.days))throw Error('Invalid progress file');
 routeKey(p.settings);if(!LANGS.includes(p.settings.ui))throw Error('Invalid UI language');
 const clean=newProgress();
 for(const k of ['target','support','ui','voice','effects','labels','large'])if(Object.hasOwn(p.settings,k))clean.settings[k]=p.settings[k];
 clean.settings.voice=['offline','auto'].includes(clean.settings.voice)?clean.settings.voice:'offline';
 for(const k of ['effects','labels','large'])clean.settings[k]=Boolean(clean.settings[k]);
 const safeKey=k=>/^(it|en|ar|ru)>(it|en|ar|ru)\|[a-z_]+\|[a-z_0-9]+$/.test(k);
 for(const [k,v]of Object.entries(p.missions).slice(0,10000))if(safeKey(k)&&v&&Number.isFinite(v.score)&&v.score>=0&&v.score<=10000)clean.missions[k]={score:v.score,stars:Math.min(3,Math.max(1,Number.isFinite(v.stars)?Math.floor(v.stars):1)),done:true,date:Number.isFinite(v.date)?Math.max(0,v.date):0};
 for(const [k,v]of Object.entries(p.memory).slice(0,20000))if(safeKey(k)&&v&&Number.isFinite(v.due)&&Number.isFinite(v.stage))clean.memory[k]={stage:Math.min(5,Math.max(0,Math.floor(v.stage))),tries:Math.min(1000000,Math.max(0,Number.isFinite(v.tries)?Math.floor(v.tries):0)),independent:Math.min(1000000,Math.max(0,Number.isFinite(v.independent)?Math.floor(v.independent):0)),last:Math.max(0,Number.isFinite(v.last)?v.last:0),due:Math.max(0,v.due),assisted:Boolean(v.assisted),correct:Boolean(v.correct)};
 clean.seen=[...new Set(p.seen.filter(v=>typeof v==='string'&&v.length<80))].slice(0,2000);
 clean.days=[...new Set(p.days.filter(v=>/^\d{4}-\d{2}-\d{2}$/.test(v)))].slice(0,5000);
 return clean;
}
export function mergeProgress(a,b){
 const out=validateProgress(a),other=validateProgress(b);
 for(const [k,v]of Object.entries(other.missions))if(!out.missions[k]||out.missions[k].score<v.score)out.missions[k]=v;
 for(const [k,v]of Object.entries(other.memory))if(!out.memory[k]||out.memory[k].last<v.last)out.memory[k]=v;
 out.seen=[...new Set([...out.seen,...other.seen])];out.days=[...new Set([...out.days,...other.days])].sort();return out;
}
