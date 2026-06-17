---
name: website-content-editing
category: devops
description: >-
  Editing content on traditional small/medium business websites (企业官网内容编辑).
  Covers two modes — flat-file (FTP download→edit→upload) AND database-driven
  (server-side script injection for ASP+Access / PHP+MySQL). Also covers CMS
  backend editing, JSON-LD deployment, DNS verification, and site content audit.
  Umbrella skill superseding db-website-content-mgmt and ftp-static-site-editing.
tags: [website, ftp, asp, php, access, mysql, cms, editing, json-ld, dns]
trigger: >-
  用户说"改官网"、"网站内容更新"、"改一下网站上的内容"、"改网站"、
  "官网维护"、"网站编辑"、"网站内容修改"、或提供FTP凭据要求修改网站。
references:
  - references/asp-access-session-example.md
  - references/2026-05-22-yingxin-content-unification.md
  - references/sme-website-audit-checklist.md
  - references/yingxin-cms-backend.md
  - references/dns-troubleshooting.md
templates:
  - templates/asp-update-template.asp
---

# Website Content Editing (网站内容编辑)

> Class-level umbrella covering all approaches to editing content on traditional Chinese SME websites.
> **Supersedes:** `db-website-content-mgmt`, `ftp-static-site-editing`

---

## 1. Diagnosis — What kind of site is it?

Before editing, determine the site architecture. This decides which mode to use:

| Observation | Likely type | Approach |
|-------------|-------------|----------|
| `.asp` + `.mdb` files on server | ASP + Access (database-driven) | **Mode B** — script injection |
| `.php` files, no `.html` | PHP + MySQL (database-driven) | **Mode B** — script injection |
| Only `.html` / `.htm` files | Static flat-file | **Mode A** — direct FTP edit |
| `.asp` files but **no** `.mdb` | ASP flat-file (no DB) | **Mode A** — direct FTP edit |
| Has `/admin/` or CMS login page | CMS backend available | **CMS** — web-based editor |
| URL has `?id=` or `?info=` parameter | Dynamic / database-driven | **Mode B** — script injection |
| `.html` URL but `.asp` template files exist | URL Rewrite (pseudo-static) | **Mode B** — look for DB |

**Quick test:** Check if the site displays dynamic content (product lists, news articles) with similar templates → likely database-driven. If every page is a separate `.html` file → flat-file.

**Approach selection:**
- **Flat-file → Mode A** — Download files via FTP → edit locally → upload back
- **Database-driven → Mode B** — Upload temporary query script → locate data → upload update script → clean up
- **Has CMS backend → CMS approach** — Login to web admin → use built-in editor

> If unsure, start with Mode A (check file system). If content isn't in files, move to Mode B.

---

## 2. Prerequisites (Shared)

### FTP Connection

```bash
# Recommended: use --user for passwords with special chars
curl -sL ftp://hostname/path --user "username:password"

# For listing directory contents
curl -sL ftp://hostname/ --user "user:pass"

# For downloading single file
curl -sL ftp://hostname/wwwroot/file.asp --user "user:pass" -o local/file.asp

# For uploading
curl -sL ftp://hostname/wwwroot/file.asp --user "user:pass" -T local/file.asp
```

**⛔ PASSWORD SPECIAL CHARS:** When the password contains `/ * - % ! @`, always use `--user` flag — never embed in the URL:

```bash
# ❌ WRONG — / in password breaks path parsing
curl ftp://user:pass/with/slashes@host/path

# ✅ RIGHT
curl --user "username:Yx168168/*-" ftp://host/path
```

**🔴 FTP vs HTTP root mismatch:** The FTP login root may differ from the HTTP document root. Always verify:

```bash
# Compare FTP root index.asp vs HTTP root content
curl -sL ftp://host/ --user "user:pass" | grep -c index.asp
curl -sL http://domain.com | head -5
# If they differ → real site is in subdirectory (often /wwwroot/)
```

**🔴 HTTP vs HTTPS:** IIS servers with outdated TLS configs may fail on HTTPS:
```
SSL alert: error:0A000438:SSL routines::tlsv1 alert internal error
```
→ Use `http://` (not `https://`) for curl-based checks on such servers.

### FTP Encoding for Chinese Servers

```python
from ftplib import FTP
ftp = FTP()
ftp.encoding = 'latin-1'      # ✅ Chinese Windows servers
ftp.connect(host, 21, timeout=15)
ftp.login(user, passwd)
ftp.set_pasv(True)
```

### HTTP Verification

```bash
# Check old text is gone
curl -sL http://domain.com | grep -c '旧文字'

# Check new text appeared
curl -sL http://domain.com | grep '新文字'
```

---

## 3. Mode A: Flat-File Editing (FTP Direct Edit)

Use when site content is stored directly in HTML/ASP/PHP files on the filesystem.

### Workflow

**Step 1: Discover which files contain the target string**

```bash
FTP_URL="ftp://host"
for f in file1.asp file2.asp; do
  content=$(curl -sL "$FTP_URL/wwwroot/$f" --user "user:pass" 2>&1)
  if echo "$content" | grep -q "目标文字"; then
    echo "🔴 Found in: $f"
    echo "$content" > "local/$f"
  fi
done
```

**Step 2: Edit locally** — Use `patch()` tool for targeted find-and-replace.

**Step 3: Upload back**

```bash
curl -sL "ftp://host/wwwroot/file.asp" --user "user:pass" -T local/file.asp
```

**Step 4: Verify** — HTTP check as above.

### Common Flat-File Tasks

**JSON-LD / Schema deployment:**
1. Check existing: `curl -s http://domain.com | grep -c 'application/ld+json'`
2. If count > 0: edit existing block in-place (do NOT add a second block)
3. If count == 0: create from template
4. Validate JSON with `python3 -c "import json; json.loads(open('file').read())"`
5. Upload and verify: grep for `application/ld+json` (should be 1)

**Global search-replace (address, phone, company name):**
1. FTP download all candidate files
2. Grep each for old text
3. Edit matching files with `patch()`
4. Upload all changed files
5. Verify each URL

> For bulk operations with many files, download all candidates, grep locally, edit with `patch()`, upload changed files only, then verify each URL.

---

## 4. Mode B: Database-Driven Editing (Script Injection)

Use when content is stored in a database (Access .mdb, MySQL, SQL Server) and you don't have a direct DB client.

### Workflow

**Step 1: Create temporary query script**

Upload a read-only query script that dumps the target table as HTML:

**query.asp** (Access):
```asp
<%@ Language=VBScript %>
<% Option Explicit %>
<%
Dim conn, rs, sql
Set conn = Server.CreateObject("ADODB.Connection")
conn.Open "Provider=Microsoft.Jet.OLEDB.4.0;Data Source=" & Server.MapPath("database.mdb")
sql = "SELECT * FROM a_info ORDER BY a_id"
Set rs = conn.Execute(sql)
Response.Write "<table border='1'><tr>"
For i = 0 To rs.Fields.Count - 1
    Response.Write "<th>" & rs.Fields(i).Name & "</th>"
Next
Response.Write "</tr>"
Do While Not rs.EOF
    Response.Write "<tr>"
    For i = 0 To rs.Fields.Count - 1
        Response.Write "<td>" & Server.HTMLEncode(rs.Fields(i).Value & "") & "</td>"
    Next
    Response.Write "</tr>"
    rs.MoveNext
Loop
Response.Write "</table>"
rs.Close: Set rs = Nothing
conn.Close: Set conn = Nothing
%>
```

**query.php** (MySQL):
```php
<?php
$conn = mysqli_connect('localhost', 'user', 'pass', 'dbname');
if (!$conn) { die('Connection failed: ' . mysqli_connect_error()); }
$sql = "SELECT * FROM pages";
$result = mysqli_query($conn, $sql);
echo "<table>";
while ($row = mysqli_fetch_assoc($result)) {
    echo "<tr><td>" . htmlspecialchars($row['title']) . "</td></tr>";
}
echo "</table>";
mysqli_close($conn);
?>
```

> 💡 **Pro tip:** Check existing ASP files for server-side helper functions like `db_content(table, id)` — these exist in many Chinese CMS builds and are more reliable than raw SQL.

**Step 2: Upload via FTP and access via HTTP**

Upload the `.asp` / `.php` file to the website root. Visit the URL in browser.

**🔴 Progressive query strategy (for HTTP 500 errors):**
1. First: `SELECT id, s_name FROM table ORDER BY id` — simple fields only
2. Locate target row
3. Then: `SELECT * FROM table WHERE id=N` — single row
4. If still 500, add columns one at a time

> **Why:** Access OLEDB on some IIS setups crashes on SQL functions like `LEFT()` / `LEN()` on long text fields. Use raw column names.

**Step 3: Create update script**

Use RecordSet read-modify-write pattern (preferred) for Chinese text:

```asp
<%@LANGUAGE="VBSCRIPT" Codepage="65001"%>
<%
Response.Charset = "utf-8"
Session.CodePage = "65001"
%>
<%
Dim rs, oldC, newC
Set rs = Server.CreateObject("ADODB.RecordSet")
rs.Open "SELECT s_content FROM a_info WHERE id=1", conn, 1, 3   ' 3=Optimistic
If Not rs.EOF Then
    oldC = rs("s_content") & ""
    newC = Replace(oldC, "旧文字", "新文字")
    rs("s_content") = newC
    rs.Update()
    Response.Write "✅ Updated: " & Len(oldC) & " → " & Len(newC)
End If
rs.Close()
%>
```

**Why RecordSet over SQL UPDATE:**
- VBScript `Replace()` handles Chinese encoding reliably
- Supports conditional logic (If/Else per row)
- Can verify-and-rollback via `Err.Number` + `CancelUpdate()`
- Chain multiple `Replace()` calls for multi-target updates

**Step 4: 🔴 CRITICAL — Clean up temporary scripts**

Delete ALL uploaded `.asp`/`.php` files via FTP:
```bash
curl --user "user:pass" ftp://host/wwwroot/ -X DELE query.asp
curl --user "user:pass" ftp://host/wwwroot/ -X DELE update.asp
# List directory to confirm
curl --user "user:pass" ftp://host/wwwroot/
```

**Never leave temporary scripts on the server.** They expose database structure.

### Encoding Safety for ASP with Chinese

**ASP header three-piece set (every file):**
```asp
<%@LANGUAGE="VBSCRIPT" Codepage="65001"%>
<% Response.Charset = "utf-8" %>
<% Session.CodePage = "65001" %>
```

**Upload in binary mode (never text mode):**
```python
# ✅ Correct: binary transfer preserves UTF-8 byte sequences
with open('/tmp/script.asp', 'wb') as f:
    f.write(asp_content.encode('utf-8'))
with open('/tmp/script.asp', 'rb') as f:
    ftp.storbinary('STOR script.asp', f)

# ❌ Wrong: storlines() in text mode breaks multi-byte UTF-8 chars
```

**Common encoding pitfalls:**
| Problem | Cause | Fix |
|---------|-------|-----|
| ASP shows garbled Chinese | Used `storlines()` instead of `storbinary()` | Binary transfer only |
| SQL LIKE with Chinese → HTTP 500 | OLEDB encoding mismatch | Use `WHERE id=N` instead |
| FTP file listing has garbled names | Wrong FTP encoding | Use `latin-1` for Chinese Windows servers |

### Common Database Table Patterns

Sites built on common Chinese CMS systems often follow these conventions:

| Page type | Likely table | Key fields |
|-----------|-------------|------------|
| Homepage / About | `a_info` | `id`, `s_name` (title), `s_content` (HTML body), `s_photo_url` |
| News / Articles | `news` | `title`, `content`, `update_time` |
| Services | `service` | `s_title`, `s_content` |
| Team members | `team` | `s_name`, `s_detail`, `s_photo_url` |
| Certificates | `cert` | `s_name`, `s_photo_url` |

> For detailed patterns and advanced scenarios, refer to the Mode B workflow above (section 4). The template file provides a copy-and-paste starting point.
> **Template:** `templates/asp-update-template.asp` for copy-and-paste usage.

---

## 5. CMS Backend Approach

Some flat-file ASP sites also have a web-based CMS admin panel for content editing without FTP.

### Discovery
- Backend URL patterns: `/admin/`, `/manage/`, `/sz@yxmanage/`
- Login: typically user + password + captcha
- Common layout: left navigation frame + main content area

### FTP vs CMS Decision

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Global search-replace (address/phone) | FTP | Batch download + grep all files |
| JSON-LD / Schema markup | FTP | Requires editing ASP template files directly |
| Site config (name, keywords, copyright) | CMS | Dedicated config page |
| Content pages (About, Services, Contact) | CMS | WYSIWYG editor, no code |
| News / articles / case studies | CMS | Built-in article management |
| URL structure, robots.txt, sitemap | FTP | Flat files, not managed by CMS |

> **Rule of thumb:** Content changes → CMS. Structural changes → FTP.

> **Reference:** `references/yingxin-cms-backend.md` for a complete guide to the yingxinkuaiji.com ASP CMS backend.

---

## 6. Audit Before Editing

Before making changes, run a **site content audit** using the checklist in references:

| Priority | Check | Method |
|----------|-------|--------|
| 🔴 High | Phone/address correct | Compare with latest info from user |
| 🔴 High | Company name/founding year | Compare homepage vs about vs footer |
| 🟡 Medium | Outdated time words ("今年", "去年") | grep for time-sensitive text |
| 🟡 Medium | SSL certificate | Check HTTPS in browser |
| 🟡 Medium | Link validity | Navigation links, certificate images |
| 🟢 Low | Image filename consistency | Check path uniformity |
| 🟢 Low | Text formatting | Visual consistency |

> **Reference:** `references/sme-website-audit-checklist.md` for the full audit protocol and delivery template.

---

## 7. Advanced Add-Ons

### DNS Verification for Domain Ownership

Used when Google Search Console, SSL cert, or other services require TXT record proof.

**Tool (WSL without dig):** Use Windows' nslookup via WSL interop:
```bash
/mnt/c/Windows/System32/nslookup.exe -type=txt DOMAIN 8.8.8.8
```

**🔴 CNAME vs TXT conflict (RFC 1912):** A CNAME record at the domain apex CANNOT coexist with TXT records. This is the #1 reason verification fails silently.

**Solutions:**
1. **HTML file verification** (simplest): Upload Google-provided HTML file to web root
2. **Subdomain verification**: Verify `www.domain.com` instead of root domain
3. **Replace CNAME with A record**: Delete apex CNAME, add A record → TXT records coexist

> **Reference:** `references/dns-troubleshooting.md` for full reproduction steps.

---

## 8. Pitfalls (合并)

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Forgot to delete temp scripts | DB structure exposed to web | Delete immediately after use, list dir to confirm |
| Wrong WHERE condition | Updated wrong rows | SELECT first to confirm row count |
| Wrong database path | Script returns HTTP 500 | Check connection string in existing ASP files |
| Chinese SQL LIKE → HTTP 500 | OLEDB encoding breakdown | Use `WHERE id=N` not LIKE with Chinese |
| FTP text mode for .asp with Chinese | Garbled Chinese text | Use `storbinary()` (binary), never `storlines()` |
| ASP syntax `%%>` from Markdown copy | Page blank / 500 | Replace `%%>` with `%>` in ASP code |
| Cache after update | Changes not visible | Clear browser cache or use incognito mode |
| FTP root ≠ HTTP root | Wrong file edited | Compare FTP root index.asp vs HTTP root content |
| HTTPS curl fails on IIS | TLS alert internal error | Use `http://` instead |
| Multiple JSON-LD blocks | Search engines ignore schema | Maintain exactly ONE `application/ld+json` per page |
| Long text + SQL functions = 500 | `LEFT(s_content,200)` kills page | SELECT raw column name, avoid SQL text functions |

---

## 9. Verification Checklist

After any modification (regardless of mode):

- [ ] Temporary scripts/files fully deleted from server
- [ ] Old string no longer appears on live site (grep count = 0)
- [ ] New string appears correctly on live site (grep confirmed)
- [ ] Page format/HTML not broken
- [ ] Other pages unaffected
- [ ] Images load (if images were changed)
- [ ] FTP password with special chars handled via `--user`

---

## 10. Reference Files

| File | Content |
|------|---------|
| `references/asp-access-session-example.md` | 2026.5 real session — ASP+Access site modification transcript |
| `references/2026-05-22-yingxin-content-unification.md` | Multi-page keyword unification case study on yingxin website |
| `references/sme-website-audit-checklist.md` | Pre-edit content audit checklist and delivery template |
| `references/yingxin-cms-backend.md` | Complete CMS backend operation guide (yingxinkuaiji.com) |
| `references/dns-troubleshooting.md` | DNS verification troubleshooting (CNAME apex conflict) |
| `templates/asp-update-template.asp` | Reusable ASP update script template |

View via: `skill_view(name="website-content-editing", file_path="references/<filename>")`
