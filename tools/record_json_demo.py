#!/usr/bin/env python3
"""Record real Jev JSON completion and Claude SSE deltas. Key only from environment."""
import concurrent.futures, json, os, time, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'docs/demos/json-data'; OUT.mkdir(parents=True,exist_ok=True)
TICKETS=[
('ticket_01','I was charged twice for my subscription.'),
('ticket_02','The app crashes every time I upload a PDF.'),
('ticket_03','Can we get pricing for a team of 200?'),
('ticket_04','Please reset my account password.'),
('ticket_05','My refund has not arrived after ten days.'),
('ticket_06','Our webhook returns a 500 error.'),
('ticket_07','Do you offer an annual enterprise plan?'),
('ticket_08','I need to change the email on my account.'),
('ticket_09','Please send an invoice for last month.'),
('ticket_10','The search endpoint times out.'),
('ticket_11','Can someone demonstrate your product to our team?'),
('ticket_12','Please enable two-factor authentication for my login.')]
CRITERIA={'billing':'Payments, refunds, invoices and charges.','technical':'Software failures, outages, API errors.','sales':'Purchases, plans, pricing and demos.','account':'Login, credentials and account settings.'}
questions={k:{'type':'choice','instructions':f'Which department should handle {k}?','criteria':CRITERIA} for k,_ in TICKETS}
state=dict(TICKETS)
example={'answers':{k:{'type':'choice','choice':'one of billing, technical, sales, account','probabilities':dict.fromkeys(CRITERIA,0.25),'confidence':0.0} for k,_ in TICKETS}}
jev_request={'model':'typesafe/jev-1.13-20260917','state':state,'questions':questions}
claude_request={'model':'anthropic/claude-haiku-4.5','temperature':0,'max_tokens':6000,'stream':True,
 'messages':[{'role':'system','content':'Evaluate every supplied Choice question against the supplied state. Return only valid JSON, no markdown. Use the exact question IDs and answer structure given. Each probabilities map must include every allowed option, with values from 0 to 1 summing to 1. choice must be an allowed option with maximum probability. confidence is your self-estimated confidence from 0 to 1. Do not copy the placeholder choice or numeric example values unless appropriate. These are decisions, not prose.'},
 {'role':'user','content':json.dumps({'state':state,'questions':questions,'output_shape':example})}]}
(OUT/'requests.json').write_text(json.dumps({'provenance':'synthetic support-ticket batch; created for this demonstration','jev':jev_request,'claude':claude_request},indent=2)+'\n')
key=os.environ['OPENROUTER_API_KEY']
def request(path,payload):
 return urllib.request.Request('https://openrouter.ai/api/v1/'+path,data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
def jev():
 start=time.perf_counter()
 with urllib.request.urlopen(request('systemone',jev_request),timeout=120) as r: body=json.load(r)
 elapsed=time.perf_counter()-start
 (OUT/'jev-raw.json').write_text(json.dumps({'elapsed_s':elapsed,'raw_response':body},indent=2)+'\n')
 return {'elapsed_s':elapsed,'raw_response':body,'display':json.dumps({'answers':body['answers']},indent=2)}
def claude():
 start=time.perf_counter();events=[];chunks=[];usage=None;model=None;rid=None
 with urllib.request.urlopen(request('chat/completions',claude_request),timeout=120) as r:
  for line in r:
   if not line.startswith(b'data: '):continue
   payload=line[6:].strip()
   if payload==b'[DONE]':break
   obj=json.loads(payload)
   if 'error' in obj: raise RuntimeError('Provider returned a streaming error')
   rid=obj.get('id',rid); model=obj.get('model',model);usage=obj.get('usage') or usage
   for c in obj.get('choices',[]):
    delta=c.get('delta',{}).get('content') or ''
    if delta: events.append({'at_s':time.perf_counter()-start,'text':delta});chunks.append(delta)
 elapsed=time.perf_counter()-start
 text=''.join(chunks)
 (OUT/'claude-stream-raw.json').write_text(json.dumps({'events':events,'text':text,'elapsed_s':elapsed,'request_id':rid,'model':model},indent=2)+'\n')
 cleaned=text.strip()
 if cleaned.startswith('```'):
  cleaned='\n'.join(cleaned.splitlines()[1:-1])
 parsed=json.loads(cleaned)
 return {'elapsed_s':elapsed,'events':events,'raw_text':text,'parsed':parsed,'model':model,'request_id':rid,'usage':usage}
with concurrent.futures.ThreadPoolExecutor(2) as pool:
 a=pool.submit(jev);b=pool.submit(claude);j=a.result();c=b.result()
# Validate all output fields before making a demo.
for answers in (j['raw_response']['answers'],c['parsed']['answers']):
 assert set(answers)==set(state)
 for value in answers.values():
  assert value['type']=='choice' and value['choice'] in CRITERIA
  assert set(value['probabilities'])==set(CRITERIA)
  assert all(isinstance(v,(int,float)) and 0<=v<=1 for v in value['probabilities'].values())
  assert abs(sum(value['probabilities'].values())-1)<0.025
  assert 0<=value['confidence']<=1
assert j['raw_response']['model']==jev_request['model']
data={'recorded_at_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'provider':'OpenRouter','kind':'one fresh paired API run; synthetic inputs','jev':j,'claude':c,
 'agreement':sum(j['raw_response']['answers'][k]['choice']==c['parsed']['answers'][k]['choice'] for k in state), 'questions':len(state)}
(OUT/'capture.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps({'jev_seconds':j['elapsed_s'],'claude_seconds':c['elapsed_s'],'matching_choices':data['agreement'],'questions':len(state),'claude_stream_events':len(c['events'])}))
