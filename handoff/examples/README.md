Worked examples of the helper scripts used for hash-checker and Omni-Notes (run from `work/`, copy them out and adjust the paths first):

- `make_vlog_hash_checker.py`, `make_vlog_omni_notes.py`: write `graphs/<App>/verification.csv` from the final build. Every note is asserted against the graph (`has_edge`) so the log cannot say something the graph does not carry. The Omni one also rebuilds the first graph (`SCR/omni_old`: the archived v1 definition built with the current builder) to tell which first-graph routes had the first-resume shortcut; the path `SCR` is a scratch directory, change it.
- `croute.py <App> <method>...`: compact route printer (kind, class, trigger, guard, ENV, STATE, evidence) with the enclosing `if` / `for` / `catch` lines of each bytecode-cited call.
- `src.py <App> File.java:from-to ...`: prints source lines of the app by file name (flavor aware, uses `tools/show_route.py`).
