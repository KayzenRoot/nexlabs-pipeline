import csv,hashlib,json,collections,pathlib
P=pathlib.Path(__file__).resolve().parent; root=P.parent
paths={'agent_catalog':root/'NexLabs_AI_Enterprise_Agent_Catalog.json','skill_registry':root/'NexLabs_Skills_Registry/registry.json','agent_bindings':root/'NexLabs_Skills_Registry/agent-bindings.json','assignment_matrix':root/'NexLabs_Skills_Registry/assignment-matrix.csv'}
A={a['id']:a for a in json.loads(paths['agent_catalog'].read_text())['agents']}; R=json.loads(paths['skill_registry'].read_text()); B=json.loads(paths['agent_bindings'].read_text()); pk={p['id'] for p in R['packages']}
mode={'I':'INTERNAL_ONLY','P':'POLICY_GATED_EXTERNAL','H':'HUMAN_APPROVAL_REQUIRED'}
links={'SAL-01':['SAL-02'],'SAL-02':['SAL-04'],'SAL-03':['SAL-04'],'SAL-04':['SAL-05'],'SAL-05':['SAL-07'],'SAL-07':['ENG-01','OPS-01'],'ENG-01':['ENG-02'],'ENG-02':['ENG-03','ENG-04','ENG-05','ENG-06','ENG-07','ENG-08','ENG-09'],'ENG-07':['ENG-08','ENG-09'],'ENG-03':['ENG-10'],'ENG-04':['ENG-10'],'ENG-05':['ENG-10'],'ENG-06':['ENG-10'],'ENG-08':['ENG-10'],'ENG-09':['ENG-10'],'ENG-10':['ENG-11'],'ENG-11':['ENG-12'],'ENG-12':['OPS-01'],'DIG-01':['DIG-02'],'DIG-02':['DIG-03'],'DIG-03':['DIG-04'],'DIG-04':['DIG-05','MKT-01'],'MKT-01':['MKT-02','MKT-09','MKT-10','MKT-11','MKT-12','MKT-13'],'MKT-02':['MKT-03','MKT-04','MKT-05','MKT-06','MKT-07','MKT-08'],'DIG-05':['FIN-01'],'QNT-01':['QNT-03'],'QNT-02':['QNT-03'],'QNT-03':['QNT-04'],'QNT-04':['QNT-05'],'RES-01':['RES-03'],'RES-02':['RES-03'],'RES-03':['ENG-01','DIG-01']}
wf=[]; rows=[]
for line in (P/'spec.txt').read_text().splitlines():
 i,name,owner,trigger,inputs,steps,review,gate,risk,output,kpi,test=line.split('|'); oid='NLE-'+owner; rid='NLE-'+review; steps=[x.split(':',1) for x in steps.split(';')]; seq=[]
 for j,(agent,task) in enumerate(steps,1):
  aid='NLE-'+agent; a=A[aid]; seq.append({'step':j,'agent_id':aid,'task':task,'autonomy_ceiling':a['autonomy'],'eligible_packages':B[aid]['packages'],'scope':'analysis_only' if a['autonomy']=='A1' else 'internal_draft_or_authorized_internal_action','external_effects':'DENY'})
 roles=[(oid,'accountable'),(rid,'reviewer')]+[(s['agent_id'],f"step-{s['step']}") for s in seq]; packages=sorted({p for aid,_ in roles for p in B[aid]['packages']});
 item={'id':'NLE-WF-'+i,'name':name,'accountable':oid,'dispatch_agent':'NLE-ATHENA-PMO' if A[oid]['autonomy'] in ('A1','A2') else oid,'trigger_proposed':trigger,'inputs':inputs,'steps':seq,'reviewer':rid,'reviewer_packages':B[rid]['packages'],'gate':mode[gate],'risk':risk,'output':output,'kpi_proposed':kpi,'scenario_specific_not_run':test,'next_candidates':['NLE-WF-'+x for x in links.get(i,[])],'eligible_packages_union':packages,'activation':'DISABLED','qualification':'NOT_RUN','new_spend_limit_usd':0,'effect_policy':'DENY_DEFAULT','common_tests':['DUPLICATE_EVENT','STALE_LOCK','REVOKED_GRANT','REVIEWER_SEPARATION','TIMEOUT_RECONCILE','COST_CAP'],'failure':'BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.'}; wf.append(item)
 for aid,role in roles:
  for pack in B[aid]['packages']:rows.append([item['id'],aid,role,pack,'ELIGIBLE_NOT_RUNTIME_VERIFIED'])
ids={w['id'] for w in wf}; assert len(ids)==len(wf)
assert all(x in ids for w in wf for x in w['next_candidates']); assert all(w['reviewer'] not in [s['agent_id'] for s in w['steps']]+[w['accountable']] for w in wf)
assert all(s['agent_id'] in A and set(s['eligible_packages'])<=pk for w in wf for s in w['steps']); assert {r[1] for r in rows}==set(A); assert {r[3] for r in rows}==pk
assert all(w['activation']=='DISABLED' and w['qualification']=='NOT_RUN' and w['new_spend_limit_usd']==0 and w['effect_policy']=='DENY_DEFAULT' for w in wf)
assert all(A[w['dispatch_agent']]['autonomy']=='A3' for w in wf)
assign=list(csv.DictReader(paths['assignment_matrix'].open(encoding='utf-8-sig'))); assert len(assign)==1110 and all(r['package_id'] in B[r['agent_id']]['packages'] for r in assign)
summary={'workflows':len(wf),'agents_covered':len({r[1] for r in rows}),'packages_eligible':len({r[3] for r in rows}),'original_assignments_preserved':len(assign),'agent_qualification_tests_preserved':sum(len(a['qualification_tests']) for a in A.values()),'specific_workflow_scenarios':len(wf),'common_test_instances_planned':6*len(wf),'counts_by_group':dict(collections.Counter(w['id'].split('-')[2] for w in wf)),'counts_by_gate':dict(collections.Counter(w['gate'] for w in wf)),'mapping_rows':len(rows),'activated':0,'operational_tests_run':0}
manifest={'schema':'nexlabs.workflow-plan.v1','status':'PROPOSED_NOT_EXECUTABLE','source_lock':{k:{'file':v.name,'sha256':hashlib.sha256(v.read_bytes()).hexdigest()} for k,v in paths.items()},'summary':summary,'workflows':wf}
(P/'workflows.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n'); (P/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
with (P/'agent-skill-workflow-matrix.csv').open('w',encoding='utf-8-sig',newline='') as f:
 wr=csv.writer(f);wr.writerow(['workflow_id','agent_id','role_in_workflow','eligible_skill_package','status']);wr.writerows(rows)
with (P/'assignment-trace.csv').open('w',encoding='utf-8-sig',newline='') as f:
 wr=csv.writer(f);wr.writerow(['assignment_id','agent_id','package_id','eligible_workflow_ids']); by=collections.defaultdict(set)
 for wid,aid,role,pack,status in rows:by[aid,pack].add(wid)
 for r in assign:
  key=(r['agent_id'],r['package_id']);assert by[key];wr.writerow([r['assignment_id'],*key,';'.join(sorted(by[key]))])
md=['# Catálogo de workflows NLE-WF-PLAN-001','Status: PROPOSED / não ativado. As skills listadas são elegíveis, não carregadas ou comprovadas. Todos os passos têm efeito externo negado por padrão. O dono é accountable, não recebe permissões adicionais. A aprovação humana não amplia a permissão do agente; ação externa passa por serviço autorizado e read-back.']
for w in wf:
 md += [f"## {w['id']} · {w['name']}",f"**Responsável:** {w['accountable']} | **Despacho:** {w['dispatch_agent']} | **Revisor:** {w['reviewer']} | **Risco:** {w['risk']} | **Gate:** {w['gate']}",f"**Gatilho:** {w['trigger_proposed']}  \n**Entradas:** {w['inputs']}",'### Etapas']
 for s in w['steps']:md.append(f"{s['step']}. **{s['agent_id']} ({s['autonomy_ceiling']})**: {s['task']}. Skills elegíveis: {', '.join(s['eligible_packages'])}.")
 md += [f"**Entrega:** {w['output']}  \n**KPIs:** {w['kpi_proposed']}  \n**Teste específico (NOT_RUN):** {w['scenario_specific_not_run']}  \n**Próximos candidatos condicionais:** {', '.join(w['next_candidates']) or 'encerrar/aguardar próximo evento'}",f"**Falhas:** {w['failure']}",'']
(P/'catalogo-workflows.md').write_text('\n\n'.join(md)+'\n')
(P/'VALIDATION.txt').write_text('PASS: hashes das quatro fontes calculados; IDs únicos; referências e links válidos; revisor separado do dono e executores; despachante A3; 105/105 agentes; 92/92 pacotes elegíveis; 1110/1110 atribuições rastreáveis; todos desativados e US$0 incremental por padrão.\nNÃO EXECUTADOS: workflows, integrações, testes operacionais ou benchmarks.\n'+json.dumps(summary,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(summary,ensure_ascii=False,indent=2))
