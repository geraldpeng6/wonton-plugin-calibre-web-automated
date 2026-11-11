# 家庭书架（Calibre-Web Automated）

开发流程见[插件开发指南](https://github.com/wontonapp/wonton-docs/blob/main/develop.md)，规范见[插件规范](https://github.com/wontonapp/wonton-docs/blob/main/plugin-spec.md)。

把 [Calibre-Web Automated](https://github.com/crocodilestick/Calibre-Web-Automated)（GPL-3.0）装进云吞：电子书自动入库（转格式、补元数据）、网页读书、阅读器 App 经 OPDS 连上来读。上游镜像按清单列表摘要固定（`crocodilestick/calibre-web-automated:v4.0.8`，amd64 + arm64），未修改上游、未另发镜像。

## 权限

| 权限 | 用途 |
| --- | --- |
| `storage.share.books:write` | 书库放在 `books` 共享文件夹（容器内 `/calibre-library`），应用要写 `metadata.db` 和转换后的书 |
| `network.egress` | 抓封面、简介等元数据（应用内置源：Google Books、Douban 等） |
| `network.lan` | 阅读器 App 在局域网直连 8083（OPDS，应用自带的账号密码认证）；详情页开关默认关 |
| `owner.identity` | 把默认管理员账号改成用户的用户名 |

## 登录

`webui.sso: proxy`，网关带 `Remote-User: {user}` 请求头。Calibre-Web 的"允许反向代理认证"、头名和"自动建号"三项存在 `/config/app.db`（`settings` 表），没有环境变量；首次启动由镜像内的 s6 一次性服务（`wonton-sso`，经 `configs` 注入，排在应用服务之前）直接写库，同时把默认管理员 `admin` 改名为用户的用户名、密码换成 `secrets` 生成的 `client_password`（OPDS、发阅读器 App 都用这套账号）。家人打开网页时按 `{user}` 自动建普通用户（默认角色：下载 + 网页阅读，见 `sso-setup.py`）。

已配过（`/config/.wonton-sso-ready`）就不再改，用户在应用里改的设置不会被重装冲掉。

## 截图

`screenshots/` 里是插件网页在手机宽度（390×844）下的截图。

## 图标

`icon.svg` 用 Calibre-Web Automated 官方标志（viewBox 平移到原点，图形未改），来源、许可与商标说明见 [NOTICE](NOTICE)。
