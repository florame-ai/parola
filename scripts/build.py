"""Build a dependency-free static site and an optional single-file offline edition."""
import pathlib,json,re,base64,argparse,html as markup
R=pathlib.Path(__file__).resolve().parents[1]
version=(R/'VERSION').read_text(encoding='utf-8').strip()
p=argparse.ArgumentParser();p.add_argument('--standalone',type=pathlib.Path);p.add_argument('--require-all-audio',action='store_true');a=p.parse_args()
course=json.loads((R/'data/course.json').read_text(encoding='utf-8'));ui=json.loads((R/'data/ui.json').read_text(encoding='utf-8'));manifest=json.loads((R/'audio/manifest.json').read_text(encoding='utf-8'))
requests=json.loads((R/'data/audio-requests.json').read_text(encoding='utf-8'))
missing=[k for k,v in requests.items() if k not in manifest['entries'] or not (R/manifest['entries'][k]['path']).is_file() or manifest['entries'][k].get('lang')!=v['lang']]
if a.require_all_audio and missing:raise SystemExit(f'Release blocked: {len(missing)} missing or mismatched audio entries. First: {missing[:5]}')
css=(R/'src/styles.css').read_text(encoding='utf-8');js='\n'.join(re.sub(r'^import .*?;\n','', (R/'src'/f).read_text(encoding='utf-8'),flags=re.M).replace('export ','') for f in ['engine.mjs','storage.mjs','icons.mjs','audio.mjs','app.mjs'])
def html(embedded):
 data=json.dumps({'COURSE':course,'UI':ui,'MANIFEST':manifest,'AUDIO':embedded,'VERSION':version},ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
 return '<!doctype html>\n<html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#1b6567"><meta name="description" content="Parola: Mahjong, frasi e lingue. Un gioco autonomo in italiano, inglese, arabo e russo."><title>Parola 6 — Mahjong delle lingue</title><meta name="application-name" content="Parola 6"><link rel="icon" href="./icon.svg" type="image/svg+xml"><style>'+css+'</style></head><body><div id="app"></div><div id="announcer" class="sr-only" aria-live="polite"></div><script>globalThis.PAROLA_DATA='+data+';</script><script type="module">'+js+"\nif(location.protocol!=='file:'&&'serviceWorker' in navigator){addEventListener('load',()=>navigator.serviceWorker.register('./sw.js').catch(()=>{}));}\n"+'</script></body></html>'
def hosted(document):
 return document.replace('<title>Parola 6 —',f'<title>Parola {version} —').replace('</head>',f'<meta name="application-version" content="{version}"><link rel="manifest" href="./manifest.webmanifest"></head>')
(R/'index.html').write_text(hosted(html({})),encoding='utf-8',newline='\n');print('Static site:',R/'index.html')
if a.standalone:
 audio={v['path']:'data:audio/mpeg;base64,'+base64.b64encode((R/v['path']).read_bytes()).decode() for v in manifest['entries'].values()}
 document=html(audio)
 if a.standalone.resolve()==(R/'index.html').resolve():document=hosted(document)
 else:document=document.replace('<link rel="icon" href="./icon.svg" type="image/svg+xml">','')
 a.standalone.write_text(document,encoding='utf-8',newline='\n');print('Standalone:',a.standalone,'bytes',a.standalone.stat().st_size)

# Public release notes share the source changelog with the repository.
notes=[];in_list=False
for line in (R/'CHANGELOG.md').read_text(encoding='utf-8').splitlines():
 if not line.startswith('- ') and in_list:notes.append('</ul>');in_list=False
 if line.startswith('# '):notes.append('<h1>'+markup.escape(line[2:])+'</h1>')
 elif line.startswith('## '):notes.append('<h2>'+markup.escape(line[3:])+'</h2>')
 elif line.startswith('- '):
  if not in_list:notes.append('<ul>');in_list=True
  notes.append('<li>'+markup.escape(line[2:])+'</li>')
 elif line.strip():notes.append('<p>'+markup.escape(line)+'</p>')
if in_list:notes.append('</ul>')
(R/'changelog.html').write_text('<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Aggiornamenti — Parola '+version+'</title><meta name="application-version" content="'+version+'"><link rel="icon" href="./icon.svg"><style>body{margin:0;background:#f8f7f3;color:#183f43;font:17px/1.65 system-ui,sans-serif}main{max-width:740px;margin:0 auto;padding:32px 24px 64px}a{color:#1b6567}h1{line-height:1.2}h2{margin-top:36px}li{margin:8px 0}a:focus-visible{outline:3px solid #7461a4;outline-offset:4px}</style></head><body><main><a href="./">← Torna al gioco</a>'+''.join(notes)+'</main></body></html>',encoding='utf-8',newline='\n')
