#!/usr/bin/env python3
import json,sys,pathlib,subprocess,hashlib
PREFERRED=['/generate','/chat','/predict','/respond','/infer','/run']
def run(cmd,timeout=240): return subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)
def payload_for(spec,prompt):
 p={}; set_prompt=False
 for x in spec.get('parameters',[]):
  n=x.get('name',''); l=n.lower(); req=bool(x.get('required',False)); default=x.get('default'); typ=(x.get('type') or {}).get('type')
  if l in {'message','prompt','text','query','input','instruction','user_message'}: p[n]=prompt; set_prompt=True
  elif l in {'chat_history','history','messages'}: p[n]=[]
  elif l in {'max_new_tokens','max_tokens','maximum_new_tokens'}: p[n]=900
  elif l=='temperature': p[n]=0.1
  elif l=='top_p': p[n]=0.9
  elif l=='top_k': p[n]=40
  elif l in {'system','system_prompt'}: p[n]='Defensive authorized cybersecurity only. CLAIM<=EVIDENCE. Never invent executions.'
  elif req and default is None:
   if typ=='string' and not set_prompt: p[n]=prompt; set_prompt=True
   else: return None
 return p if set_prompt else None
def extract(raw):
 raw=raw.strip()
 try:
  o=json.loads(raw)
  if isinstance(o,dict):
   for k in ('Response','response','text','output','message'):
    if isinstance(o.get(k),str): return o[k].strip()
 except: pass
 return raw
def invoke(space,prompt):
 info=run(['hf-gradio','info',space],120)
 if info.returncode!=0: return False,'',{'stage':'info','error':(info.stderr or info.stdout)[-1200:]}
 try: api=json.loads(info.stdout)
 except Exception as e: return False,'',{'stage':'decode','error':repr(e)}
 eps=list(api.items()); eps.sort(key=lambda kv:(PREFERRED.index(kv[0]) if kv[0] in PREFERRED else 99,kv[0])); errs=[]
 for ep,spec in eps:
  payload=payload_for(spec,prompt)
  if payload is None: continue
  pred=run(['hf-gradio','predict',space,ep,json.dumps(payload,ensure_ascii=False)],240)
  if pred.returncode==0 and (pred.stdout or '').strip():
   text=extract(pred.stdout)
   if text: return True,text,{'endpoint':ep,'sha256':hashlib.sha256(text.encode()).hexdigest()}
  errs.append((pred.stderr or pred.stdout)[-700:])
 return False,'',{'stage':'predict','error':' | '.join(errs[-3:]) or 'No compatible endpoint'}
role=sys.argv[1]; model=sys.argv[2]; focus=sys.argv[3]
prompt=f'''ROLE: {role}\nMISSION: CEREBRON Farm 19 Cybersecurity. Work only on defensive, authorized cybersecurity. Do not provide malware deployment, credential theft, persistence, evasion, destructive exploitation, or unauthorized access instructions. Focus: {focus}. Return concise defensive findings with observations, risks, mitigations, evidence_needed, assumptions, unknowns, verification_steps. CLAIM <= EVIDENCE.'''
ok,text,meta=invoke(model,prompt)
obj={'role':role,'model':model,'focus':focus,'epistemic_status':'UNREVIEWED_EXTERNAL_AGENT_OUTPUT' if ok else 'EXTERNAL_INFERENCE_FAILED','status':'UNREVIEWED_EXTERNAL_AGENT_OUTPUT' if ok else 'EXTERNAL_INFERENCE_FAILED','inference_success':bool(ok),'error':None if ok else meta.get('error'),'result':text if ok else None,'meta':meta}
pathlib.Path('out').mkdir(exist_ok=True); pathlib.Path(f'out/{role}.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)); print(json.dumps({'role':role,'inference_success':bool(ok),'model':model}))