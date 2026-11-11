# 把代登录设置和默认账号写进 app.db（表名和列名来自上游 cps/config_sql.py、cps/ub.py 的 v4.0.8 源码）。
# 这些值上游只存在 app.db，没有环境变量；应用启动时把 settings 表读进内存单例，
# 所以必须在应用启动前（本 oneshot 排在应用服务之前）写好，配置页的表单接口对缺省键会
# 把别的开关清成关，不能用来部分提交。
import os
import sqlite3

from werkzeug.security import generate_password_hash

owner = os.environ["WONTON_OWNER_NAME"]
secret = os.environ["WONTON_SECRET_CLIENT_PASSWORD"]
assert owner and secret

db = sqlite3.connect("/config/app.db")
# 默认角色 258 = 下载(1<<1) + 网页阅读(1<<8)：代登录自动建的家人账号能读书、能下载；
# 上游默认 0，自动建的号登录后既不能读也不能下，对家庭库没有用。
db.execute(
    """UPDATE settings SET
         config_allow_reverse_proxy_header_login = 1,
         config_reverse_proxy_login_header_name = 'Remote-User',
         config_reverse_proxy_auto_create_users = 1,
         config_default_role = 258"""
)
# 密码哈希和应用同源（镜像里的 werkzeug），OPDS 的 Basic Auth、发阅读器的密码都用它校验。
db.execute(
    "UPDATE user SET password = ? WHERE lower(name) = 'admin'",
    (generate_password_hash(secret),),
)
if owner != "admin":
    db.execute("UPDATE user SET name = ? WHERE lower(name) = 'admin'", (owner,))
db.commit()

row = db.execute("SELECT name FROM user WHERE lower(name) = ?", (owner,)).fetchone()
settings_row = db.execute(
    "SELECT config_allow_reverse_proxy_header_login,"
    " config_reverse_proxy_login_header_name,"
    " config_reverse_proxy_auto_create_users FROM settings"
).fetchone()
db.close()

if row is None:
    raise SystemExit(f"[wonton-sso] 写完后找不到账号 {owner}，app.db 状态异常")
if settings_row != (1, "Remote-User", 1):
    raise SystemExit(f"[wonton-sso] 设置没写进去：{settings_row}")
print(f"[wonton-sso] app.db 已配置：代登录 Remote-User，账号 {owner}（默认角色 下载+网页阅读）")
