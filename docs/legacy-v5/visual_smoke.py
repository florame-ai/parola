from playwright.sync_api import sync_playwright
import json,pathlib,threading,http.server,functools
R=pathlib.Path(__file__).resolve().parents[1]
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(R)))
threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
 page=b.new_page(viewport={'width':1440,'height':1060},device_scale_factor=1)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content(((R.parent/'Parola-Mahjong-v5.html') if (R.parent/'Parola-Mahjong-v5.html').exists() else (R/'Parola-Mahjong-v5.html')).read_text().replace('<script>globalThis.PAROLA_DATA=', '<script>Object.defineProperty(window,"localStorage",{value:{data:{},getItem(k){return this.data[k]??null},setItem(k,v){this.data[k]=String(v)},removeItem(k){delete this.data[k]}}});globalThis.PAROLA_DATA='));page.wait_for_timeout(500)
 print('ERRORS',errors)
 page.screenshot(path=str(R/'docs/home-desktop.png'),full_page=False)
 print('STATE',page.evaluate('Parola.state.view'))
 page.evaluate("Parola.intro('identity','complete')");page.wait_for_timeout(100);page.screenshot(path=str(R/'docs/intro-desktop.png'),full_page=False)
 page.evaluate('Parola.start()');page.wait_for_timeout(100);page.screenshot(path=str(R/'docs/game-desktop.png'),full_page=True)
 page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(300);page.screenshot(path=str(R/'docs/game-mobile.png'),full_page=True)
 print('MOBILE',page.evaluate('({width:innerWidth,body:document.body.scrollWidth,board:document.querySelector(".board").getBoundingClientRect().toJSON()})'))
 page.evaluate("Parola.setRoute('ru','ar','ar');Parola.intro('identity','pair');Parola.start()");page.wait_for_timeout(200);page.screenshot(path=str(R/'docs/game-ar-mobile.png'),full_page=True)
 print('AR ERRORS',errors)
 b.close()
