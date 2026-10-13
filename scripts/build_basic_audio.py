"""Generate basic audio with installed eSpeak. Never substitute another language."""
import pathlib,json,re,unicodedata,hashlib,subprocess,tempfile,concurrent.futures,time
R=pathlib.Path(__file__).resolve().parents[1];C=json.load(open(R/'data/course.json'))
def norm(s,l):
 s=unicodedata.normalize('NFC',s).lower().replace('’',"'").replace('‘',"'").replace('`',"'")
 if l=='ar':s=re.sub('[\u064B-\u065F\u0670\u0640]','',s)
 return ' '.join(re.sub('[.,!?؟،؛:;…«»“”"()]',' ',s).split())
requests={}
for i in C['items']+C['vocab']:
 for l in C['languages']:
  for text in dict.fromkeys([i['text'][l],*(i.get('accepted',{}).get(l,[]))]):
   say=text
   if l=='en' and i['unitId'] in ['past','experience']:say=re.sub(r'\bread\b','red',say)
   if l=='ru' and i['unitId']=='plural':say=say.replace('Дома','Дома́')
   requests[f'{l}|{norm(text,l)}']={'lang':l,'text':text,'say':say}
  for text in re.sub('[.,!?؟،؛:;…«»“”"()]',' ',i['text'][l]).split():
   k=f'{l}|{norm(text,l)}';requests.setdefault(k,{'lang':l,'text':text,'say':text})
   if l=='en' and i['unitId'] in ['past','experience'] and text.lower()=='read':requests[k+'|'+i['id']]={'lang':l,'text':text,'say':'red','context':i['id']}
(R/'data/audio-requests.json').write_text(json.dumps(requests,ensure_ascii=False,indent=2))
voices={'it':'it','en':'en-gb','ru':'ru'}
def work(kv):
 k,v=kv;l=v['lang'];name=hashlib.sha256(k.encode()).hexdigest()[:20]+'.mp3';p=R/'audio'/name
 if not p.exists():
  with tempfile.TemporaryDirectory() as d:
   wav=pathlib.Path(d)/'s.wav'
   subprocess.run(['espeak','-v',voices[l],'-s','150','-p','48','-a','125','-w',str(wav),'--',v['say']],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(wav),'-af','highpass=f=80,alimiter=limit=0.95','-ar','22050','-ac','1','-c:a','libmp3lame','-b:a','40k',str(p)],check=True)
 if p.stat().st_size<200:raise ValueError(k)
 return k,{'path':'audio/'+name,'lang':l,'text':v['text'],'voice':'eSpeak '+voices[l],'quality':'basic-synthetic','bytes':p.stat().st_size}
start=time.time();tasks=[(k,v) for k,v in requests.items() if v['lang'] in voices]
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:entries=dict(pool.map(work,tasks))
manifest={'version':5,'languages':list(voices),'missingLanguages':['ar'],'entries':entries,'reviewedByNativeSpeakers':False,'generatedWith':'eSpeak 1.48 + FFmpeg'}
(R/'audio/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('Generated',len(entries),'clips,',round(sum(v['bytes'] for v in entries.values())/1024/1024,2),'MB in',round(time.time()-start),'seconds; Arabic NOT fabricated.')
