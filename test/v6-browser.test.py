"""v6 regression checks on real localhost origin, including browser persistence and offline reload."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import json,time
R=Path(__file__).resolve().parents[1]
class QuietHandler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(R.parent)))
Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/{R.name}/'
results=[]
def passed(name,**details):
 results.append(dict(check=name,passed=True,**details));print('PASS',name,details,flush=True)
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
  context=browser.new_context(viewport={'width':1360,'height':950},accept_downloads=True)
  page=context.new_page();errors=[];missing=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.on('console',lambda m:missing.append(m.text) if 'Missing translation' in m.text else None)
  page.goto(url);page.wait_for_function('!!window.Parola');page.set_default_timeout(6000)
  assert page.evaluate('Parola.state.store.version')==6
  assert page.locator('.unitcard').count()==24
  page.evaluate("Parola.intro('identity','write')");assert page.locator('.mode-card').count()==5
  passed('v6 boot with five modes on a repository subdirectory')
  # Native HTML audio, not a playback mock.
  for lang in ['it','en','ru']:
   ok=page.evaluate("async l=>{const item=Parola.data.items.find(i=>i.id==='greetings_0');return await Parola.player.speak(l,item.text[l],{context:item.id,rate:0.8})}",lang)
   assert ok is True,lang;passed('actual MP3 playback',language=lang)
  page.evaluate("window.playAudio=Parola.player.speak.bind(Parola.player);Parola.player.speak=async()=>false;Parola.nav('settings');const cb=document.querySelector('[data-setting=effects]');cb.checked=false;cb.dispatchEvent(new Event('change',{bubbles:true}));")
  # Blank/incorrect writing must not reveal a tile; guided writing must be recorded.
  page.evaluate("Parola.setRoute('en','it','it');Parola.intro('identity','write');Parola.start()")
  tile=page.evaluate("()=>Parola.state.game.board.find(t=>t.type==='target'&&document.querySelector('.tile[data-id=\"'+t.id+'\"]').dataset.free==='true')")
  assert tile
  page.evaluate('id=>Parola.pick(id)',tile['id']);assert page.locator('#write-answer').count()==1
  page.locator('[data-action=checkWrite]').click();assert not page.evaluate('Parola.state.game.revealed.length')
  for _ in range(2):
   page.locator('#write-answer').fill('xxx');page.locator('[data-action=checkWrite]').click()
  assert page.locator('.model-box').count()==1
  answer=page.evaluate("id=>[...Parola.data.items,...Parola.data.vocab].find(i=>i.id===id).text.it",tile['itemId'])
  page.locator('#write-answer').fill(answer);page.locator('[data-action=checkWrite]').click()
  assert tile['itemId'] in page.evaluate('Parola.state.game.revealed')
  assert page.evaluate('Parola.state.game.assist')[tile['itemId']]
  assert not next(t for t in page.evaluate('Parola.state.game.board') if t['id']==tile['id'])['gone']
  passed('writing gate: blank rejected, two errors show model, correct answer reveals without removing')
  # Real localStorage reload, both allowances and writing draft survive.
  page.evaluate("Parola.help('hint');Parola.help('shuffle')")
  game=page.evaluate('Parola.state.game');page.reload();page.wait_for_function('!!window.Parola')
  page.locator('[data-action=resume]').click();restored=page.evaluate('Parola.state.game')
  assert restored['id']==game['id'];assert restored['helpUses']==game['helpUses'];assert restored['revealed']==game['revealed']
  passed('real browser reload retains board, revealed tiles and used helpers')
  # Deliberately corrupt only the primary; the app recovers a valid prior snapshot.
  page.evaluate("localStorage.setItem('parola-mahjong-v6','{corrupt')")
  page.reload();page.wait_for_function('!!window.Parola');assert page.evaluate('Parola.state.store.version')==6
  assert page.locator('[data-action=resume]').count()==1
  page.locator('[data-action=resume]').click();assert page.evaluate('Parola.state.game.id')==game['id']
  passed('corrupt primary save recovered from backup in real browser storage')
  # Migration from v5 with legacy keys preserved.
  page.evaluate("()=>{const p=Parola.state.store;p.version=5;for(const g of Object.values(p.sessions))g.version=5;localStorage.setItem('parola-mahjong-v5',JSON.stringify(p));localStorage.removeItem('parola-mahjong-v6');localStorage.removeItem('parola-mahjong-v6.backup');}")
  page.reload();page.wait_for_function('!!window.Parola');assert page.evaluate('Parola.state.store.version')==6
  assert page.evaluate("JSON.parse(localStorage.getItem('parola-mahjong-v5')).version")==5
  page.locator('[data-action=resume]').click();assert page.evaluate('Parola.state.game.id')==game['id']
  passed('v5 progress and active session migrated without deleting the old save')
  # All 12 directions complete a writing-Mahjong game using real handlers.
  page.evaluate("Parola.player.speak=async()=>false")
  solver=r'''a=>{
   Parola.setRoute(a.support,a.target,a.ui);Parola.intro(a.unit,'write');Parola.start();let moves=0;
   while(Parola.state.view==='game'&&moves++<40){const g=Parola.state.game;
    const b=g.board.filter(t=>!t.gone&&document.querySelector('.tile[data-id="'+t.id+'"]').dataset.free==='true');
    let pair;for(const x of b)for(const y of b)if(x.type==='target'&&y.type==='support'&&x.pairKey===y.pairKey)pair=[x,y];
    if(!pair)throw Error('No free pair');const [target,support]=pair;
    if(!g.revealed.includes(target.itemId)){
     Parola.pick(target.id);const input=document.querySelector('#write-answer');if(!input)throw Error('Missing writing input');
     input.value=[...Parola.data.items,...Parola.data.vocab].find(i=>i.id===target.itemId).text[a.target];Parola.checkWrite();
    }
    Parola.pick(target.id);Parola.pick(support.id);
   }
   if(Parola.state.view!=='summary')throw Error('Game did not finish');
   if(Parola.state.lastSummary.errors)throw Error('Unexpected writing errors');
   return {score:Parola.state.lastSummary.score,pairs:Parola.state.lastSummary.completed.length};
  }'''
  for target in ['it','en','ar','ru']:
   for support in ['it','en','ar','ru']:
    if target==support:continue
    result=page.evaluate(solver,dict(target=target,support=support,ui=support,unit='identity'))
    assert result['pairs']==6;passed('complete writing-Mahjong game',target=target,support=support,**result)
  # Localization matrix and responsive layout.
  page.set_viewport_size({'width':390,'height':844})
  for target in ['it','en','ar','ru']:
   for support in ['it','en','ar','ru']:
    if target==support:continue
    for ui in ['it','en','ar','ru']:
     value=page.evaluate("a=>{Parola.setRoute(a.support,a.target,a.ui);Parola.intro('identity','write');Parola.start();return {lang:document.documentElement.lang,dir:document.documentElement.dir,width:document.body.scrollWidth,viewport:innerWidth}}",dict(target=target,support=support,ui=ui))
     assert value['width']<=value['viewport']+1,value;assert value['lang']==ui;assert value['dir']==('rtl' if ui=='ar' else 'ltr')
     passed('mobile writing-mode localization',target=target,support=support,ui=ui)
  # Help remains writing-gated after the free allowance.
  page.evaluate("Parola.setRoute('en','it','it');Parola.intro('identity','pair');Parola.start();Parola.help('hint');Parola.help('hint')")
  assert page.locator('#help-answer').count()==1
  page.locator('#help-answer').fill('incorrect');page.locator('[data-action=checkHelp]').click()
  assert page.evaluate('Parola.state.game.helpUses.hint')==1
  help_id=page.evaluate('Parola.state.game.helpPending.itemId')
  answer=page.evaluate("id=>Parola.data.items.find(i=>i.id===id).text.it",help_id)
  page.locator('#help-answer').fill(answer);page.locator('[data-action=checkHelp]').click()
  assert page.evaluate('Parola.state.game.helpUses.hint')==2;passed('one free helper followed by a written-production gate')
  # Export carries sessions and v6 schema; import into a fresh store recovers them.
  page.evaluate("Parola.nav('settings')")
  with page.expect_download() as pending:page.locator('[data-action=export]').click()
  download=pending.value;export_path=R/'docs/test-progress-export.json';download.save_as(export_path)
  exported=json.loads(export_path.read_text());assert exported['version']==6;assert exported['sessions']
  page.evaluate("Parola.resetTest();Parola.nav('settings')")
  page.locator('#import-file').set_input_files(export_path)
  page.wait_for_function('Object.keys(Parola.state.store.sessions).length>0')
  passed('export/import roundtrip includes the active game')
  export_path.unlink()
  # Offline reload with same repository subdirectory and real cache storage.
  page.evaluate('navigator.serviceWorker.ready');page.wait_for_function('navigator.serviceWorker.controller!==null')
  context.set_offline(True);page.reload();page.wait_for_function('!!window.Parola')
  assert page.evaluate('Parola.state.store.version')==6
  ok=page.evaluate("Parola.player.speak('it','Ciao!',{context:'greetings_0'})")
  assert ok is True;passed('offline reload and actual embedded audio with network disabled')
  context.set_offline(False)
  page.set_viewport_size({'width':1360,'height':950});page.evaluate("Parola.setRoute('en','it','it');Parola.intro('identity','write');Parola.start()")
  page.screenshot(path=str(R/'docs/v6-desktop.png'),full_page=True)
  page.set_viewport_size({'width':390,'height':844});page.evaluate("Parola.setRoute('it','ar','ar');Parola.intro('identity','write');Parola.start()")
  page.screenshot(path=str(R/'docs/v6-mobile-ar.png'),full_page=True)
  assert not errors,errors;assert not missing,missing
  passed('no JavaScript exceptions or missing translations during this suite')
  report={'version':'6.0.0','checks':len(results),'origin':'real localhost, repository subdirectory','storage':'real browser localStorage; no storage mock','audioTested':['it','en','ru'],'arabicAudioIncluded':False,'errors':errors,'missingTranslations':missing,'results':results}
  (R/'docs/browser-v6-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
  browser.close()
finally:server.shutdown()
print('TOTAL',len(results),flush=True)
