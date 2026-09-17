import json, os, sys
from pathlib import Path
from hf_gradio import GradioClient

role=sys.argv[1]; model=sys.argv[2]; focus=sys.argv[3]
mission='''CEREBRON Farm 19 Cybersecurity. Work only on defensive, authorized cybersecurity. Do not provide malware deployment, credential theft, persistence, evasion, destructive exploitation, or unauthorized access instructions. Distinguish established facts, inference, unknowns and hypotheses. Treat all output as UNREVIEWED_EXTERNAL_AGENT_OUTPUT until independently verified. Focus: '''+focus
prompt=f'''ROLE: {role}\nMISSION: {mission}\nReturn concise defensive findings with: observations, risks, mitigations, evidence_needed, assumptions, unknowns, verification_steps. CLAIM <= EVIDENCE.'''
Path('out').mkdir(exist_ok=True)
obj={'role':role,'model':model,'focus':focus,'epistemic_status':'UNREVIEWED_EXTERNAL_AGENT_OUTPUT','inference_success':False,'error':None,'result':None}
try:
    c=GradioClient(model)
    r=c.predict(message=prompt, max_new_tokens=900, temperature=0.2, api_name='/chat')
    obj['result']=r; obj['inference_success']=True
except Exception as e:
    obj['error']=repr(e)
Path(f'out/{role}.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2))
print(json.dumps(obj,ensure_ascii=False))
