import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as E from '../src/engine.mjs';
const C=JSON.parse(fs.readFileSync(new URL('../data/course.json',import.meta.url)));
const U=JSON.parse(fs.readFileSync(new URL('../data/ui.json',import.meta.url)));
const unitItems=u=>C.items.filter(i=>i.unitId===u.id);
let boards=0,sequenceMoves=0,randomStalls=0;
test('24 units, 72 aligned phrases, four complete UI languages, 12 directions',()=>{
 assert.equal(C.units.length,24);assert.equal(C.items.length,72);
 for(const l of E.LANGS){assert.deepEqual(Object.keys(U[l]).sort(),Object.keys(U.it).sort());for(const v of Object.values(U[l]))assert.ok(typeof v==='string'&&v.trim());}
 for(const u of C.units){assert.equal(unitItems(u).length,3);for(const t of E.LANGS)for(const s of E.LANGS)assert.ok(u.rules[t][s]);}
 for(const i of [...C.items,...C.vocab])for(const l of E.LANGS){assert.ok(i.text[l]);assert.ok(i.accepted[l].includes(i.text[l]));}
 assert.equal(E.LANGS.flatMap(t=>E.LANGS.filter(s=>s!==t)).length,12);
});
test('precise Mahjong covering and lateral blocking rules',()=>{
 let b=[{id:0,x:0,y:0,z:0},{id:1,x:1,y:0,z:0},{id:2,x:2,y:0,z:0},{id:3,x:0,y:0,z:1}];
 assert.equal(E.free(b[0],b),false);assert.equal(E.free(b[1],b),false);assert.equal(E.free(b[2],b),true);assert.equal(E.free(b[3],b),true);
 b[0].gone=true;assert.equal(E.free(b[1],b),true);assert.equal(E.free(b[0],b),false);
});
test('all 12 directions × 24 units × 10 randomized pair boards have a solution',()=>{
 for(const target of E.LANGS)for(const support of E.LANGS.filter(s=>s!==target))for(const u of C.units)for(let seed=0;seed<10;seed++){
  const rand=E.rng(seed+u.index*211),entries=[...unitItems(u),...C.vocab.slice(0,3)];let b=E.makePairs(entries,target,support,rand);let n=0;
  while(b.some(t=>!t.gone)){let ids=E.pairHint(b);assert.equal(ids.length,2,`stall ${target}/${support}/${u.id}/${seed}`);for(const id of ids){let t=b.find(t=>t.id===id);assert.ok(E.free(t,b));t.gone=true;}n++;}
  assert.equal(n,6);boards++;
 }
});
test('random legal pair choices: record any deadlocks instead of hiding them',()=>{
 for(let seed=0;seed<2000;seed++){
 const rand=E.rng(seed),b=E.makePairs([...C.items.slice(0,3),...C.vocab.slice(0,3)],'it','ru',rand);
 while(b.some(t=>!t.gone)){const av=E.freeTiles(b),pairs=[];for(let i=0;i<av.length;i++)for(let j=i+1;j<av.length;j++)if(av[i].pairKey===av[j].pairKey&&av[i].type!==av[j].type)pairs.push([av[i],av[j]]);if(!pairs.length){randomStalls++;break;}const p=pairs[Math.floor(rand()*pairs.length)];p.forEach(t=>t.gone=true);}
 }
 assert.equal(randomStalls,0,`Random legal choices caused ${randomStalls} stalls`);
});
test('all sentence boards can be completed; alternative identical tiles repaired safely',()=>{
 for(const lang of E.LANGS)for(const u of C.units)for(let seed=0;seed<15;seed++){
 const rand=E.rng(seed*13+u.index),items=unitItems(u),payloads=E.payloadsFor(items,lang),words=payloads.map(p=>p.text);let b=E.makeSequence(payloads,rand);
 for(let n=0;n<words.length;n++){
  let candidates=E.freeTiles(b).filter(t=>E.norm(t.text,lang)===E.norm(words[n],lang));
  if(!candidates.length){b=E.repairSequence(b,words.slice(n),lang,rand);candidates=E.freeTiles(b).filter(t=>E.norm(t.text,lang)===E.norm(words[n],lang));}
  assert.ok(candidates.length,`${lang}/${u.id}/${n}`);candidates[Math.floor(rand()*candidates.length)].gone=true;sequenceMoves++;
 }
 assert.ok(b.every(t=>t.gone));boards++;
 }
});
test('prefixes, variants, ordered words and preservation of important spelling distinctions',()=>{
 for(const i of C.items)for(const l of E.LANGS){const w=E.tokens(i.text[l]);for(let k=0;k<=w.length;k++)assert.ok(E.prefixMatch(w.slice(0,k),i.text[l],l));assert.ok(E.matchesText(i,i.text[l],l));assert.equal(E.matchesText(i,'impossible خطأ nonsense xxx',l),false);}
 assert.notEqual(E.norm('e'),E.norm('è'));assert.notEqual(E.norm('е','ru'),E.norm('ё','ru'));assert.equal(E.norm('كِتاب','ar'),E.norm('كتاب','ar'));assert.notEqual(E.norm('إلى','ar'),E.norm('الى','ar'));
});
test('review spacing, same-day repetition, assistance, errors, and direction isolation',()=>{
 const now=Date.parse('2026-10-13T12:00:00Z');let p=E.updateMemory(null,true,false,now);assert.equal(p.stage,1);assert.equal(p.due,now+86400000);
 let again=E.updateMemory(p,true,false,now+1000);assert.equal(again.stage,1);assert.equal(again.due,p.due);
 let due=E.updateMemory(p,true,false,p.due+1000);assert.equal(due.stage,2);
 let help=E.updateMemory(due,true,true,due.last+2000);assert.equal(help.stage,2);assert.equal(help.due,help.last+600000);
 let wrong=E.updateMemory(due,false,false,due.last+2000);assert.equal(wrong.stage,0);
 assert.notEqual(E.memoryKey('it>ru','pair','a'),E.memoryKey('ru>it','pair','a'));assert.notEqual(E.memoryKey('it>ru','pair','a'),E.memoryKey('it>ru','listen','a'));
});
test('safe progress import and highest-score merge without accumulating duplicate XP',()=>{
 const a=E.newProgress();a.missions['en>it|pair|greetings']={score:100,stars:1,date:10};const b=E.newProgress();b.missions['en>it|pair|greetings']={score:90,stars:1,date:20};const c=E.mergeProgress(a,b);assert.equal(c.missions['en>it|pair|greetings'].score,100);assert.equal(Object.keys(c.missions).length,1);
 assert.throws(()=>E.validateProgress({version:3}));assert.throws(()=>E.validateProgress({...a,settings:{...a.settings,support:'it'}}));
 const evil=JSON.parse(JSON.stringify(a));evil.missions['<script>evil</script>']={score:900};assert.equal(Object.keys(E.validateProgress(evil).missions).length,1);
});
process.on('exit',()=>{const report={boards,sequenceMoves,randomStalls};console.log('SIMULATION_REPORT',JSON.stringify(report));fs.writeFileSync(new URL('../docs/engine-report.json',import.meta.url),JSON.stringify(report,null,2));});
