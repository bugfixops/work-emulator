# Trigger graph output, schema 2

Proposal for the reviewer: how the ground-truth requirements (3.1, 3.2, 4, 6) appear in the files. The file list per app stays: `<prefix>_trigger_graph.json`, `methods.csv`, `README.md`, optional HTML viewer. Two files are new: `verification.csv` (the audit log) and `sanity_check.csv` (tool coverage next to the labels). Implemented in `tools/build_graph.py`; nothing is verified yet unless a `verification.csv` row says so.

## Fields

| Requirement | Where | Values |
|---|---|---|
| 3.1 reachability class | `verdict` (JSON map, CSV column) | `REACHABLE`, `UNREACHABLE` |
| 3.1 reason of an UNREACHABLE method | `labels[m].unreachable.kind` and `.text`; CSV `unreachable_kind`, `unreachable_reason` | `no_trigger_in_app`, `branch_never_taken`, `framework_never_calls`, `closed_by_configuration` (debug build, manifest, permission), `closed_by_api_level` (code for another Android version than 27) |
| 3.2 (1) ENV gate | `labels[m].env` = list of `{kinds, text}`; CSV `env_kinds`, `env` | `network`, `tls_chain`, `permission`, `hardware`, `other_app`, `system_event`, `time`, `other` |
| 3.2 (1) STATE gate | `labels[m].state`; CSV `state_kinds`, `state` | `data`, `settings`, `account`, `file`, `session` |
| 3.2 (2) implicit edges | every edge: `edge_class` (and `via` for non_standard); per method: `route_edge_classes`, `explicit_standard_route` | `explicit`, `standard`, `non_standard` (`page` = a page transition of the model, not counted) |
| 2 how a label was confirmed | `labels[m].confirmed_by`, `source_ref` | `DEVICE`, `SOURCE`, `INFERRED` |
| 4 paths | CSV `route_edge_ids` (the derived route); JSON `paths[]` only for verified paths; `path_status` | `UNCHECKED`, `SOURCE_OK`, `DEVICE_OK`, `STALE`, `WRONG` |
| 6 error rate per app | JSON `verification`, computed from `verification.csv` | for label, edge, path: checked, errors found, error rate |

Removed: `dead`, `framework_only`, and the verdicts DEAD, FRAMEWORK_ONLY, REACHABLE_AFTER_SETUP (the setup becomes STATE). Moved: Monkey/APE columns to `sanity_check.csv`; the frontier columns are dropped. Edge ids are now a hash of the edge's content, so editing other edges never renumbers an edge; a changed edge gets a new id and the paths verified through it turn `STALE`.

## How the labels are derived

- `REACHABLE` when a route from the launcher entry exists (STATE gates allowed); otherwise `UNREACHABLE`, and every UNREACHABLE method needs an authored reason with a source reference (no automatic dead code).
- Best route: of the cheapest route without a STATE gate and the cheapest route overall, the one with the fewest ENV kinds, then the fewest STATE kinds, then the fewest steps. `env` and `state` list the gates on that route (a gate that another route avoids is not a blocker); `route_edge_classes` are the classes of its edges; `explicit_standard_route` says whether some route (any gates) uses only explicit and standard edges.
- `confirmed_by` is `SOURCE` when every claim in the evidence of every edge of the best route cites a source line (`SRC` app file:line, `FW-SRC` Android 8.1.0_r1 or library file:line), `INFERRED` when any claim rests on memory, inference or another app, and `DEVICE` only through a `verification.csv` row (our own replay on the emulator). Tool coverage never sets it and no edge may cite it.
- `verification.csv` columns: `type` (label, edge, path), `item` (method or edge id), `result` (`correct`, `fixed` = it was wrong and is now corrected, `wrong`, `unclear`), `confirmed_by`, `ref` (file:line or scenario id), `edges` (for a path row: the ids of the verified route), `note`. Error rate = (fixed + wrong) / (correct + fixed + wrong); the share of correct paths is one minus the path error rate.

## Edge class rules (defaults; any edge can be overridden by hand)

- `explicit`: a direct call in the app code.
- `standard`: lifecycle callbacks; callbacks and listeners registered in the app code through the framework API (`setOnClickListener`, menu callbacks, `AsyncTask`, `startActivity(new Intent(this, X.class))`, `startActivityForResult` with `onActivityResult`); the launcher entry.
- `non_standard`, with `via`: a library or reflection makes the link and nothing in the app code calls or registers the target: EventBus, ButterKnife, data binding, DI, Rx, reflection, XML `android:onClick`, views and fragments instantiated from layout XML, intents resolved by action name (manifest receivers for system broadcasts, widget providers).

## Open points for the reviewer

1. Are the field names and the new files acceptable? (`verdict` keeps its name; `labels` is new.)
2. ENV and STATE kinds: your lists plus `other` (ENV) and `session` (STATE, for in-process state such as the selection mode or a second visit in the same process). Is in-memory state a STATE?
3. The edge class rules above, especially: manifest receivers and widget providers reached by an action name are `non_standard`; explicit-component intents and the launcher entry are `standard`; XML `android:onClick` and XML-instantiated views are `non_standard`.
4. The five UNREACHABLE reasons; code behind `SDK_INT` checks that cannot hold on API 27 is `closed_by_api_level`.
5. Tool coverage lives only in `sanity_check.csv` and never touches a label; the frontier columns are gone.
6. The confirmation fields are in the shared files (you wrote "keep internally"); fine?
7. Standard configuration: our copy of the dataset has `_fixtures` but no `_setup`; which API 27 image do you use (Google APIs or plain, arm64 or x86); and is the dataset's Currency v1.58 the version to use (your examples cite v1.33)?

The HTML viewer still builds and understands the new labels. Helper scripts written for schema 1 (`hubs`, `sample_paths`, `show_paths`, `summary_table`, `gen_readme`, `compare_graphs`, `make_test_manifest`, ...) read columns that no longer exist and apply only to the old outputs.

Helper tools: `tools/show_route.py` (a route with the source lines it cites), `tools/verify_sample.py` (the stratified sample of paths to read), `tools/check_routes.py` (routes whose guards contradict each other), `tools/gen_readme_v2.py` (README from the outputs), `tools/tests/check_v2.py` (the new tool gives the old paths on unconverted graphs).
