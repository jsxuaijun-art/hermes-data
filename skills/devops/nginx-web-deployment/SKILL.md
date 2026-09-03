---
name: nginx-web-deployment
category: devops
description: nginx 反代/HTTPS/访问控制运维 — Basic Auth、证书、子路径部署、配置不生效排查。
---

# Nginx Web 部署运维（阿里云 47.103.27.171）

用户在阿里云服务器（47.103.27.171，Ubuntu 22.04，root）上跑多个 nginx 站点：`callback.yingxinkuaiji.com`（→8800）、`hermes-gateway`（处理 47.103.27.171:443）、`images`、`/diag/`（注销清税诊断 Flask 应用 →8000）。本技能存**通用可迁移的 nginx/Web 部署技术**；服务器上 Hermes 的拓扑、升级流程、diag 应用细节在用户自有的 `aliyun-hermes-server` / `hermes-server-ops` 技能里，勿重复。

## When to Use

- 给 web 应用加访问密码 / Basic Auth
- 改 nginx 反代、加 location、换证书、做子域名
- 「nginx 配置改了但没生效」类排查
- 部署 Flask/其他应用挂到 nginx 子路径下

## Basic Auth 给应用加密码（auth_basic）

1. **生成密码文件**（服务器无 htpasswd 命令，用 openssl `-apr1`——nginx 支持的 MD5 格式）：
   ```bash
   HASH=$(openssl passwd -apr1 '密码')
   printf "用户名:%s\n" "$HASH" > /etc/nginx/.htpasswd_xxx
   ```
2. 在目标 location 加两行：
   ```
   location /xxx/ {
       auth_basic "说明文字";
       auth_basic_user_file /etc/nginx/.htpasswd_xxx;
       proxy_pass http://127.0.0.1:8000/;
   }
   ```
3. `nginx -t && systemctl reload nginx`
4. **验证**（无凭据 401 / 带凭据 200）：
   ```bash
   curl -sk -o /dev/null -w "HTTP %{http_code}\n" https://IP/xxx/           # 期望 401
   curl -sk -u 用户名:密码 -o /dev/null -w "HTTP %{http_code}\n" https://IP/xxx/  # 期望 200
   ```
5. 改密码 = 重新生成哈希、替换 htpasswd 文件里该用户行、reload nginx。密码变更后要同步通知使用者（如企微群 webhook）。

## ⚠️ 坑：sites-enabled 里的 .bak 残留会「吞掉」新配置

`include /etc/nginx/sites-enabled/*` 加载目录下**所有**文件，包括备份（如 `hermes-gateway.bak.diag`）。两个 server 块监听同一 IP:443 且 server_name 相同 → nginx 告警 `conflicting server name ... ignored`，**先加载的块接管请求**，你改的正式块被忽略 → 改动看似无效（实测：加了 auth_basic 后无密码仍返回 200）。

- 备份必须放 sites-enabled **外**（如 `/etc/nginx/backups/`），不要留在 enabled 目录。
- 见到 conflicting server name 警告：`grep -rln "<IP 或域名>" /etc/nginx/` 找出所有重复块，把旧的移出 sites-enabled 再 reload。

## HTTPS 证书：自签名 vs Let's Encrypt

- **自签名**（openssl 生成，subject==issuer，如 `/etc/nginx/ssl/hermes.crt` CN=47.103.27.171）：浏览器提示「不安全/不是私密连接」，同事首次访问要「高级→继续前往」。内部工具可接受，但需在企微群发引导说明。
- **Let's Encrypt（acme.sh）只能签域名，不能签裸 IP**。要消除警告必须绑域名子域（如 `diag.yingxinkuaiji.com`）：用户先在阿里云域名解析加 A 记录（类型 A、主机记录 diag、记录值 47.103.27.171）→ 等解析生效（`nslookup` 验证）→ acme.sh 签发 → nginx 换证书。
- 查证书：`openssl x509 -in <cert> -noout -subject -issuer -dates`（subject==issuer 即自签名）。

## Flask 应用挂 nginx 子路径（location /xxx/ + proxy_pass 剥前缀）

- 子路径下的应用**所有表单 action / 链接必须相对路径**（`action="diagnose"`、`href="download/xxx"`），绝对路径会绕开 /xxx/ 直接 404。
- Flask 生产模式缓存模板：改模板要 `TEMPLATES_AUTO_RELOAD=True` 或重启服务；改 app.py 必须 `systemctl restart <service>`。
- 上传中文文件名：用 uuid + 原扩展名保存（`secure_filename` 会剥中文导致 openpyxl 认不出格式）。
- 独立子域名方案更省心：专属 server 块 root 反代 8000，无需子路径、无需相对路径 hack。

## 服务端验证套路

- `nginx -t`（语法）+ `systemctl reload nginx`（重载）
- 本机健康：`curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/`（在服务器上测）
- 外网：`curl -sk https://IP/...`（-k 跳过自签名校验）
