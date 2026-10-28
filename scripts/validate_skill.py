#!/usr/bin/env python3
"""Small stdlib-only compatibility checks for the Agent Skills structure."""
from pathlib import Path
import argparse
import re, sys, json, ast
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--strict-directory-name',action='store_true',
                    help='Also require an installed skill directory to match its manifest name')
args=parser.parse_args()
err=[]
text=(root/'SKILL.md').read_text(encoding='utf-8')
if not text.startswith('---\n') or '\n---\n' not in text[4:]:err.append('missing YAML frontmatter')
else:
    header=text.split('---',2)[1]
    name=re.search(r'^name:\s*([a-z][a-z0-9-]*)\s*$',header,re.M)
    desc=re.search(r'^description:\s*(.+)$',header,re.M)
    if name is None:err.append('missing valid name')
    else:
        if args.strict_directory_name and name.group(1)!=root.name:err.append(f'name must match directory: {name.group(1)} != {root.name}')
        if len(name.group(1))>64:err.append('name too long')
    if desc is None or len(desc.group(1).strip())>1024:err.append('description required, <=1024 chars')
for rel in ('engine/god_prompt.apl','engine/specialization_contracts.apl',
            'references/catalog.json','references/page-equivalence.md',
            'agents/openai.yaml','scripts/god_prompt.py','tests/test_god_prompt.py'):
    if not (root/rel).is_file():err.append('missing '+rel)
try:
    c=json.loads((root/'references/catalog.json').read_text(encoding='utf-8'))
    if len(c['prompt_patterns'])<25 or len(c['skill_candidates'])<25:err.append('research catalog below 25/25')
except (ValueError,KeyError) as e:err.append('bad catalog '+str(e))
try:
    request=json.loads((root/'examples/request.json').read_text(encoding='utf-8'))
    if (request['target_pages'],request['words_per_page'],request['pages_per_txt'])!=(10000,500,100):err.append('example defaults mismatch')
except (ValueError,KeyError) as e:err.append('bad example request '+str(e))
try:
    ast.parse((root/'scripts/god_prompt.py').read_text(encoding='utf-8'))
except SyntaxError as e:err.append('python script invalid '+str(e))
if err:
    print('SKILL INVALID:',*err,sep='\n - ');sys.exit(1)
print('SKILL OK: god-prompt; catalog, files and examples validated')
