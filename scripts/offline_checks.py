#!/usr/bin/env python3
"""Deterministic offline tests. Does not launch or control any application."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
from check_plan import check
import source_library as lib

SKILL = Path(__file__).resolve().parents[1]


def run():
    checks = []

    def verify(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    for p in SKILL.rglob('*.py'):
        compile(p.read_text(), str(p), 'exec')
    checks.append('Python syntax')
    for p in SKILL.rglob('*.rb'):
        subprocess.run(['ruby', '-c', str(p)], check=True, capture_output=True, text=True)
    checks.append('Ruby syntax (system interpreter)')
    for p in SKILL.rglob('*.md'):
        for link in re.findall(r'\]\(([^)]+)\)', p.read_text()):
            if '://' not in link and not link.startswith('#'):
                verify('local link: ' + link, (p.parent / link.split('#')[0]).is_file())
    plan = {'schema_version':1,'project_id':'test','revision':1,'units':'m','target_gfa_m2':100,
            'levels':[{'id':'L0','elevation_m':0,'gfa_m2':100,'allowance_m2':10}],
            'spaces':[{'id':'entry','level':'L0','area_m2':20,'entry':True},
                      {'id':'room','level':'L0','area_m2':70}],
            'connections':[{'from':'entry','to':'room','kind':'door'}]}
    verify('balanced plan and connected spaces', check(plan)['ok'])
    bad=copy.deepcopy(plan);bad['spaces'][1]['area_m2']=100
    verify('area overflow rejected', not check(bad)['ok'])
    bad=copy.deepcopy(plan);bad['connections']=[]
    verify('isolated occupied space rejected', not check(bad)['ok'])
    bad=copy.deepcopy(plan);bad['spaces'][1]['area_m2']=float('nan')
    verify('nonfinite area rejected', not check(bad)['ok'])
    bad=copy.deepcopy(plan);bad['spaces'][1]['id']='entry'
    verify('duplicate identity rejected', not check(bad)['ok'])
    external=copy.deepcopy(plan)
    external['spaces'].append({'id':'court','level':'L0','area_m2':50,'external':True})
    external['connections'].append({'from':'entry','to':'court','kind':'door'})
    verify('external area excluded from GFA', check(external)['ok'])
    audit={'schema_version':1,'kind':'sketchup_architect_audit','complete':True,'project_id':'test','revision':1,
           'quantities':{'gfa_m2_by_level':{'L0':100},'net_m2_by_space':{'entry':20,'room':70}}}
    verify('matching measured quantities pass', check(plan,audit)['ok'])
    bad=copy.deepcopy(audit);bad['quantities']['net_m2_by_space']={}
    verify('missing live measurements fail', not check(plan,bad)['ok'])
    bad=copy.deepcopy(audit);bad['revision']=0
    verify('old model audit rejected', not check(plan,bad)['ok'])
    bad=copy.deepcopy(audit);bad['complete']=False
    verify('truncated model audit rejected', not check(plan,bad)['ok'])
    vertical=copy.deepcopy(plan)
    vertical['levels'].append({'id':'L1','elevation_m':3,'gfa_m2':70,'allowance_m2':0})
    vertical['levels'][0]['gfa_m2']=30;vertical['spaces'][1]['level']='L1'
    verify('door cannot provide cross-level route', not check(vertical)['ok'])
    vertical['connections'][0]['kind']='stair'
    verify('explicit vertical route passes intent check', check(vertical)['ok'])

    with tempfile.TemporaryDirectory(prefix='architect-retrieval-') as temp:
        root=Path(temp)/'资料 library';root.mkdir()
        (root/'metadata').mkdir()
        (root/'metadata/SOURCE_MANIFEST.json').write_text(json.dumps({'generated_at':'offline-fixture','sources':[]}))
        current=root/'github/ruby-api-docs-gh-pages/Sketchup/Face.html'
        old=root/'github/ruby-api-docs/Sketchup/Face.html'
        for p,body in [(current,'<p>Face area current</p><script>hidden_secret</script>'),(old,'<p>Face area legacy</p>')]:
            p.parent.mkdir(parents=True,exist_ok=True);p.write_text(body)
        db=Path(temp)/'cache/index.sqlite'
        lib.build(root,db)
        result=lib.search(root,db,'Face area',None,10)['results']
        verify('default search excludes legacy HTML', len(result)==1 and result[0]['category']=='api')
        verify('HTML script text excluded', 'hidden_secret' not in lib.extract(current))
        verify('fresh hits verified by hash', not result[0]['stale'])
        current.write_text('<p>Face area updated</p>')
        verify('source changes marked stale', lib.search(root,db,'Face area',None,10)['results'][0]['stale'])
        lib.build(root,db)
        verify('rebuild refreshes content', not lib.search(root,db,'updated',None,10)['results'][0]['stale'])
        try:
            lib.source_path(root,'../../escape')
        except ValueError:
            checks.append('source path escape rejected')
        else:
            raise AssertionError('source path escape')
    result=subprocess.run(['ruby',str(SKILL/'scripts/session_contract_test.rb')],check=True,capture_output=True,text=True)
    contract=json.loads(result.stdout)
    verify('Ruby helper contract tests pass',contract['ok'])
    return {'ok':True,'mode':'offline_no_sketchup_no_computer_use','checks':checks,'ruby_contract':contract,
            'limitations':['No native geometry kernel, native Undo, GUI, save/reopen, exporters or visual fidelity tested.']}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    try:
        result=run()
    except (AssertionError,OSError,ValueError,subprocess.CalledProcessError) as exc:
        result={'ok':False,'error':str(exc),'detail':getattr(exc,'stderr',None)}
    encoded=json.dumps(result,indent=2,ensure_ascii=False)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(encoded)
    print(encoded,end='')
    return 0 if result['ok'] else 2


if __name__=='__main__':
    sys.exit(main())
