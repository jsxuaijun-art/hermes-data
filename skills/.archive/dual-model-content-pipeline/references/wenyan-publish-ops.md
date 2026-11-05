# wenyan 发布实操（2026.8.12 实测定稿）

## 核心事实：wenyan CLI 只在服务器上，本机没有

- 服务器 `/usr/lib/node_modules/@wenyan-md/cli/dist/cli.js` 存在（node v24.16.0）
- 本机 WSL **没有** wenyan CLI（`/usr/lib/node_modules/` 下不存在）——本机跑 publish 报 `Cannot find module`，不要浪费时间找本机安装
- wenyan server 在服务器 127.0.0.1:3000；根路径 GET 返回 404 是正常的（API 端点能工作即可，别误判服务挂了）

## 标准发布链路（markdown → rsync 到服务器 → ssh 上跑 publish）

```bash
# 1) 本机清代理 + rsync 传 md（unset 是必须的，否则残留代理 172.23.96.1:7890 拖死）
unset http_proxy https_proxy all_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY
rsync -av --timeout=20 -e "ssh -o ConnectTimeout=10" /tmp/article_xxx.md root@47.103.27.171:/tmp/article_xxx.md

# 2) 服务器上执行 publish（-c 指定主题 css；02 = 刘润红蓝撞色）
ssh -o ConnectTimeout=15 root@47.103.27.171 'cd /tmp && NODE_OPTIONS="--experimental-require-module" node /usr/lib/node_modules/@wenyan-md/cli/dist/cli.js publish -f /tmp/article_xxx.md --server http://127.0.0.1:3000 -c /etc/wenyan/themes/02-liurun-honglan.css 2>&1 | tail -30'
```

- 成功标志：`发布成功，Media ID: <40位base64>`，复制 Media ID 给用户（公众号后台草稿箱用它拉草稿）
- 主题 css 清单：`/etc/wenyan/themes/01-anxinbojun.css`（红底传统）、`02-liurun-honglan.css`（15px·红#FF2941/蓝#0052FF·不首行缩进）

## 02 风格红蓝撞色 recolor 配方（2026.8.12 实测）

02 风格下不要全文用默认红 #CC0000，按语义分色：

- **红 #FF2941**：标题序号（一、二、三）、核心冲击数字（罚款倍数、个税比例20%、关键日期如12月31日、涉税金额）
- **蓝 #0052FF**：对比/背景数字（大额交易红线触发线：公户200万、个人50万、现金5万；滞纳金万分之五；0.5倍至5倍罚款区间——这些是"触发线/区间"，不是单点冲击）
- 实现：先精确 replace 出蓝名单（带上下文防误伤），剩余 #CC0000 全部批量替换为 #FF2941
- 验证：`grep -o 'color:#[0-9A-F]*;">[^<]*</span>'` 列出全部颜色标注，人工核对语义分配；确认 `#CC0000` 残留为 0

## 配图上传（rsync 替代 scp）

见 SKILL.md 配图处理第2条。图片放 `/var/www/html/images/`，nginx 8080 提供静态访问，md5 查重防重复。

## 踩坑记录

1. scp 反复超时被工具拦截 → 根因是本机残留代理 env（172.23.96.1:7890），unset 后 rsync 秒传。**所有到 47.103.27.171 的传输命令开头先 unset 代理。**
2. 单条命令串多个 scp 会超时 → 分步/用 rsync 一次传多张没问题。
3. 本机别找 wenyan CLI，直接 ssh 服务器执行。
