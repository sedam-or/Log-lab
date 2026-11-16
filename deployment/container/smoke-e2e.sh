#!/usr/bin/env bash
# Uji e2e container Modul 7: build, jalankan dua service, cek health, seed akun uji,
# login lewat Source, lalu pastikan event sampai di Monitor. Tidak mencetak secret.
#   LOGLAB_PRIVATE_DIR=/folder/privat bash deployment/container/smoke-e2e.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE=(docker compose -f "$HERE/compose.yaml")
export LOGLAB_PRIVATE_DIR="${LOGLAB_PRIVATE_DIR:?set LOGLAB_PRIVATE_DIR (lihat make-private.sh)}"
[[ -f "$LOGLAB_PRIVATE_DIR/test-accounts.json" ]] || { echo "akun uji tidak ada" >&2; exit 2; }

wait_healthy() {
  local name="$1" status
  for _ in $(seq 1 40); do
    status="$(docker inspect --format '{{.State.Health.Status}}' "$name" 2>/dev/null || echo missing)"
    [[ "$status" == healthy ]] && { echo "$name: $status"; return 0; }
    sleep 3
  done
  echo "$name: tidak sehat (status=$status)" >&2
  return 1
}

echo "== 1. build dan start"
"${COMPOSE[@]}" up -d --build
wait_healthy loglab-source
wait_healthy loglab-monitor

echo "== 2. health dari dalam container (tanpa port ke host)"
"${COMPOSE[@]}" exec -T source python -c "import os,ssl,urllib.request as u; c=ssl.create_default_context(cafile=os.environ['LOGLAB_CA_BUNDLE']); print(u.urlopen('https://%s:%s/health' % (os.environ['LOGLAB_BIND_HOST'], os.environ['LOGLAB_PORT']), context=c, timeout=5).read().decode())"
"${COMPOSE[@]}" exec -T monitor python -c "import os,ssl,urllib.request as u; c=ssl.create_default_context(cafile=os.environ['LOGLAB_CA_BUNDLE']); print(u.urlopen('https://%s:%s/health' % (os.environ['LOGLAB_BIND_HOST'], os.environ['LOGLAB_PORT']), context=c, timeout=5).read().decode())"

echo "== 2b. hash operator di container cocok dengan password (password dibaca dari berkas, tidak dicetak)"
"${COMPOSE[@]}" exec -T monitor python -c "import os,sys; from loglab.security import verify_password; print('operator hash cocok:', verify_password(sys.stdin.read().strip(), os.environ['LOGLAB_OPERATOR_PASSWORD_HASH']))" < "$LOGLAB_PRIVATE_DIR/operator-password.txt"

echo "== 3. seed akun uji ke Source"
"${COMPOSE[@]}" exec -T source python -m loglab.seed_source_accounts --accounts-file - < "$LOGLAB_PRIVATE_DIR/test-accounts.json"

echo "== 4. login lewat Source (hasil saja, kredensial tidak dicetak)"
python3 - "$LOGLAB_PRIVATE_DIR/test-accounts.json" "$LOGLAB_PRIVATE_DIR/login-body.json" <<'PY'
import json, sys
accounts = json.load(open(sys.argv[1], encoding="utf-8"))
user, password = next(iter(accounts.items()))
json.dump({"username": user, "password": password}, open(sys.argv[2], "w", encoding="utf-8"))
PY
"${COMPOSE[@]}" exec -T source python -c "import os,ssl,json,sys,urllib.request as u; c=ssl.create_default_context(cafile=os.environ['LOGLAB_CA_BUNDLE']); req=u.Request('https://%s:%s/api/v1/login' % (os.environ['LOGLAB_BIND_HOST'], os.environ['LOGLAB_PORT']), data=sys.stdin.buffer.read(), headers={'Content-Type':'application/json'}); print(u.urlopen(req, context=c, timeout=5).read().decode())" < "$LOGLAB_PRIVATE_DIR/login-body.json"
rm -f "$LOGLAB_PRIVATE_DIR/login-body.json"

echo "== 5. tunggu event sampai di Monitor (maks 90 detik)"
count=0
for _ in $(seq 1 30); do
  count="$("${COMPOSE[@]}" exec -T monitor python -c "import sqlite3; c=sqlite3.connect('/var/lib/loglab/monitor.sqlite3'); print(c.execute('SELECT COUNT(*) FROM monitor_events').fetchone()[0])" 2>/dev/null || echo 0)"
  count="${count//[$'\r\n ']/}"
  [[ "$count" =~ ^[0-9]+$ && "$count" -ge 1 ]] && break
  sleep 3
done
echo "event di Monitor: $count"
[[ "$count" -ge 1 ]] || { echo "event belum sampai di Monitor" >&2; exit 1; }

echo "== 6. status service"
"${COMPOSE[@]}" ps
