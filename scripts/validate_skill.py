#!/usr/bin/env python3
"""Validate skill files and schemas without executing their instruction content."""
import argparse
import ast
import json
from pathlib import Path
import re


def validate(root,strict_directory_name=False):
    root=Path(root);errors=[];invalid=object()
    def read(relative):
        try:return (root/relative).read_text(encoding='utf-8-sig')
        except (OSError,UnicodeError) as error:
            errors.append(relative+': unreadable UTF-8 file ('+type(error).__name__+')')
            return None
    def data(relative):
        text=read(relative)
        if text is None:return invalid
        try:return json.loads(text)
        except ValueError:errors.append(relative+': invalid JSON');return invalid
    text=read('SKILL.md')
    if text is not None:
        match=re.match(r'\A---\n(.*?)\n---\n',text,re.S)
        if match is None:errors.append('SKILL.md: missing frontmatter')
        else:
            header=match.group(1)
            name=re.search(r'^name:[ \t]*([a-z][a-z0-9-]{0,63})[ \t]*$',header,re.M)
            description=re.search(r'^description:[ \t]*([^\r\n]+)$',header,re.M)
            if name is None or name.group(1)!='god-prompt':errors.append('SKILL.md: expected skill name god-prompt')
            elif strict_directory_name and name.group(1)!=root.name:errors.append('SKILL.md: installed directory name must match god-prompt')
            if description is None or not description.group(1).strip().strip('"\'').strip() or len(description.group(1).strip())>1024:
                errors.append('SKILL.md: nonempty description of at most 1024 characters required')
    for relative in ('engine/god_prompt.apl','engine/specialization_contracts.apl',
                     'references/architecture.md','references/connectors.md','references/quality.md',
                     'references/page-equivalence.md','agents/openai.yaml','scripts/god_prompt.py',
                     'scripts/install_skill.py','scripts/package_integrity.py','tests/test_god_prompt.py'):
        if not (root/relative).is_file():errors.append('missing '+relative)
    catalog=data('references/catalog.json')
    if catalog is not invalid:
        if not isinstance(catalog,dict):errors.append('catalog: JSON object required')
        else:
            for field,keys,minimum in [('prompt_patterns',('id','title','rule'),25),
                ('skill_candidates',('id','name','repo','path','url'),25),
                ('primary_references',('name','url','kind'),1)]:
                items=catalog.get(field)
                if not isinstance(items,list) or len(items)<minimum:
                    errors.append('catalog: '+field+' must be a list with at least '+str(minimum)+' entries');continue
                ids=set()
                for index,item in enumerate(items):
                    if not isinstance(item,dict) or any(not isinstance(item.get(key),str) or not item[key].strip() for key in keys):
                        errors.append('catalog: invalid '+field+' entry '+str(index));continue
                    if 'id' in keys:
                        if item['id'] in ids:errors.append('catalog: duplicate id '+item['id'])
                        ids.add(item['id'])
                    if field=='skill_candidates':
                        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',item['repo']):errors.append('catalog: invalid repository identity')
                        if item['path'].startswith('/') or '..' in item['path'].split('/') or any(c in item['path'] for c in ':?\\#'):
                            errors.append('catalog: invalid skill path')
                        if not item['url'].startswith('https://github.com/'):errors.append('catalog: expected public GitHub reference URL')
    for relative in ('examples/request.json','examples/request_small.json','examples/request_quickstart.json'):
        request=data(relative)
        if request is invalid:continue
        if not isinstance(request,dict):errors.append(relative+': JSON object required');continue
        if not isinstance(request.get('goal'),str) or not request['goal'].strip():errors.append(relative+': nonempty goal required')
        for field,low,high in [('target_pages',1,None),('words_per_page',100,3000),('pages_per_txt',1,100000)]:
            value=request.get(field)
            if type(value) is not int or value<low or (high is not None and value>high):errors.append(relative+': invalid '+field)
        for field in ('constraints','cloud_urls','github_repos'):
            if not isinstance(request.get(field,[]),list) or any(not isinstance(x,str) or not x.strip() for x in request.get(field,[])):
                errors.append(relative+': '+field+' must be a list of strings')
        if relative=='examples/request.json' and tuple(request.get(k) for k in ('target_pages','words_per_page','pages_per_txt'))!=(10000,500,100):
            errors.append(relative+': default size must be 10000/500/100')
    for directory in ('scripts','tests'):
        for source in sorted((root/directory).glob('*.py')):
            content=read(source.relative_to(root).as_posix())
            if content is not None:
                try:ast.parse(content,filename=source.name)
                except SyntaxError as error:errors.append(source.name+': syntax error at line '+str(error.lineno))
    interface=read('agents/openai.yaml')
    if interface is not None:
        if '$god-prompt' not in interface:errors.append('agents/openai.yaml: default prompt must mention $god-prompt')
        if not re.search(r'^interface:[ \t]*$',interface,re.M):errors.append('agents/openai.yaml: interface metadata missing')
    return errors


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--strict-directory-name',action='store_true')
    args=parser.parse_args()
    try:errors=validate(args.root,args.strict_directory_name)
    except (OSError,UnicodeError,ValueError) as error:errors=['Cannot inspect package: '+str(error)]
    if errors:
        print('SKILL INVALID:',*errors,sep='\n - ')
        return 1
    print('SKILL OK: god-prompt; instructions, schemas, examples and Python syntax validated')
    return 0


if __name__=='__main__':raise SystemExit(main())
