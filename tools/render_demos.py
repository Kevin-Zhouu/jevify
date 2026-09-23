#!/usr/bin/env python3
"""Minimal, data-backed latency replays. No new inference or fabricated answers."""
import hashlib, json, math, os, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'docs/demos'
SOURCE=ROOT/'eval/results/dev-03/anthropic_classification-codex-headless/original/JEV_PARITY.json'
rows=json.loads(SOURCE.read_text())['sites'][0]['rows']
# First accepted, matching repo fixture in each distinct category, in source order.
queue=[]; seen=set()
for r in rows:
    if r['provenance']=='repo' and not r['fallback_taken'] and r['jev_answer']==r['original_answer'] and r['jev_answer'] not in seen:
        queue.append(r); seen.add(r['jev_answer'])
    if len(queue)==6: break
billing=next(r for r in queue if r['jev_answer']=='Billing Inquiries')
captions={'Claims Assistance':'My parked car was hit.','Quotes and Proposals':'Can you beat my current quote?',
'Account Management':"I can’t sign in.",'Billing Inquiries':'Why is my bill higher?',
'Billing Disputes':'I don’t recognize this charge.','Claims Disputes':'Why was my claim denied?'}
W,H,FPS=1280,720,30
BG='#0c1010'; WHITE='#eef3ef'; MUTED='#8b9890'; GREEN='#c4fa72'; CORAL='#e6ae94'
FD=Path(os.environ.get('JEVIFY_DEMO_FONTS','/System/Library/Fonts/Supplemental'))
fonts={}
def font(n,b=False):
    key=(n,b)
    if key not in fonts: fonts[key]=ImageFont.truetype(str(FD/('Arial Bold.ttf' if b else 'Arial.ttf')),n)
    return fonts[key]
def frame(batch,mode,t):
    im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
    def text(x,y,s,n=22,c=WHITE,b=False): d.text((x,y),s,font=font(n,b),fill=c)
    def center(x,y,s,n=22,c=WHITE,b=False): text(x-d.textlength(s,font=font(n,b))/2,y,s,n,c,b)
    def box(x,y,x2,y2,c,outline=None): d.rounded_rectangle((x,y,x2,y2),radius=18,fill=c,outline=outline,width=2)
    text(42,28,'jevify',24,b=True); text(1044,31,'MEASURED REPLAY',15,MUTED)
    center(640,79,'Route one ticket.' if mode=='single' else 'Clear the inbox.',38,b=True)
    if mode=='single':
        center(640,135,'“Why is my bill higher?”',25,MUTED)
    else: center(640,135,'6 tickets. Same decisions.',25,MUTED)
    elapsed=max(0,t-2)
    totals=[]
    for side,x in enumerate((42,658)):
        accent=CORAL if side==0 else GREEN
        times=[r['original_latency_ms' if side==0 else 'latency_ms']/1000 for r in batch]
        total=sum(times); totals.append(total)
        cumulative=[]; acc=0
        for n in times: acc+=n; cumulative.append(acc)
        completed=sum(elapsed>=v for v in cumulative)
        done=completed==len(batch)
        box(x,198,x+580,611,'#151c19',accent if done else '#2c3530')
        center(x+290,217,'CLAUDE' if side==0 else 'JEV',42,accent,True)
        center(x+290,273,'Haiku 4.5' if side==0 else '1.13',17,MUTED)
        center(x+290,312,f'{min(elapsed,total):.2f}s',88,WHITE,True)
        if mode=='single':
            # Envelope becomes a routed card; no artificial token streaming.
            box(x+82,432,x+498,513,'#243023' if done else '#202824')
            center(x+290,456,'Billing Inquiries' if done else ('Ready' if t<2 else 'Routing…'),27,accent if done else MUTED,True)
        else:
            center(x+290,417,f'{completed} / {len(batch)} routed',27,accent,True)
            for j in range(len(batch)):
                xx=x+64+j*78
                box(xx,474,xx+63,520,accent if j<completed else '#263029')
                center(xx+31,484,str(j+1),22,BG if j<completed else MUTED,True)
            active=batch[min(completed,len(batch)-1)]
            center(x+290,543,'Inbox empty' if done else captions[active['jev_answer']],21,accent if done else MUTED)
        if mode=='single': center(x+290,546,'Routed' if done else '',20,accent)
    if elapsed>=max(totals):
        center(640,637,f'{totals[0]/totals[1]:.1f}× faster'+(' on this ticket' if mode=='single' else ' in this selected queue'),28,GREEN,True)
    else: center(640,637,'Same input. Same start.' if t<2 else '',23,MUTED)
    center(640,688,'1× timing replay • OpenRouter • Selected cases • Shortened ticket previews',15,MUTED)
    return im

OUT.mkdir(parents=True,exist_ok=True); ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
scenes=[('01-ticket-race',[billing],'single',8),('02-inbox-race',queue,'queue',12)]
manifest={'kind':'visual replay of archived live API timings; not a fresh recording',
'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
'new_api_calls':False,'selection':'first accepted matching repository fixture for each of first six distinct categories; single-ticket scene uses the billing-inquiry member',
'previews':'Human-written shortened previews; models received the full original inputs in the rows below.',
'queue':'Illustrative serial replay of separately measured calls, one in flight per model. Totals are sums, not measured batch throughput.',
'full_set':'21/22 accepted matches, 14/36 fallbacks; these scenes select accepted matching cases only.',
'scenes':[]}
for name,batch,mode,seconds in scenes:
    p=subprocess.Popen([ffmpeg,'-y','-loglevel','error','-f','rawvideo','-vcodec','rawvideo','-s',f'{W}x{H}','-pix_fmt','rgb24','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/f'{name}.mp4')],stdin=subprocess.PIPE)
    for n in range(FPS*seconds): p.stdin.write(frame(batch,mode,n/FPS).tobytes())
    p.stdin.close()
    if p.wait(): raise RuntimeError('ffmpeg failed')
    frame(batch,mode,seconds-1).save(OUT/f'{name}.png')
    manifest['scenes'].append({'file':f'{name}.mp4','seconds':seconds,'rows':batch,
      'claude_total_ms':sum(r['original_latency_ms'] for r in batch),'jev_total_ms':sum(r['latency_ms'] for r in batch)})
    print(name,flush=True)
concat=OUT/'concat.txt'; concat.write_text(''.join(f"file '{name}.mp4'\n" for name,*_ in scenes))
subprocess.run([ffmpeg,'-y','-loglevel','error','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(OUT/'claude-vs-jev.mp4')],check=True); concat.unlink()
subprocess.run([ffmpeg,'-y','-loglevel','error','-i',str(OUT/'claude-vs-jev.mp4'),'-filter_complex','fps=10,scale=800:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer','-loop','0',str(OUT/'preview.gif')],check=True)
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
