# 微信发布错误码速查（wenyan publish 实战记录）

| 错误码 | 触发条件 | 原因 | 解决方案 |
|:------|:---------|:-----|:---------|
| 40113 | 正文中含 `asset://` 图片引用 | WeChat 不识别 asset:// 协议 | 改用 HTTP 直链（nginx 8080 方案） |
| 45110 | `author:` 字段超过8个中文字符 | 微信作者栏长度限制 | 使用「苏州盈信财税」（6字）而非全称 |
| fetch failed | 封面图用 HTTP 而 wenyan-server 异常 | wenyan-server 端口占用或进程崩溃 | `fuser -k -n tcp 3000 && systemctl restart wenyan-server` |

## wenyan-server 故障恢复

```bash
# 杀占用进程
fuser -k -n tcp 3000
sleep 1
# 重启服务
systemctl restart wenyan-server.service
# 验证
curl -s http://localhost:3000/verify
```
