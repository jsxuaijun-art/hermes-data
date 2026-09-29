# 阿里云 ECS 环境拓扑（2026.8.17 实测）

> 服务器：47.103.27.171（root@ SSH 可连，Ubuntu，nginx 1.18.0）
> 用途：企微网关、图片托管、wenyan 公众号排版、未来 H5 留资页托管

## 端口与进程

| 端口 | 服务 | 说明 |
|:-----|:-----|:-----|
| 80 / 443 | nginx | 主站点（含 HTTPS），`callback`、`hermes-gateway` 等站点配置 |
| 8080 | nginx | 图片托管（`images` 站点，公众号配图/官网图源） |
| 8000 | python | HTML 服务（未知具体，supervisord 管理） |
| 8800 | python | 服务（`hermes_bridge.py` 企微桥接，supervisord 管理） |
| 3000 | node | wenyan 公众号排版服务（@wenyan-md/cli serve） |

## 关键路径 / 配置

- 静态目录：`/var/www/html/`（images/、manga/、screenshot.png 等）
- nginx 站点：`/etc/nginx/sites-enabled/`（callback、hermes-gateway、images）
- 进程管理：supervisord（`/etc/supervisor/supervisord.conf`），新增后台服务用它托管
- 企微桥接：`/root/hermes-data/wecom-bot/hermes_bridge.py`（8800）
- Hermes gateway 也在 ECS 上跑（hermes_cli.main gateway run）

## 部署注意

- **无 PHP**（`php -v` 报 command not found）→ 后端用 Python（FastAPI/Flask）或 Node
- 静态 H5 页放 `/var/www/html/`，新增后端服务用 supervisord 托管，nginx 反代或单独 location
- 公众号菜单「跳转网页」需要 HTTPS/已备案域名（IP+端口不被信任）
