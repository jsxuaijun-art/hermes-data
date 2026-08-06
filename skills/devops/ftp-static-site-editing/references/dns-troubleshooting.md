# DNS Troubleshooting — Session Transcript

## Context

Date: 2026-05-26
Domain: yingxinkuaiji.com
Host: WSL (无 dig 工具)
DNS Provider: 西部数码 (ns1.myhostadmin.net)
Web Host: 西部数码虚拟主机 (gotoip11 → vhostgo.com)

## Problem

17:35 左右在西部数码添加了 Google Search Console TXT 验证记录。18:35 检查时仍未生效。

## Diagnosis Steps

### Step 1: Try standard tools (all fail)

```bash
# ❌ dig not found
dig txt yingxinkuaiji.com +short
# → command not found

# ❌ nslookup not installed in WSL
nslookup -type=txt yingxinkuaiji.com
# → command not found

# ❌ host not installed
host -t txt yingxinkuaiji.com
# → command not found

# ❌ apt-get needs sudo (password required)
sudo apt-get install -y dnsutils
# → "a terminal is required to read the password"

# ❌ pip install times out
pip install dnspython
# → timed out after 30s

# ❌ DNS-over-HTTPS also times out (firewall?)
curl -s "https://dns.google/resolve?name=yingxinkuaiji.com&type=TXT"
# → timed out after 15s
```

### Step 2: Use Windows' nslookup via WSL interop ✅

```bash
# Query with default DNS
/mnt/c/Windows/System32/nslookup.exe -type=txt yingxinkuaiji.com
# → Shows only CNAME info, no TXT records

# Query Google DNS explicitly
/mnt/c/Windows/System32/nslookup.exe -type=txt yingxinkuaiji.com 8.8.8.8
# → Again, no TXT records. Only shows:
#   yingxinkuaiji.com → CNAME → jsxuaijun.gotoip11.com → CNAME → web.s1286.vhostgo.com

# Query ANY type to see all records
/mnt/c/Windows/System32/nslookup.exe -type=any yingxinkuaiji.com 8.8.8.8
# → Shows: nameservers (ns1/ns2.myhostadmin.net), MX records (mxbiz1/2.qq.com)
#   NO TXT records. Serial: 2025051609

# Query authoritative nameserver directly
/mnt/c/Windows/System32/nslookup.exe -type=txt yingxinkuaiji.com ns1.myhostadmin.net
# → Still only CNAME, no TXT
```

### Step 3: Root cause identified

**The domain has a CNAME record at the apex:**

```
yingxinkuaiji.com  CNAME  jsxuaijun.gotoip11.com
```

Per RFC 1912, CNAME records cannot coexist with ANY other record type (including TXT). This means:

- The TXT record was either silently rejected by the DNS provider, OR
- It was added to the zone but never published because the CNAME takes priority

**Key diagnostic clue:** The serial number on the SOA record is `2025051609` — this suggests the zone hasn't been updated recently enough to include the TXT record.

## Verified Result

After 60 minutes, the TXT record was **not visible** from any DNS server queried (Google DNS 8.8.8.8, authoritative ns1.myhostadmin.net, local Windows resolver).

## Recommended Fix

Two options presented to user:

1. **Subdomain verification (faster):** Verify `www.yingxinkuaiji.com` instead of the root domain in Google Search Console, and add the TXT record to the `www` subdomain
2. **Replace CNAME with A record:** Delete the apex CNAME, get the IP from the host provider, add A record, then TXT records can coexist
