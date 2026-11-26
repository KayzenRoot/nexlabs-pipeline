"""Deterministic source validation, no network or dependencies. No operational qualification."""
from pathlib import Path
from collections import Counter, defaultdict
import csv, hashlib, json, zipfile, sys

ROOT=Path(__file__).resolve().parents[1]
class ValidationError(ValueError): pass

def require(condition, message):
    if not condition: raise ValidationError(message)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))
def index(rows,key,label):
    result={r[key]:r for r in rows}; require(len(result)==len(rows),f'duplicate {label}'); return result
def validate(root=ROOT, verbose=True):
    s=root/'sources'; sr=s/'NexLabs_Skills_Registry'; wf=s/'NexLabs_Workflows'; it=s/'NexLabs_Intelligence_Plan'; inf=s/'NexLabs_Infrastructure_Plan'; cc=s/'NexLabs_Command_Center_Plan'
    def say(t):
        if verbose: print('PASS:',t)
    lock=load(root/'locks/source-lock.json')['files']; actual={p.relative_to(root).as_posix() for p in s.rglob('*') if p.is_file()}; require(actual==set(lock),'source inventory drift')
    for p,h in lock.items(): require(digest(root/p)==h,f'fingerprint mismatch {p}')
    archives=sorted(s.glob('*.zip')); require(len(archives)==6,'six archives expected')
    for a in archives:
        with zipfile.ZipFile(a) as z:
            require(z.testzip() is None,f'bad ZIP {a.name}')
            dest=s/'agent-pack' if 'Agent_Pack' in a.name else s
            for n in z.namelist():
                if not n.endswith('/'):
                    q=dest/n; require(q.resolve().is_relative_to(dest.resolve()),'archive traversal'); require(q.read_bytes()==z.read(n),f'extracted bytes mismatch {n}')
    require((s/'agent-pack/manifest.json').read_bytes()==(s/'NexLabs_AI_Enterprise_Agent_Catalog.json').read_bytes(),'agent manifest mismatch')
    say(f'6 ZIPs and {len(lock)} locked source files, extracted bytes preserved')
    for d in [it,inf,cc]:
        l=load(d/'source-lock.json'); pairs=l.get('files') or [{'path':k,'sha256':v} for k,v in l.items()]
        for i in pairs: require(digest(s/i['path'])==i['sha256'],f'prior lock mismatch {i["path"]}')
    Wdoc=load(wf/'workflows.json'); l=Wdoc['source_lock']
    for k,v in l.items():
        q=s/v['file'] if k=='agent_catalog' else sr/v['file']; require(digest(q)==v['sha256'],f'workflow lock {k}')
    say('all embedded cross-plan source locks match')
    a=load(s/'NexLabs_AI_Enterprise_Agent_Catalog.json')['agents']; A=index(a,'id','agent'); r=load(sr/'registry.json'); P=index(r['packages'],'id','package'); C=index(r['competencies'],'id','competency'); S=index(r['sources'],'id','source'); B=load(sr/'agent-bindings.json'); rows=read_csv(sr/'assignment-matrix.csv'); R=index(rows,'assignment_id','assignment'); W=index(Wdoc['workflows'],'id','workflow'); U=index(load(cc/'screens.json'),'id','screen')
    require((len(A),len(P),len(R),len(W),len(U),len(C))==(105,92,1110,62,35,1071),'catalog count mismatch')
    require(len(S)==18 and 'OWN' in S,'candidate source count')
    require(Counter(x['type'] for x in P.values())=={'domain':80,'shared':12},'package type distribution')
    require(Counter((x['agent_id'],x['original_competency']) for x in rows)==Counter((x['id'],y) for x in a for y in x['skills']),'assignment content mismatch')
    require(set(B)==set(A),'agent binding coverage')
    Arows=defaultdict(list); Prows=defaultdict(list)
    for x in rows:
        aid,pid,cid=x['agent_id'],x['package_id'],x['competency_id']; require(aid in A and pid in P and cid in C,'dangling assignment'); c=C[cid]; require(c['package']==pid and x['original_competency'] in c['labels'] and aid in c['agents'],'competency mismatch'); require(x['domain_context'] in P,'unknown context'); Arows[aid].append(x); Prows[pid].append(x)
    for aid,ag in A.items():
        require(not ag['enabled'] and not ag['heartbeat_enabled'] and not ag['new_spend_authorized'] and ag['external_effects_default']=='DENY','unsafe agent baseline '+aid)
        require(ag['resolved_model_id'] is None,'unqualified resolved model')
        v=B[aid]; require(not v['enabled'] and v['qualification_tests']==ag['qualification_tests'] and v['autonomy_ceiling']==ag['autonomy'],'agent binding mismatch '+aid)
        require(set(v['packages'])=={x['package_id'] for x in Arows[aid]},'package binding mismatch '+aid)
        require(load(s/'agent-pack/agents'/aid/'spec.json')==ag,'individual spec mismatch '+aid)
        seen={aid}; parent=ag['reports_to']
        while parent is not None:
            require(parent in A and parent not in seen,'hierarchy invalid/cycle '+aid); seen.add(parent); parent=A[parent]['reports_to']
        require('NLE-ZEUS-CEO' in seen,'missing CEO path')
    require(sum(len(x['qualification_tests']) for x in a)==316,'agent test count')
    for pid,pk in P.items():
        rr=Prows[pid]; require(rr and pk['assignments']==len(rr) and set(pk['agents'])=={x['agent_id'] for x in rr} and set(pk['competency_ids'])=={x['competency_id'] for x in rr},'package matrix '+pid)
        require(set(pk['sources'])<=set(S) and not pk['tool_grants'] and pk['artifact_sha256'] is None,'unsafe package '+pid)
        require((sr/'packages'/pid/'SPEC.md').is_file(),'missing SPEC '+pid)
    require(not list(sr.rglob('SKILL.md')),'unqualified executable skill')
    require(all(x['commit_sha'] is None for x in S.values()),'unqualified source pin drift')
    say('105 agents, 316 individual scenarios, 92 packages, 1110 assignments, 1071 contextual competencies, hierarchy and disabled baseline')
    m=read_csv(wf/'agent-skill-workflow-matrix.csv'); trace=index(read_csv(wf/'assignment-trace.csv'),'assignment_id','trace'); require(set(trace)==set(R),'assignment trace coverage')
    M=defaultdict(set); MA=defaultdict(set); MP=defaultdict(set)
    for x in m:
        wid,aid,pid=x['workflow_id'],x['agent_id'],x['eligible_skill_package']; require(wid in W and aid in A and pid in B[aid]['packages'],'workflow matrix dangling/unauthorized'); M[wid].add((aid,pid)); MA[wid].add(aid); MP[wid].add(pid)
    require(set().union(*MA.values())==set(A) and set().union(*MP.values())==set(P),'workflow coverage')
    for aid,t in trace.items():
        x=R[aid]; require(t['agent_id']==x['agent_id'] and t['package_id']==x['package_id'],'assignment trace mismatch'); wids=set(t['eligible_workflow_ids'].split(';')); require(wids and wids=={wid for wid,v in M.items() if (x['agent_id'],x['package_id']) in v},'trace workflow membership')
    dispatch_only={}
    for wid,w in W.items():
        actors={x['agent_id'] for x in w['steps']}|{w['accountable'],w['dispatch_agent']}; require(w['reviewer'] not in actors and w['reviewer'] in A,'reviewer overlap '+wid)
        require(({x['agent_id'] for x in w['steps']}|{w['accountable'],w['reviewer']})<=MA[wid]<=actors|{w['reviewer']} and set(w['eligible_packages_union'])==MP[wid],'workflow participants '+wid)
        if w['dispatch_agent'] not in MA[wid]: dispatch_only[wid]=w['dispatch_agent']
        require(w['activation']=='DISABLED' and w['qualification']=='NOT_RUN' and w['effect_policy']=='DENY_DEFAULT' and w['new_spend_limit_usd']==0,'unsafe workflow '+wid)
        require(set(w['next_candidates'])<=set(W),'workflow edge unknown')
        for step in w['steps']:
            require(set(step['eligible_packages'])<=set(B[step['agent_id']]['packages']),'step package mismatch')
            require(int(step['autonomy_ceiling'][1:])<=int(A[step['agent_id']]['autonomy'][1:]),'step privilege escalation')
    require(Counter(w['gate'] for w in W.values())=={'INTERNAL_ONLY':36,'POLICY_GATED_EXTERNAL':12,'HUMAN_APPROVAL_REQUIRED':14},'gate distribution')
    require(dispatch_only=={wid:'NLE-ATHENA-PMO' for wid in ['NLE-WF-GOV-03','NLE-WF-QNT-01','NLE-WF-QNT-02','NLE-WF-QNT-03','NLE-WF-QNT-05']},'dispatch-only discrepancy changed')
    say('5 dispatch-only discrepancies preserved; C12 requires correction before runtime')
    say(f'62 workflows, {len(m)} matrix rows, 1110 trace rows, reviewer segregation and gates')
    for d,filename,key,expected in [(it,'agent-memory-bindings.json','agent_id',A),(inf,'agent-runtime-bindings.json','agent_id',A),(it,'skill-learning-bindings.json','package_id',P),(inf,'skill-runtime-bindings.json','package_id',P),(it,'workflow-memory-bindings.json','workflow_id',W),(inf,'workflow-runtime-bindings.json','workflow_id',W),(cc,'workflow-screen-bindings.json','workflow_id',W)]:
        data=index(load(d/filename),key,filename); require(set(data)==set(expected),'binding coverage '+filename)
        for id,v in data.items():
            if key=='agent_id':
                require(set(v.get('packages',v.get('package_ids',[])))==set(B[id]['packages']),'agent bound packages '+id)
                require(set(v['assignment_ids'])=={x['assignment_id'] for x in Arows[id]},'agent bound assignments '+id)
                require(set(v['workflow_ids'])=={wid for wid,ag in MA.items() if id in ag},'agent bound workflows '+id)
                require(not v['cross_client_access'] and not v['critical_edit_allowed'],'unsafe memory/runtime grant')
                require(not v.get('enabled',False) and not v.get('heartbeat_enabled',False) and not v.get('promotion_authority_granted',False),'enabled grant')
            elif key=='package_id':
                require(set(v['agent_ids'])==set(P[id]['agents']) and set(v['assignment_ids'])=={x['assignment_id'] for x in Prows[id]},'skill binding membership')
                require(v['version_preserved']==P[id]['version'] and not v.get('auto_promote',False) and not v.get('auto_promotion',False),'skill promotion drift')
            else:
                require(set(v['agent_ids'])==MA[id]|{W[id]['dispatch_agent']} and set(v['package_ids'])==MP[id],'workflow binding drift '+filename+' '+id)
                require(v.get('gate',v.get('gate_preserved'))==W[id]['gate'] and v.get('risk',v.get('risk_preserved'))==W[id]['risk'],'workflow policy drift')
                require(v.get('activation',v.get('activation_preserved'))=='DISABLED','workflow enabled')
                if 'primary_screen' in v: require(v['primary_screen'] in U,'screen reference unknown')
    require(set(index(read_csv(cc/'agent-navigation.csv'),'agent_id','navigation'))==set(A),'UI agent coverage')
    require(Counter(v['mode'] for v in U.values())=={'NATIVE':2,'AUGMENT':6,'EXT':27},'screen modes')
    require(len(load(it/'benchmarks.json')['scenarios'])==48 and len(load(inf/'infra-qualification.json'))==32 and len(load(cc/'qualification.json'))==59,'platform scenario counts')
    policy=load(inf/'runtime-policy.json'); require(policy['limits']['additional_spend_usd']==0 and not policy['limits']['auto_paid_fallback'] and not policy['limits']['heartbeat_default'] and policy['limits']['llm_slots_global']==1,'runtime limits drift')
    require(sum(policy['ram_mib_caps'].values())==4608 and sum(policy['disk_gib_growth_caps'].values())==40,'resource budget drift')
    say('INT/INFRA/CC bindings and 35 screens, 48/32/59 planned scenarios, resource and cost caps')
    backlog=load(root/'docs/backlog.json'); expected={f'NLE-{family}-WO-{n:03d}' for family in ['INFRA','SR','WF','INT','CC'] for n in range(1,9)}; require(len(backlog)==40 and {x['id'] for x in backlog}==expected,'backlog coverage')
    prev='NLE-BOOTSTRAP-001'
    for x in backlog:
        require(x['previous_gate']==prev and x['status']=='NOT_STARTED','backlog sequence/activation'); prev=x['id']
    say('40 domain WOs, no missing/duplicate IDs, sequential gate')
    return True
if __name__=='__main__':
    try: validate()
    except (ValidationError,KeyError,FileNotFoundError,ValueError) as e:
        print('FAIL:',e,file=sys.stderr); sys.exit(1)
