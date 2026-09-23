#!/usr/bin/env python3
"""Render actual Claude stream events alongside Jev's complete JSON response."""
import hashlib,json,math,os,subprocess,textwrap
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/demos';SOURCE=OUT/'json-data/capture.json'
data=json.loads(SOURCE.read_text());j=data['jev'];c=data['claude']
W,H,FPS=1280,720,30;DURATION=math.ceil(2+max(j['elapsed_s'],c['elapsed_s'])+3)
BG='#0b1010';WHITE='#edf5ef';MUTED='#82938a';GREEN='#c5fc77';CORAL='#efb69b'
FD=Path(os.environ.get('JEVIFY_DEMO_FONTS','/System/Library/Fonts/Supplemental'));fonts={}
def f(n,b=False,mono=False):
 key=(n,b,mono)
 if key not in fonts: fonts[key]=ImageFont.truetype(os.environ.get('JEVIFY_DEMO_MONO','/System/Library/Fonts/Menlo.ttc') if mono else str(FD/('Arial Bold.ttf' if b else 'Arial.ttf')),n)
 return fonts[key]
def frame(t):
 im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im);elapsed=max(0,t-2)
 def text(x,y,s,n=20,color=WHITE,b=False,mono=False):d.text((x,y),s,font=f(n,b,mono),fill=color)
 def center(x,y,s,n=20,color=WHITE,b=False):text(x-d.textlength(s,font=f(n,b))/2,y,s,n,color,b)
 def box(x,y,x2,y2,color,outline=None):d.rounded_rectangle((x,y,x2,y2),radius=15,fill=color,outline=outline,width=1)
 text(35,23,'jevify',23,b=True);center(640,27,'12 tickets → structured JSON',23);text(1034,29,'LIVE CAPTURE / REPLAY',14,MUTED)
 for side,x in enumerate((35,655)):
  accent=CORAL if side==0 else GREEN;end=c['elapsed_s'] if side==0 else j['elapsed_s'];done=elapsed>=end
  center(x+295,83,'CLAUDE' if side==0 else 'JEV',36,accent,True)
  center(x+295,129,'Haiku 4.5' if side==0 else '1.13',15,MUTED)
  center(x+295,156,f'{min(elapsed,end):.2f}s',67,WHITE,True)
  if side==0:
   raw=''.join(e['text'] for e in c['events'] if e['at_s']<=elapsed)
   # Remove only markdown wrapper for JSON display; never invent streaming deltas.
   if raw.startswith('```'):
    raw=raw.partition('\n')[2]
    if raw.rstrip().endswith('```'):raw=raw.rstrip()[:-3].rstrip()
  else:raw=j['display'] if done else ''
  lines=raw.splitlines();total=len(j['display'].splitlines()) if side else len(c['raw_text'].strip().removeprefix('```json').removesuffix('```').strip().splitlines())
  status=f'COMPLETE · {total} lines' if done else ('READY' if t<2 else 'STREAMING' if raw else 'WAITING')
  box(x,249,x+590,638,'#141d18','#33442e' if done else '#253029')
  text(x+18,264,status,14,accent if done else MUTED,True)
  # Claude follows its actual growing text. Jev's entire object is ready at once.
  visible=lines[-16:] if side==0 and not done else lines[:16]
  for n,line in enumerate(visible):
   color=accent if '"choice"' in line else '#b8c9bd' if ':' in line else '#708577'
   text(x+20,296+n*20,line[:61],15,color,mono=True)
  if not raw:center(x+270,429,'{ … }',42,'#405148')
  # Mini-map shows actual response availability, not artificial typing.
  for n in range(total):
   yy=296+n*2.25
   if yy>612:break
   width=6+(n*13%23)
   d.line((x+547,yy,x+547+width,yy),fill=accent if n<len(lines) else '#26352a',width=1)
 if elapsed>=max(j['elapsed_s'],c['elapsed_s']):center(640,652,f"{c['elapsed_s']/j['elapsed_s']:.1f}× faster · 12/12 category choices match",25,GREEN,True)
 elif elapsed>=j['elapsed_s']:center(640,652,'Jev is done. Claude is still writing JSON.',25,GREEN,True)
 else:center(640,652,'Same questions. Same output fields.',23,MUTED)
 center(640,695,'Actual stream replay at 1× · OpenRouter · One synthetic example · Not a general benchmark',14,MUTED)
 return im
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
p=subprocess.Popen([ffmpeg,'-y','-loglevel','error','-f','rawvideo','-vcodec','rawvideo','-s',f'{W}x{H}','-pix_fmt','rgb24','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'claude-vs-jev.mp4')],stdin=subprocess.PIPE)
for n in range(DURATION*FPS):p.stdin.write(frame(n/FPS).tobytes())
p.stdin.close();assert p.wait()==0
frame(4).save(OUT/'json-race.png');frame(DURATION-1).save(OUT/'json-complete.png')
subprocess.run([ffmpeg,'-y','-loglevel','error','-i',str(OUT/'claude-vs-jev.mp4'),'-filter_complex','fps=12,scale=960:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer','-loop','0',str(OUT/'preview.gif')],check=True)
(OUT/'manifest.json').write_text(json.dumps({'source':'json-data/capture.json','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'duration_seconds':DURATION,'fps':FPS,'request_start_video_seconds':2,'speed':1,'claude_seconds':c['elapsed_s'],'jev_seconds':j['elapsed_s'],'ratio':c['elapsed_s']/j['elapsed_s'],'agreement':data['agreement'],'input_provenance':'synthetic','rendering':'actual timestamped Claude SSE text; Jev JSON appears on response completion; markdown fences removed only for display'},indent=2)+'\n')
print('Rendered',DURATION,'seconds')
