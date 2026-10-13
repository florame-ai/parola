import {norm} from './engine.mjs';
/** A missing target voice never becomes a voice in the wrong language. */
export class AudioPlayer {
 constructor(manifest,embedded={},onError=()=>{}){this.manifest=manifest;this.embedded=embedded;this.onError=onError;this.serial=0;this.active=null;this.voices=[];this.cancelPending=null;this.syncVoices();globalThis.speechSynthesis?.addEventListener?.('voiceschanged',()=>this.syncVoices());}
 syncVoices(){try{this.voices=globalThis.speechSynthesis?.getVoices?.()||[];}catch{this.voices=[];}}
 voice(lang){this.syncVoices();return this.voices.find(v=>v.lang.toLowerCase().split(/[-_]/)[0]===lang);}
 entry(lang,text,context=''){const key=`${lang}|${norm(text,lang)}`;return this.manifest.entries[key+'|'+context]||this.manifest.entries[key];}
 available(lang){return this.manifest.languages.includes(lang)||Boolean(this.voice(lang));}
 stop(){this.serial++;if(this.cancelPending)this.cancelPending(false);this.cancelPending=null;if(this.active){this.active.pause();this.active=null;}try{globalThis.speechSynthesis?.cancel();}catch{}}
 async speak(lang,text,{rate=1,preference='offline',context=''}={}){
  this.stop();const serial=this.serial;const ent=this.entry(lang,text,context);const device=this.voice(lang);
  const order=preference==='auto'?[['device',device],['file',ent]]:[['file',ent],['device',device]];
  for(const [kind,v] of order){if(!v)continue;try{const success=await(kind==='file'?this.playFile(v,rate,serial):this.playVoice(v,lang,text,rate,serial));if(success)return true;if(serial!==this.serial)return false;}catch{if(serial!==this.serial)return false;}}
  if(serial===this.serial)this.onError('audioUnavailable');return false;
 }
 playFile(entry,rate,serial){return new Promise(resolve=>{
  let settled=false;const source=this.embedded[entry.path]||entry.path;const el=new Audio(source);this.active=el;el.playbackRate=rate;el.preservesPitch=true;
  const done=ok=>{if(settled)return;settled=true;clearTimeout(timeout);el.onended=null;el.onerror=null;if(this.active===el)this.active=null;this.cancelPending=null;if(!ok)el.pause();resolve(ok&&serial===this.serial);};
  const timeout=setTimeout(()=>done(false),45000);this.cancelPending=()=>done(false);el.onended=()=>done(true);el.onerror=()=>done(false);el.play().catch(()=>done(false));
 });}
 playVoice(voice,lang,text,rate,serial){return new Promise(resolve=>{
  if(!globalThis.speechSynthesis||!globalThis.SpeechSynthesisUtterance){resolve(false);return;}let settled=false;const u=new SpeechSynthesisUtterance(text);u.voice=voice;u.lang=voice.lang;u.rate=rate;u.volume=1;
  const done=ok=>{if(settled)return;settled=true;clearTimeout(timer);this.cancelPending=null;resolve(ok&&serial===this.serial);};const timer=setTimeout(()=>done(false),45000);this.cancelPending=()=>done(false);u.onend=()=>done(true);u.onerror=()=>done(false);try{speechSynthesis.speak(u);}catch{done(false);}
 });}
}
