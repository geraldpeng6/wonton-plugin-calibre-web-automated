#!/usr/bin/with-contenv bash
# 启动前的一次性配置（s6 oneshot，应用服务依赖本服务）：等上游的 cwa-init/cwa-auto-library 建好 app.db，
# 直接改库打开代登录、把默认 admin 换成用户自己的账号。应用第一次读配置就是改好的，不用重启、不用 HTTP 登录。
# 已配过（/config/.wonton-sso-ready）就跳过：重装、升级不冲掉用户后来在应用里改的设置。
set -euo pipefail

if [ "$(id -u)" = "0" ]; then
  # cwa-init 已把 /config 交给 PUID:PGID；以同一用户写库，不留 root 的 sqlite 日志文件。
  exec s6-setuidgid abc "$0" "$@"
fi

marker=/config/.wonton-sso-ready
[ -f "$marker" ] && { echo "[wonton-sso] 已配置过，跳过"; exit 0; }

: "${WONTON_OWNER_NAME:?核心没有注入用户名（owner.identity）}"
: "${WONTON_SECRET_CLIENT_PASSWORD:?核心没有注入密钥}"

db=/config/app.db
i=0
until [ -f "$db" ] && [ "$(sqlite3 "$db" "SELECT count(*) FROM sqlite_master WHERE name IN ('settings','user')")" = "2" ]; do
  i=$((i + 1))
  [ "$i" -lt 120 ] || { echo "[wonton-sso] app.db 两分钟内没有就绪（上游初始化没跑完？）"; exit 1; }
  sleep 1
done

/lsiopy/bin/python3 /etc/s6-overlay/s6-rc.d/wonton-sso/setup.py

: >"$marker"
echo "[wonton-sso] 代登录已打开，管理员账号已改为 $WONTON_OWNER_NAME"
