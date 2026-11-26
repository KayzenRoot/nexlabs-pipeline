import csv, json, hashlib, pathlib, sys, collections
p=pathlib.Path(__file__).parent
source=pathlib.Path(sys.argv[1]); raw=source.read_bytes(); a=json.loads(raw)['agents']
r=json.loads((p/'registry.json').read_text()); b=json.loads((p/'agent-bindings.json').read_text()); s=r['summary']
rows=list(csv.DictReader((p/'assignment-matrix.csv').open(encoding='utf-8-sig')))
assert hashlib.sha256(raw).hexdigest()==s['source_sha256']
assert len(a)==len(b)==105 and len(rows)==1110
assert len({x['assignment_id'] for x in rows})==1110
assert collections.Counter((x['agent_id'],x['original_competency']) for x in rows)==collections.Counter((x['id'],y) for x in a for y in x['skills'])
ps={x['id']:x for x in r['packages']}; cs={x['id']:x for x in r['competencies']}; ss={x['id'] for x in r['sources']}
assert len(ps)==92 and len(cs)==1071 and len(ss)==18
for x in rows:
 c=cs[x['competency_id']]; assert c['package']==x['package_id'] and x['original_competency'] in c['labels'] and x['agent_id'] in c['agents']; assert x['package_id'] in b[x['agent_id']]['packages']; assert x['domain_context'] in ps
for k,v in ps.items():
 rr=[x for x in rows if x['package_id']==k]; assert rr and v['assignments']==len(rr); assert set(v['agents'])=={x['agent_id'] for x in rr}; assert set(v['competency_ids'])=={x['competency_id'] for x in rr}; assert set(v['sources'])<=ss; assert not v['tool_grants'] and v['artifact_sha256'] is None; assert (p/'packages'/k/'SPEC.md').is_file()
for ag in a:
 v=b[ag['id']]; assert not v['enabled']; assert v['qualification_tests']==ag['qualification_tests']; assert v['autonomy_ceiling']==ag['autonomy']; assert set(v['packages'])=={x['package_id'] for x in rows if x['agent_id']==ag['id']}
assert sum(len(v['qualification_tests']) for v in b.values())==316
assert not list(p.rglob('SKILL.md'))
assert all(x['commit_sha'] is None for x in r['sources'])
print('PASS: source fingerprint, 105 agents, 1110 assignments, 92 packages, 1071 contextual records, 316 tests preserved, no active skills or grants.')
