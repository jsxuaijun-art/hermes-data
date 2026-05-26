---
name: ftp-static-site-editing
category: devops
description: 纯静态/ASP/PHP 网站的 FTP 远程编辑工作流 — 下载→搜索→替换→上传→验证。适用于不具备 CMS 后台或数据库驱动的传统网站维护。覆盖批量搜索替换、JSON-LD 部署、密码特殊字符编码等实战场景。
triggers:
  - User wants to edit content on a static/ASP website
  - User provides FTP credentials for website maintenance
  - User needs to search-replace text across a flat-file website
  - User needs to add/update JSON-LD or schema markup on an FTP-hosted site
  - FTP password contains special characters (* / % ! @ etc.)
  - Site is ASP static (non-QCNET99) on IIS
  - User says "改官网" or "网站内容更新"
  - User needs to bulk update contact info (address, phone) site-wide
  - User needs to verify domain ownership for Search Console/SEO/SSL
  - User asks to check DNS TXT record propagation
  - Domain has CNAME and TXT verification fails
---

# FTP Static Site Editing

## Overview

Workflow for editing **static/plain-file websites** hosted on FTP — no CMS, no database, just `.asp` / `.html` / `.php` files on a filesystem. Covers the discovery, editing, and verification cycle.

## Distinction from `db-website-content-mgmt`

| Skill | Applies to | Method |
|:------|:-----------|:-------|
| `db-website-content-mgmt` | Database-driven sites (ASP+Access, PHP+MySQL) | Injects server-side scripts to modify DB |
| **`ftp-static-site-editing`** | Flat-file sites (pure ASP/HTML/PHP) | Direct FTP file download → edit → upload |

## FTP Connection

### URL Format

```bash
# Standard
curl -sL ftp://hostname/path/to/file --user "username:password"

# ⚠️ PITFALL: Password with special characters in curl FTP URL
# When the password contains / * - % ! etc., you must URL-encode them
# in the FTP URL, OR use --user "username:password" parameter instead.
# 
# ❌ WRONG: curl ftp://user:pass/with/slashes@host  # / in password breaks path
# ✅ RIGHT: curl --user "username:pass/word-with*" ftp://host/path
# 
# Common encodings needed in URL:
#   / → %2F
#   * → %2A
#   - stays as -
#   ! → %21
# 
# Real example: password "Yx168168/*-"
#   --user "jsxuaijun:Yx168168/*-"  ✓ works
#   ftp://jsxuaijun:Yx168168%2F*-@host  ✓ also works but harder to type
```

### Directory Structure Note

FTP sites often have a **real root** that differs from the FTP login root:
```bash
# FTP login lands at / but real site is at /wwwroot/
ftp://host/                      → FTP root (may have backup index.asp)
ftp://host/wwwroot/              → REAL website root
```

Always verify by checking which `index.asp`/`index.html` serves HTTP content vs FTP content.

## Workflow: Search-Replace Across Site

### Step 1: Discover which files contain the target string

```bash
FTP_URL="ftp://username:password@host"
for f in file1.asp file2.asp file3.asp; do
  content=$(curl -sL "$FTP_URL/wwwroot/$f" 2>&1)
  if echo "$content" | grep -q "目标文字"; then
    echo "🔴 含目标: $f"
    echo "$content" > "local/$f"
  fi
done
```

### Step 2: Edit the file locally

Use `patch()` tool for targeted find-and-replace. For text content (not HTML tags), `patch()` with exact match works well.

### Step 3: Upload

```bash
curl -sL "ftp://host/wwwroot/file.asp" --user "user:pass" -T local/file.asp
```

### Step 4: Verify

```bash
# Check count of remaining old text
curl -s http://site.com | grep -c '旧文字'
# Check new text present
curl -s http://site.com | grep -c '新文字'
```

## Workflow: Add/Update JSON-LD

### ⚠️ CRITICAL: Always check existing content first

```bash
curl -s http://domain.com | grep -o 'application/ld+json' | wc -l
```

**If count > 0:** Download existing, **modify in-place** — do NOT add a second block.
**If count == 0:** Create from template (see `geo-optimization` skill references).

### Editing JSON-LD in downloaded file

1. Download: `curl -sL ftp://host/path --user "user:pass" -o local/file`
2. Edit: Use `patch()` to modify the existing JSON-LD block
3. Validate JSON syntax: Python `json.loads()` to verify
4. Upload back
5. Verify online:
   ```bash
   curl -s http://domain.com | grep -o 'application/ld+json' | wc -l  # should be 1
   curl -s http://domain.com | grep -o 'makesOffer\|@type\|FAQ'       # fields present
   ```

## Pitfalls

### ⚠️ HTTP vs HTTPS

IIS servers with outdated TLS configs fail on HTTPS curl:
```
SSL alert: error:0A000438:SSL routines::tlsv1 alert internal error
```
**Fix:** Always use `http://` (not `https://`) for curl checks on such servers.

### ⚠️ FTP vs Web root mismatch

FTP root may contain a backup `index.asp` that is NOT the real site. The real one is in a subdirectory (often `wwwroot/`). Always verify by comparing:
```bash
# What FTP says
curl -sL ftp://host/ --user "user:pass" | grep index.asp
# What HTTP serves
curl -s http://domain.com | head -5
```
If FTP root index.asp and HTTP root content differ → real site is in subdirectory.

### ⚠️ Multiple JSON-LD blocks hurt GEO

Search engines may merge or ignore duplicate schema blocks. Always maintain exactly ONE `application/ld+json` per page.

### ⚠️ Timeout on large batch downloads

FTP over curl is per-file and slow. For 15+ files, expect ~2-3 seconds per file. For bulk operations, consider lftp if available, or batch in groups.

## DNS Verification for Domain Ownership

### Background

Used when Google Search Console, SSL cert (Let's Encrypt), or other services ask you to add a TXT/CNAME record to verify domain ownership.

### When dig is unavailable

In WSL or minimal environments where `dig` (dnsutils) is not installed, use one of these alternatives:

| Tool | Command | Status on WSL |
|:-----|:--------|:-------------|
| `nslookup` (Windows) | `/mnt/c/Windows/System32/nslookup.exe -type=txt DOMAIN` | ✅ Works via WSL interop |
| `nslookup` (Linux) | `nslookup -type=txt DOMAIN` | ❌ May not be installed |
| `host` | `host -t txt DOMAIN` | ❌ Not in minimal installs |
| DNS-over-HTTPS | `curl -s "https://dns.google/resolve?name=DOMAIN&type=TXT"` | ⚠️ May be blocked by firewall |

**Recommended in this environment:** Use `/mnt/c/Windows/System32/nslookup.exe` directly.

### Query specific DNS servers

```bash
# Query Google's public DNS (most reliable for propagation check)
/mnt/c/Windows/System32/nslookup.exe -type=txt DOMAIN 8.8.8.8

# Query the authoritative DNS server directly
/mnt/c/Windows/System32/nslookup.exe -type=txt DOMAIN ns1.myhostadmin.net
```

### ⚠️ Critical: CNAME vs TXT conflict

**Standard DNS rule (RFC 1912):** A CNAME record at the root/apex of a domain **cannot coexist** with any other record type (TXT, MX, NS, A).

This is the #1 reason Google Search Console TXT verification fails silently:

```
yingxinkuaiji.com  →  CNAME  →  jsxuaijun.gotoip11.com  (西部数码虚拟主机)
                  →  (TXT record added but silently dropped by DNS)
```

**Diagnosis:** If `nslookup -type=any DOMAIN` shows a CNAME but `-type=txt` shows nothing, the TXT record was likely rejected due to conflict.

**Solutions (ordered by practicality for this case):**

0. **HTML file verification (simplest, no DNS changes):**
   - Download `googleXXXX.html` from Google Search Console
   - FTP upload to website root (`wwwroot/`)
   - Click Verify → GSC requests `http://domain/googleXXXX.html` → done
   - ✅ Works with CNAME apex conflict. No DNS changes needed.
   - ⚠️ File must stay on server permanently (don't delete after verification)
   - ⚠️ Must be in the REAL web root (not FTP root — `wwwroot/`)

1. **Use a subdomain instead** (recommended, fastest DNS-based fix):
   - Add `www.yingxinkuaiji.com` to Google Search Console instead of `yingxinkuaiji.com`
   - Add TXT record to `www` subdomain (which does NOT have CNAME conflict)

2. **Replace CNAME with A record** (for root domain):
   - Delete the CNAME record at the apex
   - Find the hosting server's IP address (ask hosting provider)
   - Add an A record pointing to that IP
   - Now TXT records can coexist at the apex

3. **Use DNS provider's CNAME flattening** (if supported):
   - Some providers (Cloudflare, DNSimple) offer "CNAME Flattening" or "ANAME" that auto-resolves at the edge
   - Western Digital / 西部数码 may not support this

### Reference file

See `references/dns-troubleshooting.md` for a detailed session transcript and reproduction steps.

## Verification Checklist

- [ ] Old string no longer appears on live site: `curl -s http://site | grep -c '旧文字'` == 0
- [ ] New string appears correctly: `curl -s http://site | grep '新文字'`
- [ ] No syntax errors (for ASP: response loads normally; for JSON-LD: JSON valid)
- [ ] File count preserved (didn't accidentally delete files)
- [ ] FTP password with special chars handled correctly via `--user` param
