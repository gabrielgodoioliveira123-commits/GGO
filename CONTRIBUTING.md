# Contributing

1. Prefer incremental improvements and preserve existing substantive requirements.
2. Run local tests, check syntax, and review licenses for new material.
3. Keep public documentation, comments, examples, and default user messages in English. Preserve proper names and user-supplied source text.
4. Do not copy complete third-party implementations without the applicable license and permission.
5. Do not commit private documents, generated customer output, or API credentials.
6. Adjust parameters and tests for longer prompts; never simulate completed page counts.
7. Update `CHANGELOG.md`, documentation, and release files after distribution changes:

```bash
python scripts/build_release.py
python -m unittest discover -s tests -v
python scripts/validate_skill.py
python scripts/verify_package.py
python scripts/build_release.py --check
```

Original project author: Gabriel Godoi de Oliveira. Attribute later contributions accurately rather than implying the original author wrote every subsequent change.
