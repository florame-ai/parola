"""UI/logic checks using Chromium's set_content: URL navigation is blocked in this environment.
Storage is a transparent in-memory stand-in, not proof of disk persistence. Audio tests are separate.
"""
from playwright.sync_api import sync_playwright
from pathlib import Path
import json,time
R=Path(__file__).resolve().parents[1]
source=(R/'index.html').read_text()
shim='Object.defineProperty(window,"localStorage",{configurable:true,value:{data:{},getItem(k){return this.data[k]??null},setItem(k,v){this.data[k]=String(v)},removeItem(k){delete this.data[k]}}});'
source=source.replace('<script>globalThis.PAROLA_DATA=','<script>'+shim+'globalThis.PAROLA_DATA=')
results=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
 page=browser.new_page(viewport={'width':1440,'height':1060})
 errors=[];missing=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('console',lambda m:missing.append(m.text) if 'Missing translation' in m.text else None)
 page.set_content(source);page.wait_for_function('!!window.Parola');page.set_default_timeout(5000)
 # Real embedded audio, no mocks: validate player resolves only after actual playback.
 for lang in ['it','en','ru']:
  start=time.monotonic()
  value=page.evaluate("async l=>{const i=Parola.data.items.find(i=>i.id==='greetings_0');return await Parola.player.speak(l,i.text[l],{context:i.id,rate:0.8})}",lang)
  assert value is True,(lang,value);assert time.monotonic()-start>.25
  results.append({'check':'real embedded audio playback at 0.8x','lang':lang,'passed':True})
 # Arabic absence is explicitly surfaced; never a different-language voice.
 available=page.evaluate("Parola.player.available('ar')")
 if not available:
  ok=page.evaluate("Parola.player.speak('ar','مرحبًا!',{context:'greetings_0'})")
  assert ok is False;assert page.locator('.toast').count()==1
  results.append({'check':'Arabic absence explicitly reported, no false listening credit','passed':True})
 # Logic simulations intentionally silence speech (not an audio-availability test).
 page.evaluate("window.realSpeak=Parola.player.speak.bind(Parola.player);Parola.player.speak=async()=>false;Parola.nav('settings');const e=document.querySelector('[data-setting=effects]');e.checked=false;e.dispatchEvent(new Event('change',{bubbles:true}));")
 helper=r'''window.solve=(unit,mode,target,support)=>{
  Parola.setRoute(support,target,'it');Parola.intro(unit,mode);Parola.start();let steps=0;
  const normalize=s=>s.normalize('NFC').toLocaleLowerCase(target).replace(/[.,!?؟،؛:;…«»“”"()]/g,' ').replace(/[\u064B-\u065F\u0670\u0640]/g,'').replace(/\s+/g,' ').trim();
  const words=s=>s.replace(/[.,!?؟،؛:;…«»“”"()]/g,' ').trim().split(/\s+/);
  const free=t=>document.querySelector('.tile[data-id="'+t.id+'"]')?.dataset.free==='true';
  while(Parola.state.view==='game'&&steps++<400){const g=Parola.state.game;
   if(g.phase==='roundDone'){Parola.next();continue;}
   if(g.errors)throw Error('Unexpected error '+unit+' '+mode+' '+target+' '+JSON.stringify(g.prefix)); const b=g.board.filter(t=>!t.gone&&free(t));
   if(mode==='pair'){
    let pair;for(let i=0;i<b.length;i++)for(let j=i+1;j<b.length;j++)if(b[i].pairKey===b[j].pairKey&&b[i].type!==b[j].type)pair=[b[i],b[j]];
    if(!pair)throw Error('No free pair '+unit+' '+target);
    Parola.pick(pair[0].id);Parola.pick(pair[1].id);
   }else{
    const items=Parola.data.items.filter(i=>i.unitId===unit),p=g.prefix.map(x=>x.text);
    let opts=items.filter(i=>!g.completed.includes(i.id)).flatMap(i=>i.accepted[target].map(text=>({i,words:words(text)}))).filter(o=>p.every((v,i)=>normalize(v)===normalize(o.words[i]||'')));
    opts=opts.filter(o=>{const counts={};for(const t of g.board.filter(t=>!t.gone)){const k=normalize(t.text);counts[k]=(counts[k]||0)+1;}for(const w of o.words.slice(p.length)){const k=normalize(w);if(!counts[k])return false;counts[k]--;}return true;}); if(mode==='complete')opts=[{i:items[g.round],words:words(items[g.round].text[target])}];
    if(mode==='compose'&&opts.some(o=>o.words.length===p.length)){Parola.check();continue;}
    let next=b.find(t=>opts.some(o=>normalize(t.text)===normalize(o.words[p.length]||'')));
    if(!next)throw Error('No next word '+unit+' '+target+' '+mode+' '+p.join(' '));
    Parola.pick(next.id);
   }
  }
  if(Parola.state.view!=='summary')throw Error('No finish '+unit+' '+mode+' '+target);
  const s=Parola.state.lastSummary;if(s.errors)throw Error('Unexpected errors '+unit+' '+mode+' '+target+': '+s.errors);
  return{unit,mode,target,support,score:s.score,steps};
 };'''
 page.evaluate(helper+'; true')
 # 36 real-UI completed games, three selected units x four targets x three modes.
 for target in ['it','en','ar','ru']:
  support='en' if target!='en' else 'ru'
  for mode in ['pair','complete','compose']:
   print('GROUP',target,mode,flush=True)
   value=page.evaluate("a=>Parola.data.units.filter(u=>[1,13,23].includes(u.index)).map(u=>window.solve(u.id,a.mode,a.target,a.support))",dict(mode=mode,target=target,support=support))
   results.extend({'check':'completed UI game',**v,'passed':True} for v in value)
 # 12 directions x 4 UI languages at mobile size.
 page.set_viewport_size({'width':390,'height':844})
 for target in ['it','en','ar','ru']:
  for support in ['it','en','ar','ru']:
   if target==support:continue
   for ui in ['it','en','ar','ru']:
    stats=page.evaluate("a=>{Parola.setRoute(a.support,a.target,a.ui);Parola.intro('identity','pair');Parola.start();return {lang:document.documentElement.lang,dir:document.documentElement.dir,width:document.body.scrollWidth,viewport:innerWidth}}",dict(target=target,support=support,ui=ui))
    assert stats['width']<=stats['viewport']+1,stats
    assert stats['lang']==ui;assert stats['dir']==('rtl' if ui=='ar' else 'ltr')
    results.append({'check':'mobile localization','target':target,'support':support,'ui':ui,'passed':True})
 # Wrong answers don't consume tiles; ordering really matters.
 page.evaluate("Parola.setRoute('en','it','it');Parola.intro('identity','complete');Parola.start()")
 game=page.evaluate('Parola.state.game')
 wrong=page.evaluate("()=>{let g=Parola.state.game;return g.board.find(t=>document.querySelector('.tile[data-id=\"'+t.id+'\"]').dataset.free==='true'&&t.text.toLowerCase()!=='io')?.id}")
 assert wrong is not None
 page.evaluate('id=>Parola.pick(id)',wrong);after=page.evaluate('Parola.state.game')
 assert after['errors']==1;assert after['prefix']==[];assert not next(t for t in after['board'] if t['id']==wrong)['gone']
 results.append({'check':'wrong next tile rejected without tile loss','passed':True})
 # One free hint then written-production gate.
 page.evaluate("Parola.help('hint')");assert page.evaluate('Parola.state.game.helpUses.hint')==1
 page.evaluate("Parola.help('hint')");assert page.locator('#help-answer').count()==1
 page.locator('#help-answer').fill('');page.locator('[data-action=checkHelp]').click();assert page.evaluate('Parola.state.game.helpUses.hint')==1
 for _ in range(2):page.locator('#help-answer').fill('non è una risposta corretta');page.locator('[data-action=checkHelp]').click()
 assert page.locator('.model-box').count()==1
 hid=page.evaluate('Parola.state.game.helpPending.itemId')
 answer=page.evaluate("id=>Parola.data.items.find(i=>i.id===id).text.it",hid)
 page.locator('#help-answer').fill(answer);page.locator('[data-action=checkHelp]').click()
 assert page.evaluate('Parola.state.game.helpUses.hint')==2
 assert not page.locator('dialog').count()
 results.append({'check':'hint: one free, blank rejected, two mistakes show model, writing unlocks exactly one','passed':True})
 page.evaluate("Parola.help('shuffle');Parola.help('shuffle')")
 assert page.evaluate('Parola.state.game.helpUses.shuffle')==1;assert page.locator('dialog').count()==1
 page.locator('[data-action=closeHelp]').click()
 # Resume uses the serialized session, retaining both allowances.
 old=page.evaluate('Parola.state.game')
 page.evaluate("Parola.nav('home')");page.locator('[data-action=resume]').click()
 new=page.evaluate('Parola.state.game');assert old['helpUses']==new['helpUses'];assert old['id']==new['id'];assert old['board']==new['board']
 results.append({'check':'serialized session resume preserves board and consumed helpers (memory storage fixture)','passed':True})
 # Listening with real English mp3 must wait for ended; transcript remains flagged assisted.
 page.evaluate("Parola.player.speak=window.realSpeak;Parola.setRoute('it','en','it');Parola.intro('greetings','listen');Parola.start()")
 pair=page.evaluate("()=>{let g=Parola.state.game,b=g.board.filter(t=>document.querySelector('.tile[data-id=\"'+t.id+'\"]').dataset.free==='true');for(let a of b)for(let c of b)if(a.id!==c.id&&a.pairKey===c.pairKey&&a.type==='target'&&c.type==='support')return[a.id,c.id]}")
 page.evaluate('a=>{Parola.pick(a[0]);Parola.pick(a[1])}',pair)
 assert page.evaluate('Parola.state.game.completed.length')==0
 page.wait_for_function('Parola.state.game.heard.length>0',timeout=10000)
 page.evaluate('id=>Parola.pick(id)',pair[1]);assert page.evaluate('Parola.state.game.completed.length')==1
 page.locator('[data-action=transcript]').click()
 assert page.evaluate('Parola.state.game.transcript') is True
 results.append({'check':'real listening waits for playback ended before credit; transcript marked supported','passed':True})
 assert not errors,errors;assert not missing,missing
 report={'checks':len(results),'completedUIGames':36,'localizationConfigurations':48,'realAudioLanguages':['it','en','ru'],'errors':errors,'missingTranslations':missing,'storage':'in-memory test double; actual browser persistence not certified','results':results}
 (R/'docs/browser-existing-v6-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print(json.dumps({k:v for k,v in report.items() if k!='results'},ensure_ascii=False))
 browser.close()
