# Ground-truth (schema 2) progress. Read by tools/resume_after_reset.sh: a line that starts with "- [ ]" means work remains.
# "- [x]" = converted and checked (strict build 0/0, verification.csv, readme_notes.md, out/README.md, all checkers pass).
# "- [~]" = blocked, do not touch (the script ignores it).
# Order = the order to work in (smallest first). Recipe: handoff/CONVERSION_RECIPE.md. Rules of Yang: memory file ground-truth-requirements.md.
- [x] Currency
- [x] Diary
- [x] hash-checker
- [x] Omni-Notes
- [~] openlauncher   (blocked: something other than the main session edited graphs/openlauncher/graph_def.py at 2026-10-25 18:43; it fails with NameError NEED_GESTURE; ask the user before touching)
- [ ] Vanilla-Music  (generated draft in graphs/Vanilla-Music; nothing hand-written yet; main classes were read, see "Plan" in memory)
- [ ] AnyMemo
- [ ] Markor
- [ ] Aegis
- [ ] AmazeFileManager
- [ ] AnkiDroid
- [ ] MMEX
- [ ] LibreTorrent
