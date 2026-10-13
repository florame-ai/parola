"""Build a dependency-free static site and an optional single-file offline edition."""
import pathlib,json,re,base64,argparse
R=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--standalone',type=pathlib.Path);p.add_argument('--require-all-audio',action='store_true');a=p.parse_args()
course=json.loads((R/'data/course.json').read_text());ui=json.loads((R/'data/ui.json').read_text());manifest=json.loads((R/'audio/manifest.json').read_text())
requests=json.loads((R/'data/audio-requests.json').read_text())
missing=[k for k,v in requests.items() if k not in manifest['entries'] or not (R/manifest['entries'][k]['path']).is_file() or manifest['entries'][k].get('lang')!=v['lang']]
if a.require_all_audio and missing:raise SystemExit(f'Release blocked: {len(missing)} missing or mismatched audio entries. First: {missing[:5]}')
css=(R/'src/styles.css').read_text();js='\n'.join(re.sub(r'^import .*?;\n','', (R/'src'/f).read_text(),flags=re.M).replace('export ','') for f in ['engine.mjs','storage.mjs','icons.mjs','audio.mjs','app.mjs'])
def html(embedded):
 data=json.dumps({'COURSE':course,'UI':ui,'MANIFEST':manifest,'AUDIO':embedded},ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
 return '<!doctype html>\n<html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#1b6567"><meta name="description" content="Parola: Mahjong, frasi e lingue. Un gioco autonomo in italiano, inglese, arabo e russo."><title>Parola 6 — Mahjong delle lingue</title><meta name="application-name" content="Parola 6"><link rel="icon" href="./icon.svg" type="image/svg+xml"><style>'+css+'</style></head><body><div id="app"></div><div id="announcer" class="sr-only" aria-live="polite"></div><script>globalThis.PAROLA_DATA='+data+';</script><script type="module">'+js+"\nif(location.protocol!=='file:'&&'serviceWorker' in navigator){addEventListener('load',()=>navigator.serviceWorker.register('./sw.js').catch(()=>{}));}\n"+'</script></body></html>'
(R/'index.html').write_text(html({}).replace('</head>','<link rel="manifest" href="./manifest.webmanifest"></head>'),encoding='utf-8');print('Static site:',R/'index.html')
if a.standalone:
 audio={v['path']:'data:audio/mpeg;base64,'+base64.b64encode((R/v['path']).read_bytes()).decode() for v in manifest['entries'].values()}
 a.standalone.write_text(html(audio).replace('<link rel="icon" href="./icon.svg" type="image/svg+xml">',''),encoding='utf-8');print('Standalone:',a.standalone,'bytes',a.standalone.stat().st_size)
