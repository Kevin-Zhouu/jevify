#!/usr/bin/env python3
"""Generate a clearly labeled illustrative UX animation, NOT a recorded run.
Requires Pillow. Sample counts, files, test results and diff are storyboard data.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import shutil
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/demos/jevify-flow.gif'
W,H=1080,510
FONT='/System/Library/Fonts/Menlo.ttc'
font=ImageFont.truetype(FONT,20);small=ImageFont.truetype(FONT,17);tiny=ImageFont.truetype(FONT,14)
BG='#101416';FG='#e5ece8';MUTED='#98a6a1';GREEN='#c5fc77';BORDER='#303b36'
frames=[];durations=[]
def frame(step):
 im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
 d.line((0,48,W,48),fill=BORDER)
 for i,c in enumerate(['#ff8075','#e9c16b','#96c879']):d.ellipse((22+i*19,20,30+i*19,28),fill=c)
 d.text((100,14),'jevify / support agent',font=small,fill=MUTED)
 d.text((834,17),'ILLUSTRATIVE DEMO',font=tiny,fill=MUTED)
 d.line((24,456,W-24,456),fill=BORDER)
 for i,label in enumerate(['01  AUDIT','02  PLAN','03  APPROVE','04  CONVERT']):
  d.text((30+i*265,476),label,font=small,fill=GREEN if i==step else '#738079')
 return im,d
def line(d,y,text,color=FG):d.text((30,y),text,font=font,fill=color)
def add(im,ms):frames.append(im);durations.append(ms)
command='> /jevify'
im,d=frame(0)
d.text((36,112),'CURRENT REPO · SUPPORT AGENT',font=small,fill=MUTED)
d.text((30,174),command,font=ImageFont.truetype(FONT,54),fill=GREEN)
d.text((36,275),'Reading the current repo…',font=font,fill=FG)
add(im,1400)
im,d=frame(1);line(d,73,command,GREEN);line(d,112,'Scanned 14 files · found 6 LLM calls')
rows=[('→ Jev','classify_ticket()','triage.py:42','picks 1 of 5 labels'),('→ Jev','is_safe()','guard.py:18','yes/no check'),('→ Jev','pick_tool()','agent.py:77','picks 1 of 8 tools'),('keep','draft_reply()','reply.py:30','writes text'),('keep','summarize()','summary.py:12','writes text'),('skip','days_until_due()','billing.py:55','date math → code')]
for i,(action,fn,path,why) in enumerate(rows):
 y=169+i*36
 for x,t in [(30,action),(136,fn),(438,path),(688,why)]:d.text((x,y),t,font=small,fill=GREEN if action=='→ Jev' else MUTED)
line(d,409,'Convert the 3 marked → Jev?',FG);add(im,4200)
im,d=frame(2);line(d,78,'Convert the 3 marked → Jev?')
for y,t in [(139,'1. Yes, on a new branch (recommended)'),(181,'2. Yes, in a separate copy'),(223,'3. No, just save this report'),(265,'4. Let me pick the calls')]:line(d,y,t,GREEN if y==139 else FG)
line(d,348,'> approve',GREEN);add(im,2200)
im,d=frame(3);line(d,74,'✓ New branch: jevify/2026-09-23',GREEN)
line(d,116,'jev_decisions.py · illustrative diff excerpt',MUTED)
code=['+ MODEL = "jev-1.13.0"','+ THRESHOLD = 0.95  # provisional','+ question = {"type": "choice", "criteria": LABELS}','+ …','+ if confidence_gate(confidence):','+     accepted = label','  …','  return original(ticket)  # original LLM fallback']
for i,t in enumerate(code):d.text((30,165+i*31),t,font=small,fill=GREEN if t.startswith('+') else FG)
add(im,3100)
im,d=frame(3)
for y,t,c in [(74,'✓ 3 converted · 2 kept · 1 skipped',GREEN),(119,'✓ Your tests pass',GREEN),(164,'✓ Original LLM fallback retained',GREEN),(224,'Branch:     jevify/2026-09-23',FG),(261,'Review:     jev_decisions.py',FG),(298,'Report:     JEVIFY_REPORT.md',FG),(352,'Add TYPESAFE_API_KEY for live comparison.',MUTED),(390,'Undo: switch to main, delete the new branch.',MUTED)]:line(d,y,t,c)
add(im,3600)
OUT.parent.mkdir(exist_ok=True,parents=True)
frames[0].save(OUT,save_all=True,append_images=frames[1:],duration=durations,loop=0,optimize=True)
frames[-1].save(ROOT/'docs/demos/jevify-flow-poster.png')
shutil.copy2(OUT,ROOT/'site/public/media/jevify-flow.gif')
shutil.copy2(ROOT/'docs/demos/jevify-flow-poster.png',ROOT/'site/public/media/jevify-flow-poster.png')
print({'milliseconds':sum(durations),'bytes':OUT.stat().st_size})
