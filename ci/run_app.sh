#!/usr/bin/env bash
# Run one app on an emulator that is already booted: install it, push the fixtures, run Monkey (or APE) for N minutes
# while dumping JaCoCo coverage every DUMP_INTERVAL seconds, then merge the dumps and write the reports.
#
#   bash ci/run_app.sh <App> <minutes> <seed> <tool> <outdir>
#
# Needs adb, java and python3 on PATH and the JaCoCo CLI (ci/get_jacoco.sh puts it in .cache/jacococli.jar).
# The tool command lines are the ones of the baseline runs (same flags and seed).
# Test knobs, not used in CI: RUN_SECONDS (replaces minutes*60), DUMP_INTERVAL (30), ADB (adb), JAVA (java), JACOCO.
set -u -o pipefail

APP=${1:?usage: run_app.sh <App> <minutes> <seed> <tool> <outdir>}
MINUTES=${2:-60}
SEED=${3:-20261016}
TOOL=${4:-monkey}
OUT=${5:-out/$APP}

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(dirname "$HERE")
mkdir -p "$OUT"
OUT=$(cd "$OUT" && pwd)
cd "$ROOT" || exit 2

ADB=${ADB:-adb}
JAVA=${JAVA:-java}
JACOCO=${JACOCO:-$ROOT/.cache/jacococli.jar}
INTERVAL=${DUMP_INTERVAL:-30}
RUN_SECONDS=${RUN_SECONDS:-$((MINUTES * 60))}
STATUS=ok
TOOL_RC=''
STARTED=''
ENDED=''
APP_ALIVE=''

log() { printf '[%s] %s\n' "$(date -u +%H:%M:%S)" "$*" | tee -a "$OUT/run.log"; }
group() { if [ -n "${GITHUB_ACTIONS:-}" ]; then echo "::group::$*"; fi; }
endgroup() { if [ -n "${GITHUB_ACTIONS:-}" ]; then echo "::endgroup::"; fi; }
prop() { $ADB shell getprop "$1" 2>/dev/null | tr -d '\r'; }

if ! command -v "$ADB" >/dev/null 2>&1; then
  for d in "${ANDROID_HOME:-}" "${ANDROID_SDK_ROOT:-}" /usr/local/lib/android/sdk; do
    if [ -n "$d" ] && [ -x "$d/platform-tools/adb" ]; then export PATH="$d/platform-tools:$PATH"; break; fi
  done
fi

eval "$(python3 -I ci/app_env.py "$APP")" || { echo "unknown app $APP"; exit 2; }
DEVICE_EC=/data/data/$PKG/files/coverage.ec
: > "$OUT/segments.csv"
mkdir -p "$OUT/segments"

# One coverage dump. The receiver writes only what ran since the previous dump (it resets its counters), so no dump may be lost.
dump_once() {
  local idx f t reply bytes magic valid
  idx=$(wc -l < "$OUT/segments.csv" | tr -d ' ')
  f="$OUT/segments/$(printf '%05d' "$idx").ec"
  t=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  reply=$($ADB shell am broadcast -a edu.gatech.m3.emma.COLLECT_COVERAGE -n "$PKG/$RECEIVER" 2>&1 | tr -d '\r' | tr '\n,' '  ')
  rm -f "$f"
  if ! $ADB pull "$DEVICE_EC" "$f" >/dev/null 2>&1; then
    $ADB exec-out run-as "$PKG" cat files/coverage.ec > "$f" 2>/dev/null || rm -f "$f"
  fi
  $ADB shell rm -f "$DEVICE_EC" >/dev/null 2>&1
  bytes=0
  valid=false
  if [ -f "$f" ]; then
    bytes=$(wc -c < "$f" | tr -d ' ')
    magic=$(head -c 3 "$f" | od -An -tx1 | tr -d ' \n')
    if [ "$bytes" -gt 5 ] && [ "$magic" = 01c0c0 ]; then valid=true; fi
  fi
  printf '%s,%s,%s,%s,%s\n' "$idx" "$t" "$bytes" "$valid" "$reply" >> "$OUT/segments.csv"
}

dump_loop() {
  local n
  while true; do
    n=0
    while [ "$n" -lt "$INTERVAL" ] && [ ! -e "$OUT/.stop" ]; do sleep 1; n=$((n + 1)); done
    if [ -e "$OUT/.stop" ]; then break; fi
    dump_once
  done
}

tool_command() {
  case "$TOOL" in
    monkey)
      echo "timeout -s INT $RUN_SECONDS monkey -p $PKG -s $SEED --throttle 500 --ignore-crashes --ignore-timeouts --ignore-security-exceptions -v -v 100000000" ;;
    ape)
      echo "timeout -s INT $RUN_SECONDS env CLASSPATH=/data/local/tmp/ape.jar app_process /system/bin com.android.commands.monkey.Monkey -p $PKG -s $SEED --throttle 500 --ignore-crashes --ignore-timeouts --ignore-security-exceptions -v -v --ape sata --running-minutes $MINUTES" ;;
    *) echo "unknown tool $TOOL" >&2; return 1 ;;
  esac
}

finalize() {
  group "merge and report"
  local valid_files=() cls=() idx valid
  while IFS=, read -r idx _ _ valid _; do
    if [ "$valid" = true ]; then valid_files+=("$OUT/segments/$(printf '%05d' "$idx").ec"); fi
  done < "$OUT/segments.csv"
  for c in $CLASSES; do cls+=(--classfiles "$ROOT/$c"); done
  if [ "${#valid_files[@]}" -eq 0 ]; then
    [ "$STATUS" = ok ] && STATUS=no_coverage
  elif [ ! -f "$JACOCO" ]; then
    STATUS=no_jacoco
  elif ! { "$JAVA" -jar "$JACOCO" merge "${valid_files[@]}" --destfile "$OUT/merged.ec" \
           && "$JAVA" -jar "$JACOCO" report "$OUT/merged.ec" "${cls[@]}" --xml "$OUT/report.xml" --csv "$OUT/report.csv"; } >"$OUT/jacoco.log" 2>&1; then
    STATUS=report_failed
  fi
  [ -f "$OUT/logcat_crash.txt" ] && head -c 5000000 "$OUT/logcat_crash.txt" > "$OUT/logcat_crash.tmp" && mv "$OUT/logcat_crash.tmp" "$OUT/logcat_crash.txt"
  python3 -I ci/report.py "$OUT" "app=$APP" "package=$PKG" "tool=$TOOL" "seed=$SEED" "minutes=$MINUTES" "run_seconds=$RUN_SECONDS" \
    "status=$STATUS" "tool_exit=$TOOL_RC" "started=$STARTED" "ended=$ENDED" "app_alive_at_end=$APP_ALIVE" \
    "sdk=${SDK:-}" "abi=${ABI:-}" "fingerprint=${FINGERPRINT:-}" "screen=${SCREEN:-}" "root=${IS_ROOT:-}" \
    "github_run_id=${GITHUB_RUN_ID:-}" "github_sha=${GITHUB_SHA:-}" >> "$OUT/run.log" 2>&1
  gzip -f "$OUT/report.xml" "$OUT/tool.log" 2>/dev/null
  if [ -d "$OUT/segments" ]; then tar -czf "$OUT/segments.tar.gz" -C "$OUT" segments && rm -rf "$OUT/segments"; fi
  rm -f "$OUT/.stop"
  endgroup
  log "result: $APP status=$STATUS $(grep -E '"(methods_hit|methods_total|segments_valid|segments_total|events_injected|crashes)"' "$OUT/meta.json" 2>/dev/null | tr -d ' \n')"
  if [ "$STATUS" = ok ]; then
    echo "::notice title=$APP::$(tr -d '\n ' < "$OUT/meta.json" | cut -c1-600)"
    return 0
  fi
  echo "::error title=$APP::run finished with status $STATUS"
  return 1
}

# ---------------------------------------------------------------- device
group "device"
$ADB wait-for-device
for _ in $(seq 60); do [ "$(prop sys.boot_completed)" = 1 ] && break; sleep 2; done
$ADB root >/dev/null 2>&1 || true
$ADB wait-for-device
for _ in $(seq 30); do [ "$($ADB shell id -u 2>/dev/null | tr -d '\r')" = 0 ] && break; sleep 1; done
IS_ROOT=$([ "$($ADB shell id -u 2>/dev/null | tr -d '\r')" = 0 ] && echo yes || echo no)
SDK=$(prop ro.build.version.sdk)
ABI=$(prop ro.product.cpu.abi)
FINGERPRINT=$(prop ro.build.fingerprint)
SCREEN="$($ADB shell wm size 2>/dev/null | tr -d '\r' | tail -1) $($ADB shell wm density 2>/dev/null | tr -d '\r' | tail -1)"
log "device: sdk=$SDK abi=$ABI root=$IS_ROOT screen=[$SCREEN] fingerprint=$FINGERPRINT"
$ADB shell svc power stayon true >/dev/null 2>&1 || true
$ADB shell input keyevent KEYCODE_WAKEUP >/dev/null 2>&1 || true
$ADB shell wm dismiss-keyguard >/dev/null 2>&1 || true
endgroup

# ---------------------------------------------------------------- install and fixtures
group "install and fixtures"
reply=$($ADB install -r -g -t "$APK" 2>&1 | tr -d '\r')
log "install $APK: $(echo "$reply" | tail -1)"
if ! echo "$reply" | grep -q '^Success'; then
  STATUS=install_failed
  finalize
  exit 3
fi
for d in Download Music Pictures Documents; do
  if [ -d "fixtures/$d" ]; then $ADB push "fixtures/$d" /sdcard/ >/dev/null 2>&1 || log "push of fixtures/$d failed"; fi
done
for f in fixtures/Music/* fixtures/Pictures/*; do
  [ -f "$f" ] || continue
  $ADB shell am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE \
    -d "file:///sdcard/$(basename "$(dirname "$f")")/$(basename "$f")" >/dev/null 2>&1
done
if [ "$TOOL" = ape ]; then $ADB push ci/ape.jar /data/local/tmp/ape.jar >/dev/null 2>&1; fi
endgroup

# ---------------------------------------------------------------- run
CMD=$(tool_command) || { STATUS=bad_tool; finalize; exit 2; }
$ADB logcat -c >/dev/null 2>&1 || true
$ADB logcat -b crash -v time > "$OUT/logcat_crash.txt" 2>&1 &
LOGCAT_PID=$!
log "tool: $CMD"
dump_once
dump_loop &
LOOP_PID=$!
STARTED=$(date -u +%Y-%m-%dT%H:%M:%SZ)
T0=$(date -u +%s)
$ADB shell "exec $CMD" > "$OUT/tool.log" 2>&1 &
TOOL_PID=$!
while kill -0 "$TOOL_PID" 2>/dev/null; do
  if [ $(( $(date -u +%s) - T0 )) -ge $((RUN_SECONDS + 180)) ]; then
    log "watchdog: the tool is still running after the time limit, detaching from it"
    kill "$TOOL_PID" 2>/dev/null
    break
  fi
  sleep 5
done
wait "$TOOL_PID" 2>/dev/null
TOOL_RC=$?
ENDED=$(date -u +%Y-%m-%dT%H:%M:%SZ)
ELAPSED=$(( $(date -u +%s) - T0 ))
log "tool finished with exit code $TOOL_RC after $ELAPSED s"
if [ $((ELAPSED + 30)) -lt "$RUN_SECONDS" ]; then STATUS=tool_exited_early; fi
APP_ALIVE=$([ -n "$($ADB shell pidof "$PKG" 2>/dev/null | tr -d '\r')" ] && echo yes || echo no)
touch "$OUT/.stop"
wait "$LOOP_PID" 2>/dev/null
dump_once
kill "$LOGCAT_PID" 2>/dev/null
wait "$LOGCAT_PID" 2>/dev/null

finalize
exit $?
