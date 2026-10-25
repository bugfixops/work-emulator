# work-emulator

Runs instrumented Android apps on a hosted emulator (Android 8.1, API 27, x86_64) and records JaCoCo method coverage.

For every app in `ci/apps.csv` one job boots the emulator, installs the app (`apks/`), pushes the sample files (`fixtures/`),
runs Monkey (or APE) for N minutes with the flags and seed of the earlier baseline runs, dumps the JaCoCo coverage every 30 s,
merges the dumps and writes the reports. All apps run in parallel, one job each.

## Run it

- **Actions → Emulator run → Run workflow** and choose the apps (`all` or a comma-separated list), the tool, the minutes and the seed, or
- edit `ci/run.conf` and push it to `main`: a push that changes this file starts a run with the values in it.

A run with 60 minutes per app takes about 75 minutes in total (boot, install, test, reports).

## Results

- Every job uploads the artifact `results-<App>` (kept for 7 days).
- The last job commits all of them to the branch `results` in `runs/<run id>-<attempt>/`, together with `SUMMARY.md` and `summary.csv`.
  The branch can be read without logging in: `git clone --branch results --depth 1 https://github.com/bugfixops/work-emulator.git`

Files per app:

| File | Content |
|---|---|
| `meta.json` | status, tool, seed, device data, segment and method counts, events, crashes, ANRs |
| `methods_hit.csv` | `class,method,desc,hit` for every method of the app (JaCoCo names; 1 = ran at least once) |
| `merged.ec`, `report.csv`, `report.xml.gz` | merged JaCoCo data and its reports |
| `segments.csv`, `segments.tar.gz` | one row and one raw `.ec` file per dump (each dump holds what ran since the previous one) |
| `tool.log.gz`, `logcat_crash.txt`, `jacoco.log`, `run.log` | tool output, crash log, JaCoCo output, script log |

`status` is `ok` when at least one valid dump was merged and reported and the tool ran for (almost) the whole time; other values
(`install_failed`, `no_coverage`, `report_failed`, `tool_exited_early`, ...) mark a run that is not comparable.

## Layout

| Path | Content |
|---|---|
| `apks/<App>.apk` | the instrumented app (13 open-source apps; each keeps its upstream license) |
| `classes/<App>/<i>/` | the class files that match the instrumentation, needed by the JaCoCo report |
| `fixtures/` | sample files pushed to `/sdcard` (`Download`, `Music`, `Pictures`, `Documents`) |
| `ci/apps.csv` | app, package, coverage receiver, APK, class directories, setup notes |
| `ci/run_app.sh` | everything that happens on the emulator for one app |
| `ci/plan.py`, `ci/collect.py`, `ci/publish_results.sh`, `ci/report.py`, `ci/get_jacoco.sh` | planning, summaries, publishing, JaCoCo download |

## Notes

- The coverage broadcast is `edu.gatech.m3.emma.COLLECT_COVERAGE` sent to the app's own receiver; the receiver resets its counters
  after every dump, so the dumps are merged, not compared one by one.
- Not automated: first-run setups (Aegis vault, AnkiDroid import, Markor tutorial, MMEX database), so those apps start from a fresh install plus the sample files.
- `fixtures/Documents` was assembled from the text files in `fixtures/Download`.
- APE needs an `ape.jar` built from the APE sources; put it at `ci/ape.jar` to use `tool: ape`.
- Emulator: AOSP image without Google services, 1080x1920 at 420 dpi, animations off, 3 cores and 3 GB RAM per emulator.
