from pathlib import Path
from datetime import datetime,timezone
import json
D=Path(__file__).resolve().parent;rows=[]
for lane in sorted((D/'roles').glob('*/*')):
 if not lane.is_dir():continue
 status='PACKET_PREPARED'
 if (lane/'DISPATCH_REQUESTED.json').exists():status='DISPATCHED'
 if (lane/'DISPATCH.json').exists():status='WORKER_COMPLETED_WAITING_ARCHIVE'
 if (lane/'ARCHIVE_RECEIPT.json').exists():status='ROLE_ARCHIVED'
 rows.append({'candidate':lane.parent.name,'role':lane.name,'status':status,'prepared_receipt':(lane/'PREPARED_RECEIPT.json').exists()})
decisions=[]
if (D/'decisions').exists():
 for p in sorted((D/'decisions').glob('*.json')):
  x=json.loads(p.read_text());decisions.append({'candidate':x['candidate'],'decision':x['decision'],'path':str(p.relative_to(D))})
t=datetime.now(timezone.utc);p=D/('STATE_'+t.strftime('%Y%m%dT%H%M%S%fZ')+'.json')
with p.open('x') as f:json.dump({'status':'RUNNING','observed_at':t.isoformat(),'roles':rows,'coordinator_decisions':decisions,'boundary':'DISPATCH.json is only created after observed worker completion. Current live agent state must be checked with collaboration tools. Canonical receipt is required before dependent work.','stop_before':'comparative selection of ten'},f,ensure_ascii=False,indent=2);f.write('\n')
print(str(p))
