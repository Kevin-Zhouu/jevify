#!/usr/bin/env python3
"""Draw an editorial three-panel diagram from the committed real session.
Not a screenshot, simulated terminal, or invented agent output.
"""
from pathlib import Path
from html import escape
import shutil

root=Path(__file__).resolve().parents[1]
base=root/'docs/demos/jevify-session/output'
workflow=(base/'workflow.py').read_text()
policy=(base/'jev_decisions.py').read_text()
# Each code fragment is a literal excerpt. Ellipses denote omitted code.
before=['response = client.messages.create(', '    …', ')', 'result = response.content[0].text', 'return result.strip()']
after=['MODEL = "jev-1.13.0"', 'THRESHOLD = 0.95', '"type": "choice"', '…', 'if confidence_gate(confidence):', '    accepted = label', '…', 'return original(ticket)']
for line in before:
 if line.strip() not in ('…', ')'): assert line.strip() in workflow
for line in after:
 if line.strip()!='…': assert line.strip() in policy
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="400" viewBox="0 0 1200 400" role="img" aria-labelledby="title desc">',
'<title id="title">Your code → Jevify’s plan → converted code</title>',
'<desc id="desc">A diagram based on the real recorded Codex run. One support classifier gets a Jev Choice question, a provisional confidence gate, and its original LLM fallback. Offline checks passed; live validation was skipped.</desc>',
'<rect width="1200" height="400" rx="12" fill="#101214"/>',
'<style>text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace} .label{font-size:13px;fill:#b1b9bd;letter-spacing:1px}.heading{font-family:system-ui,sans-serif;font-size:23px;font-weight:600;fill:#f1f5f4}.code{font-size:15px;fill:#d5dcdc}.small{font-size:12px;fill:#a5aeb1}.accent{fill:#c5fc77}</style>']
def text(x,y,v,cls='code'):
 s.append(f'<text x="{x}" y="{y}" class="{cls}" xml:space="preserve">{escape(v)}</text>')
for x,n,h in [(26,'01  YOUR CODE','A label from an LLM'),(422,'02  REVIEW THE PLAN','One decision call'),(818,'03  APPROVE → CONVERT','Jev + your fallback')]:
 text(x,34,n,'label');text(x,70,h,'heading')
for x in [396,792]:s.append(f'<path d="M{x} 24V330" stroke="#30383b"/>')
text(26,110,'workflow.py','small')
for i,line in enumerate(before):text(26,148+i*27,line)
text(26,304,'Existing prompt + category parser','small')
text(422,110,'workflow.py:83 · Anthropic','small')
s.append('<rect x="422" y="131" width="330" height="43" rx="5" fill="#203022"/>')
text(438,158,'DECISION  →  Jev Choice','code accent')
for y,v in [(209,'10 existing category labels'),(240,'Keep the original LLM fallback'),(271,'Wait for your approval')]:text(422,y,v)
text(422,304,'Plan summary · not a UI screenshot','small')
for i,line in enumerate(after):text(818,112+i*24,line,'code accent' if i in (2,4,7) else 'code')
s.append('<path d="M26 334H1174" stroke="#30383b"/>')
text(26,363,'1 classifier converted · offline checks passed · branch jev-convert/demo','small')
text(26,384,'Actual recorded run. Code excerpts; … marks omissions. Live validation skipped; Jev disabled until configured.','small')
s.append('</svg>')
out=root/'docs/demos/jevify-story.svg';out.write_text('\n'.join(s)+'\n')
shutil.copy2(out,root/'site/public/media/jevify-story.svg')
