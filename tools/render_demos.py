#!/usr/bin/env python3
"""Render disclosed data replays, not new API calls or screen recordings.
Requires Pillow and imageio-ffmpeg in a separate rendering environment.
"""
import hashlib
import json
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/demos'
SOURCE = ROOT / 'eval/results/dev-03/anthropic_classification-codex-headless/original/JEV_PARITY.json'
rows = json.loads(SOURCE.read_text())['sites'][0]['rows']
# First accepted fixture, then first rejected fixture whose raw answers differ.
selected = [next(r for r in rows if not r['fallback_taken']),
            next(r for r in rows if r['fallback_taken'] and r['jev_answer'] != r['original_answer'])]
W, H, FPS, SECONDS = 1280, 720, 24, 18
BG, INK, MUTED, GREEN, ORANGE = '#f4f3ed', '#17211f', '#65706b', '#c3ee73', '#f6ca91'
FONT_DIR = Path('/System/Library/Fonts/Supplemental')
# Supply equivalent fonts with these filenames in FONT_DIR on other platforms.
import os
FONT_DIR = Path(os.environ.get('JEVIFY_DEMO_FONTS', FONT_DIR))
def font(size, bold=False):
    return ImageFont.truetype(str(FONT_DIR / ('Arial Bold.ttf' if bold else 'Arial.ttf')), size)

def wrap(draw, text, f, width):
    lines, line = [], ''
    for word in text.split():
        trial = (line + ' ' + word).strip()
        if draw.textlength(trial, font=f) > width and line:
            lines.append(line); line = word
        else: line = trial
    return lines + [line]

def frame(row, index, t):
    im = Image.new('RGB', (W,H), BG); d=ImageDraw.Draw(im)
    def txt(x,y,s,size=22,color=INK,bold=False): d.text((x,y),s,font=font(size,bold),fill=color)
    def box(x,y,x2,y2,fill,outline=None): d.rounded_rectangle((x,y,x2,y2),radius=18,fill=fill,outline=outline,width=1)
    txt(42,25,'jevify',30,bold=True)
    box(890,24,1238,61,INK); txt(908,33,'RECORDED API DATA  /  REPLAY',16,'#ffffff',True)
    txt(42,80, '01  /  Let Jev take the easy decision' if index==0 else '02  /  Keep Claude for uncertain decisions',35,bold=True)
    txt(42,130,'Same ticket. Same category contract. A confidence gate decides who answers.',21,MUTED)
    box(42,170,1238,276,'#ffffff')
    txt(62,185,'INCOMING INSURANCE TICKET',14,MUTED,True)
    for j,line in enumerate(wrap(d,row['input'],font(22),1150)): txt(62,213+j*27,line,22)
    # Decision timing runs at 1x after the reading interval. End-to-end cascade is estimated.
    elapsed=max(0,t-4)*1000
    old=row['original_latency_ms']; jev=row['latency_ms']; fallback=row['fallback_taken']
    total=jev+(old if fallback else 0)
    for side,x in enumerate((42,653)):
        box(x,298,x+585,558,'#ffffff')
        txt(x+24,318,'CLAUDE' if side==0 else 'JEV + CLAUDE FALLBACK',15,MUTED,True)
        txt(x+24,346,'Haiku 4.5' if side==0 else 'Jev 1.13',29,bold=True)
        duration=old if side==0 else total
        done=elapsed>=duration
        if t<4:
            status='Ready to classify'; answer='Waiting for the same input'
        elif done:
            status='Claude answered' if side==0 or fallback else 'Jev answered'
            answer=row['original_answer'] if side==0 or fallback else row['jev_answer']
        elif side==1 and fallback and elapsed>=jev:
            status=f"Confidence {row['confidence']:.2f} < 0.90: calling Claude"
            answer='Fallback in progress'
        else:
            status='Decision in progress'; answer='Classifying ticket...'
        txt(x+24,393,status,19,MUTED)
        txt(x+24,424,answer,26,bold=True)
        if side==1 and elapsed>=jev:
            detail=(f"Raw Jev: {row['jev_answer']}  /  {row['confidence']:.2f}" if fallback else f"Confidence {row['confidence']:.2f} meets the 0.90 gate")
            txt(x+24,466,detail,17,MUTED)
        cost=row['original_cost_usd'] if side==0 else row['cost_usd']+(row['original_cost_usd'] if fallback else 0)
        metric=f"{duration:,.0f} ms" if done else f"{min(elapsed,duration):,.0f} ms"
        txt(x+24,504,metric,25,bold=True)
        if done: txt(x+205,510,f"${cost:.6f}"+(' est. cascade' if side==1 and fallback else ' API cost'),18,MUTED)
        width=int(535*min(elapsed/duration,1))
        d.rounded_rectangle((x+24,548,x+559,553),radius=2,fill='#e8ebe4')
        if width: d.rounded_rectangle((x+24,548,x+24+width,553),radius=2,fill=INK)
    complete=elapsed>=max(old,total)
    box(42,579,1238,641,GREEN if not fallback else ORANGE)
    if not complete:
        message='Read the ticket. Both paths start at 00:04; request timings replay at 1x.'
    elif not fallback:
        message=f"Same category. {old/jev:.1f}x faster on this ticket. {100*(1-row['cost_usd']/row['original_cost_usd']):.1f}% lower API cost."
    else:
        message=f"Uncertain Jev answer rejected. Claude keeps the final say. +{jev:.0f} ms estimated overhead."
    txt(62,598,message,22,bold=True)
    txt(42,656,'Measured separately via OpenRouter. Cascade sums are estimates, not a live end-to-end recording.',17,MUTED)
    txt(42,682,'Selected examples, not typical-case guarantees. Full set: 21/22 accepted matches; 14/36 fallbacks.',16,MUTED)
    txt(1155,682,f'{min(int(t),17):02d} / 18',16,MUTED)
    return im

OUT.mkdir(parents=True,exist_ok=True)
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
manifest={'kind':'visual replay of previously recorded live API measurements',
          'source':str(SOURCE.relative_to(ROOT)), 'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'new_api_calls':False, 'cascade_timing':'sum of separately measured Jev and original latency on fallback',
          'timing':'4-second reading interval, then measured milliseconds at 1x; results held for readability',
          'selection':'first accepted fixture, then first rejected fixture with differing raw answers', 'demos':[]}
for i,(name,row) in enumerate(zip(('01-confident-decision','02-confidence-fallback'),selected)):
    p=subprocess.Popen([ffmpeg,'-y','-loglevel','error','-f','rawvideo','-vcodec','rawvideo','-s',f'{W}x{H}','-pix_fmt','rgb24','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/f'{name}.mp4')],stdin=subprocess.PIPE)
    for n in range(FPS*SECONDS): p.stdin.write(frame(row,i,n/FPS).tobytes())
    p.stdin.close()
    if p.wait(): raise RuntimeError('ffmpeg failed')
    frame(row,i,12).save(OUT/f'{name}.png')
    manifest['demos'].append({'file':f'{name}.mp4','row':row})
    print(name,flush=True)
# One video containing both side-by-side comparisons, plus a lightweight README preview.
concat=OUT/'concat.txt'
concat.write_text("file '01-confident-decision.mp4'\nfile '02-confidence-fallback.mp4'\n")
subprocess.run([ffmpeg,'-y','-loglevel','error','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(OUT/'claude-vs-jev.mp4')],check=True)
concat.unlink()
subprocess.run([ffmpeg,'-y','-loglevel','error','-i',str(OUT/'claude-vs-jev.mp4'),'-filter_complex','fps=5,scale=800:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer','-loop','0',str(OUT/'preview.gif')],check=True)
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
