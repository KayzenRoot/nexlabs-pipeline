"""Offline positive and tamper-detection tests; no operational capability claims."""
import json, shutil, tempfile, unittest
from pathlib import Path
from scripts.validate_sources import ROOT, validate, ValidationError

class SourceTests(unittest.TestCase):
    def test_valid_snapshot(self):
        self.assertTrue(validate(verbose=False))
    def with_copy(self, mutation, expected):
        with tempfile.TemporaryDirectory() as td:
            d=Path(td)/'pack'
            shutil.copytree(ROOT,d,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
            mutation(d)
            with self.assertRaisesRegex(ValidationError,expected): validate(d,verbose=False)
    def test_tampered_catalog(self):
        def mutate(d):
            p=d/'sources/NexLabs_AI_Enterprise_Agent_Catalog.json'; p.write_bytes(p.read_bytes()+b' ')
        self.with_copy(mutate,'fingerprint mismatch')
    def test_missing_source(self):
        self.with_copy(lambda d:(d/'sources/NexLabs_Workflows_Plan.zip').unlink(),'source inventory drift')
    def test_added_source(self):
        self.with_copy(lambda d:(d/'sources/unknown.md').write_text('new'),'source inventory drift')
    def test_duplicate_work_order(self):
        def mutate(d):
            p=d/'docs/backlog.json'; data=json.loads(p.read_text()); data[-1]['id']=data[0]['id'];p.write_text(json.dumps(data))
        self.with_copy(mutate,'backlog coverage')
    def test_bypassed_predecessor(self):
        def mutate(d):
            p=d/'docs/backlog.json';data=json.loads(p.read_text());data[2]['previous_gate']='NLE-BOOTSTRAP-001';p.write_text(json.dumps(data))
        self.with_copy(mutate,'backlog sequence')
    def test_unapproved_activation(self):
        def mutate(d):
            p=d/'docs/backlog.json';data=json.loads(p.read_text());data[0]['status']='RUNNING';p.write_text(json.dumps(data))
        self.with_copy(mutate,'backlog sequence')
if __name__=='__main__': unittest.main()
