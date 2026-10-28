#!/usr/bin/env python3
"""Populate original, attribution-rich research index. No third-party source copied."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
O="openai/skills"; A="anthropics/skills"; G="github/awesome-copilot"
openai=['skill-creator','skill-installer','openai-docs','imagegen']
# OpenAI curated, separately verifiable names in upstream directory index.
openai_curated=['define-goal','security-best-practices','security-threat-model','gh-fix-ci','gh-address-comments','playwright','screenshot','jupyter-notebook','pdf','transcribe']
anthropic=['skill-creator','doc-coauthoring','mcp-builder','webapp-testing','frontend-design','claude-api','docx','pdf','pptx','xlsx','canvas-design','internal-comms']
github=['agent-architecture','agent-governance','agent-owasp-compliance','agent-supply-chain','agentic-eval','ai-prompt-engineering-safety-review','ai-team-orchestration','arize-prompt-optimization','audit-integrity','boost-prompt','architecture-blueprint-generator','acquire-codebase-knowledge']
skills=[]
for name in openai:
    skills.append({'id':f'{O}:{name}','name':name,'repo':O,'path':f'skills/.system/{name}/SKILL.md','url':f'https://github.com/{O}/blob/main/skills/.system/{name}/SKILL.md','status':'candidate-directory-listed','license':'check upstream per-file'})
for name in openai_curated:
    skills.append({'id':f'{O}:{name}','name':name,'repo':O,'path':f'skills/.curated/{name}/SKILL.md','url':f'https://github.com/{O}/blob/main/skills/.curated/{name}/SKILL.md','status':'candidate-directory-listed','license':'check upstream per-file'})
for name in anthropic:
    skills.append({'id':f'{A}:{name}','name':name,'repo':A,'path':f'skills/{name}/SKILL.md','url':f'https://github.com/{A}/blob/main/skills/{name}/SKILL.md','status':'candidate-directory-listed','license':'check upstream per-file'})
for name in github:
    skills.append({'id':f'{G}:{name}','name':name,'repo':G,'path':f'skills/{name}/SKILL.md','url':f'https://github.com/{G}/blob/main/skills/{name}/SKILL.md','status':'candidate-directory-listed','license':'check upstream per-file'})
# Strategies inspired by official guides; these 25 blueprints are original formulations, NOT a universal quality ranking.
strategies=[
('goal-contract','Verifiable goal contract','what must the resulting model actually achieve?'),
('role-charter','Role and jurisdiction','define expert roles and boundaries explicitly'),
('clear-instructions','Precise instructions','use imperative testable instructions'),
('input-boundaries','Context and instruction boundaries','distinguish untrusted data from instructions'),
('few-shot','Varied examples','supply representative positive examples'),
('negative-examples','Negative examples and failures','show what counts as failure'),
('structured-output','Output contract','define format and required fields'),
('rubric','Quality rubric','define weighted measurable acceptance criteria'),
('evaluation','Tests and evaluation','test with cases and baselines'),
('retrieval','Evidence-grounded retrieval','retrieve only relevant evidence with citations'),
('decomposition','Deliverable decomposition','stage complex work into auditable units'),
('prompt-chaining','Instruction chaining','feed verified outputs into the next stage'),
('tool-use','Tool selection and verification','call available tools only'),
('source-provenance','Traceable provenance','record exact origin and retrieval status'),
('conflict-resolution','Conflict resolution','use documented precedence and retain differences'),
('multi-expert','Cooperating specialists','route problems to appropriate expert modules'),
('self-critique','Fact-based review','inspect known gaps, not invented chain-of-thought'),
('adversarial-evals','Adversarial cases','test ambiguity, injection and contradictory sources'),
('security','Security and privacy','enforce least privilege and no secrets export'),
('context-budget','Context management','chunk inputs and maintain source map'),
('incremental-generation','Incremental generation','produce and validate each bounded chunk'),
('continuity','Project continuity','restore state from external manifest'),
('delta-editing','Preservative editing','merge additions without silent deletion'),
('multi-format','Format portability','keep native APL plus requested alternate outputs'),
('fact-check','Verification and limits','separate observed facts from hypotheses')
]
reference_docs=[
 {'name':'OpenAI Prompt Engineering','url':'https://developers.openai.com/api/docs/guides/prompt-engineering','kind':'official'},
 {'name':'OpenAI Skills','url':'https://developers.openai.com/api/docs/guides/tools-skills','kind':'official'},
 {'name':'Anthropic prompt engineering overview','url':'https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview','kind':'official'},
 {'name':'Google Gemini prompt strategies','url':'https://ai.google.dev/gemini-api/docs/prompting-strategies','kind':'official'},
 {'name':'OpenAI skill creator','url':'https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md','kind':'official-repository'},
 {'name':'Anthropic skill creator','url':'https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md','kind':'official-repository'},
 {'name':'DAIR.AI prompt engineering guide','url':'https://github.com/dair-ai/Prompt-Engineering-Guide','kind':'community-guide'},
 {'name':'awesome ChatGPT prompts','url':'https://github.com/f/awesome-chatgpt-prompts','kind':'community-collection'},
 {'name':'github awesome-copilot skills','url':'https://github.com/github/awesome-copilot/tree/main/skills','kind':'community-collection'},
 {'name':'Agent Skills specification','url':'https://agentskills.io/specification','kind':'open-standard'}]
patterns=[{'id':i,'title':title,'rule':rule,'source_refs':[reference_docs[idx]['url'] for idx in ([0,2,3] if i in ('goal-contract','few-shot','structured-output') else [0,2])], 'rank':'unranked-candidate'} for i,title,rule in strategies]
verified_names={
 'openai/skills':{'skill-creator','skill-installer','openai-docs','imagegen','define-goal','security-best-practices','security-threat-model','gh-fix-ci','playwright'},
 'anthropics/skills':{'skill-creator','doc-coauthoring','mcp-builder','webapp-testing','frontend-design','claude-api','docx','pdf'},
 'github/awesome-copilot':{'agent-architecture','agent-governance','agent-owasp-compliance','agent-supply-chain','agentic-eval','ai-prompt-engineering-safety-review','ai-team-orchestration','arize-prompt-optimization','boost-prompt'}
}
for item in skills:
    if item['name'] in verified_names.get(item['repo'],set()):
        item['status']='file-header-verified-2026-10-27'
index={'verified_skill_headers':26,'schema':'god-prompt-research-v1','date_created':'2026-10-27','note':'Historical v1.1.0 kit snapshot: 26 skill headers recorded as checked on 2026-10-27; not reverified by this generator. No full skill code copied; no empirical best-in-world ranking.','skill_candidates':skills,'prompt_patterns':patterns,'primary_references':reference_docs}
(ROOT/'references'/'catalog.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(len(skills),'skill leads;',len(patterns),'prompt patterns')
