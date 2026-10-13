#!/usr/bin/env python3
"""Optional Piper pack builder. Requires locally downloaded, licensed voice models.
No network request or model download is made by this script. Not executed in this build.
Official API: https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/API_PYTHON.md
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,shutil,subprocess,tempfile,wave
R=pathlib.Path(__file__).resolve().parents[1]
def main()->None:
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--lang',required=True,choices=['it','en','ar','ru'])
 p.add_argument('--model',required=True,type=pathlib.Path,help='A genuine voice in the selected language, .onnx plus .onnx.json')
 p.add_argument('--license-reviewed',action='store_true',help='Confirm that the voice model/dataset license permits this intended use')
 args=p.parse_args()
 if not args.license_reviewed:p.error('Review the MODEL_CARD and dataset license first; then pass --license-reviewed.')
 if not args.model.is_file() or not pathlib.Path(str(args.model)+'.json').is_file():p.error('Both model.onnx and model.onnx.json are required.')
 config=json.loads(pathlib.Path(str(args.model)+'.json').read_text())
 actual=(config.get('language',{}).get('code') or config.get('espeak',{}).get('voice') or '').split('_')[0].split('-')[0]
 if actual!=args.lang:p.error(f'Voice language {actual!r} does not match requested {args.lang!r}. No substitution is allowed.')
 if not shutil.which('ffmpeg'):p.error('Install ffmpeg before generating a pack.')
 try:from piper import PiperVoice
 except ImportError:p.error('Install piper-tts in a separate environment: python -m pip install piper-tts')
 voice=PiperVoice.load(str(args.model));requests=json.loads((R/'data/audio-requests.json').read_text())
 manifest=json.loads((R/'audio/manifest.json').read_text());entries=manifest['entries'].copy();generated=[]
 with tempfile.TemporaryDirectory(prefix='parola-audio-') as tmp:
  tmp=pathlib.Path(tmp)
  for key,request in requests.items():
   if request['lang']!=args.lang:continue
   filename=hashlib.sha256(key.encode()).hexdigest()[:20]+'.mp3'
   wav=tmp/'speech.wav';mp3=tmp/filename
   # Context-specific pronunciation overrides from the authored inventory are preserved.
   with wave.open(str(wav),'wb') as out:voice.synthesize_wav(request.get('say',request['text']),out)
   with wave.open(str(wav),'rb') as inp:
    if inp.getnframes()<100:raise RuntimeError('Empty audio: '+key)
   subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(wav),'-ar','22050','-ac','1','-c:a','libmp3lame','-b:a','56k',str(mp3)],check=True,timeout=60)
   if mp3.stat().st_size<300:raise RuntimeError('Invalid encoded audio: '+key)
   entries[key]={'path':'audio/'+filename,'lang':args.lang,'text':request['text'],'voice':args.model.stem,'quality':'neural-not-human-reviewed','bytes':mp3.stat().st_size}
   generated.append((mp3,R/'audio'/filename))
  if not generated:raise RuntimeError('No requests for selected language.')
  # Existing manifest stays unchanged on synthesis failure.
  for source,destination in generated:shutil.copy2(source,destination)
 manifest['entries']=entries
 langs=['it','en','ar','ru'];manifest['languages']=[l for l in langs if all(k in entries for k,r in requests.items() if r['lang']==l)]
 manifest['missingLanguages']=[l for l in langs if l not in manifest['languages']]
 manifest['reviewedByNativeSpeakers']=False
 new=R/'audio/manifest.json.tmp';new.write_text(json.dumps(manifest,ensure_ascii=False,indent=2));new.replace(R/'audio/manifest.json')
 print(f'{len(generated)} clips generated. Human pronunciation review remains required. Rebuild the HTML next.')
if __name__=='__main__':main()
