import test from 'node:test';
import assert from 'node:assert/strict';
import {newProgress,validateProgress,updateMemory,MODES} from '../src/engine.mjs';
import {loadSaved,saveSafely} from '../src/storage.mjs';
class MemoryStorage {
 constructor(){this.data=new Map();this.fail=false;}
 getItem(k){return this.data.get(k)??null;}
 setItem(k,v){if(this.fail)throw Error('Quota exceeded');this.data.set(k,String(v));}
}
const validator=validateProgress,key='v6';
test('v6 has five modes and migrates v5 progress without changing the input',()=>{
 assert.deepEqual(MODES,['pair','listen','complete','compose','write']);
 const p=newProgress();p.version=5;p.missions['en>it|pair|greetings']={score:90,stars:2,date:100};
 const migrated=validateProgress(p);assert.equal(migrated.version,6);assert.equal(p.version,5);assert.equal(migrated.missions['en>it|pair|greetings'].score,90);
});
test('early success on a different day keeps the original review deadline and assessment timestamp',()=>{
 const now=Date.parse('2026-10-13T10:00:00Z');
 const p={stage:3,tries:5,independent:4,last:now,due:now+7*86400000};
 let q=updateMemory(p,true,false,now+86400000);
 assert.equal(q.due,p.due);assert.equal(q.last,p.last);assert.equal(q.stage,3);
 q=updateMemory(q,true,false,p.due-1000);assert.equal(q.due,p.due);
 q=updateMemory(q,true,false,p.due);assert.equal(q.stage,4);assert.equal(q.due,p.due+14*86400000);
});
test('repeated early study cannot postpone a scheduled check indefinitely',()=>{
 const now=Date.parse('2026-10-13T10:00:00Z');let p={stage:3,tries:1,independent:1,last:now,due:now+7*86400000},deadline=p.due;
 for(let day=1;day<7;day++)p=updateMemory(p,true,false,now+day*86400000);
 assert.equal(p.due,deadline);assert.equal(p.stage,3);
});
test('negative or nonfinite review timestamps rejected',()=>{
 for(const n of [NaN,Infinity,-1])assert.throws(()=>updateMemory(null,true,false,n));
});
test('first save includes a recovery copy and next save keeps previous valid data',()=>{
 const st=new MemoryStorage(),p=newProgress();assert.ok(saveSafely(st,key,p,validator));assert.ok(st.getItem(key+'.backup'));
 p.days=['2026-10-13'];assert.ok(saveSafely(st,key,p,validator));assert.deepEqual(JSON.parse(st.getItem(key+'.backup')).days,[]);
});
test('corrupt primary recovers previous save; corruption cannot overwrite backup',()=>{
 const st=new MemoryStorage(),p=newProgress();saveSafely(st,key,p,validator);const backup=st.getItem(key+'.backup');
 st.setItem(key,'{corrupt');const recovered=loadSaved(st,key,validator,newProgress);
 assert.ok(recovered.recovered);assert.equal(recovered.source,key+'.backup');assert.equal(recovered.value.version,6);
 recovered.value.days=['2026-10-13'];saveSafely(st,key,recovered.value,validator);assert.equal(st.getItem(key+'.backup'),backup);
});
test('read of a v5 legacy key leaves the legacy content intact',()=>{
 const st=new MemoryStorage(),p=newProgress();p.version=5;st.setItem('legacy',JSON.stringify(p));const raw=st.getItem('legacy');
 const loaded=loadSaved(st,key,validator,newProgress,['legacy']);assert.equal(loaded.value.version,6);assert.equal(st.getItem('legacy'),raw);
});
test('quota errors do not destroy the last primary save',()=>{
 const st=new MemoryStorage(),p=newProgress();saveSafely(st,key,p,validator);const raw=st.getItem(key);st.fail=true;
 p.days=['2026-10-13'];assert.equal(saveSafely(st,key,p,validator),false);assert.equal(st.getItem(key),raw);
});
test('unavailable storage returns a playable fresh session',()=>{
 const st={getItem(){throw Error('blocked');}};const p=loadSaved(st,key,validator,newProgress);assert.equal(p.ok,false);assert.equal(p.value.version,6);
});
test('invalid save data cannot replace valid primary or backup',()=>{
 const st=new MemoryStorage(),p=newProgress();saveSafely(st,key,p,validator);const raw=st.getItem(key),bak=st.getItem(key+'.backup');
 assert.equal(saveSafely(st,key,{version:6},validator),false);assert.equal(st.getItem(key),raw);assert.equal(st.getItem(key+'.backup'),bak);
});
