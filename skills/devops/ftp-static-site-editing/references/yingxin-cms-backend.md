# 盈信会计网站 CMS 后台操作手册

> **用途：** 记录 yingxinkuaiji.com 的 ASP 网页后台管理系统的结构和操作方式，用于通过 Web 界面（非 FTP）编辑网站内容。
> **关联技能：** `ftp-static-site-editing`（FTP 编辑互补方案）
> **首次记录：** 2026.5.28

---

## 技术参数

| 参数 | 值 |
|:-----|:----|
| 后台入口 | `http://www.yingxinkuaiji.com/sz@yxmanage/` |
| 系统名称 | 盈信会计网站管理系统 |
| 服务器类型 | IIS |
| 脚本引擎 | VBScript/5.8（ASP） |
| 站点路径 | `D:\wwwroot\jsxuaijun\wwwroot\` |

---

## 登录方式

1. 浏览器打开 `http://www.yingxinkuaiji.com/sz@yxmanage/`
2. 输入用户名 + 密码 + 验证码（页面上的图形验证码）
3. 登录表单提交到 `System_chklogin.asp`
4. 登录后进入框架布局页面

> **注意：** 后台有防外链保护（`if (top==self)` 检测），禁止直接输入地址访问，必须通过框架登录。

---

## 后台界面结构

- 左侧导航栏（190px）：`System_menu.asp` — 可折叠菜单
- 主内容区：iframe 加载对应功能页面
- 右上角显示当前用户和身份

---

## 菜单结构

### ① 网站信息配置

| 功能 | URL | 用途 |
|:-----|:----|:-----|
| 栏目管理 | `menu/menu_aclass.asp` | 网站栏目（一级分类）管理 |
| 菜单管理 | `menu/menu_nclass.asp` | 菜单（二级分类）管理 |
| 网站配置 | `public/web_config.asp?show_yuyan=0&show_count=0` | 网站全局设置 |
| 密码修改 | `user/adminpwd.asp` | 修改管理员密码 |
| 友情链接 | `public/FriendSite_list.asp` | 友情链接管理 |

### ② 信息管理系统

| 功能 | 参数 `s_pai` | 内容 |
|:-----|:------------|:-----|
| 关于盈信 | `s_pai=1` | 公司介绍页内容 |
| 盈信业务 | `s_pai=2` | 业务介绍页内容 |
| 右侧联系我们 | `s_pai=3` | 侧边栏/底部的联系信息 |
| 首页简介 | `s_pai=4` | 首页简介区域内容 |

每个分类下支持：
- 列表页：`News/info_list.asp?s_pai=N`
- 编辑内容：通过列表页的编辑链接

### ③ 客户中心管理

| 功能 | URL | 用途 |
|:-----|:----|:-----|
| 文章添加 | `news/news_do.asp?s_pai=1&show_img=1` | 新增客户中心文章 |
| 文章管理 | `news/news_list.asp?s_pai=1&show_hot=1&show_img=1` | 编辑/删除客户中心文章 |
| 分类管理 | `news/Class_list.asp?s_pai=1&show_next=0&show_depth=0&show_del=1` | 管理客户中心分类 |

### ④ 资讯管理系统

| 功能 | URL | 用途 |
|:-----|:----|:-----|
| 文章添加 | `News/news_do.asp?s_pai=0&show_img=1` | 新增资讯文章 |
| 文章管理 | `News/news_list.asp?s_pai=0&show_hot=1&show_img=1` | 编辑/删除资讯文章 |
| 分类管理 | `News/Class_list.asp?s_pai=0&show_next=0&show_depth=0&show_del=1` | 管理资讯分类 |

---

## 使用场景对比：FTP vs CMS 后台

| 场景 | 推荐方式 | 原因 |
|:-----|:---------|:-----|
| 全局搜索替换（如批量改地址） | FTP | 可批量下载全站文件搜索 |
| 添加 JSON-LD 结构化数据 | FTP | 需直接编辑 ASP 模板文件 |
| 修改网站配置（网站名、keywords等） | CMS 后台 | 有配置页面，无需改代码 |
| 编辑「关于盈信」「盈信业务」等页面内容 | CMS 后台 | 可视化管理，有编辑器 |
| 添加/编辑文章（新闻、客户案例） | CMS 后台 | 系统自带文章管理 |
| URL 结构 / robots.txt / sitemap | FTP | 这些不是 CMS 后台管理的范围 |

> **经验法则：** 内容型修改走 CMS 后台，结构性修改走 FTP。

---

## 注意陷阱

- 后台不支持 HTTPS（仅 HTTP）
- 验证码每次登录都需要输入
- 文章编辑器可能是简单文本框（非富文本），HTML 标签需要手动编写
- 后台编辑的内容会直接写入 ASP 文件或数据库文件（需确认存储方式）
- 修改后刷新前台页面即可看到效果，无需重启服务
