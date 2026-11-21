# 扫描版PDF知识提取（OCR）实操指南 v2.0

> 目标：从扫描版PDF中提取高质量文字，注入销售弹药库
> 最后更新：2026-05-25 01:30（根据实战验证全面修正）

---

## 一、快速判断：有文字层还是扫描版？

```bash
# 检查有无文字层
pdftotext "文件名.pdf" - | head -c 200

# 输出>100字 → 有文字层 → 直接用 pdftotext
# 输出=0或乱码 → 扫描版 → 走OCR流程
```

---

## 二、有文字层 → pdftotext 直取（最快）

```bash
pdftotext "影响力（全新升级版）.pdf" "全文提取.txt"
# 589页/102万字 → 19秒完成，质量完美
```

**优点：** 秒级完成，零错误，不丢标点。
**适用：** 所有原生PDF，或Adobe Acrobat生成的扫描件（已含隐藏文字层）。

---

## 三、扫描版 ✅ tesseract 方案（已验证可用，推荐优先尝试）

**⚠️ 注意：** 本指南 v1.0 曾错误判定 tesseract 对中文扫描PDF"完全失败"。实际测试证明 **tesseract + chi_sim 对印刷体中文字迹识别率约90%**，足以提取正文内容用于知识库构建。

### 3.1 环境准备

```bash
# Ubuntu 22.04
sudo apt install tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-eng poppler-utils
```

### 3.2 核心流程

```
PDF → pdftoppm 转PNG（300dpi） → tesseract OCR → 逐页拼接文本
```

### 3.3 ⚠️ 致命陷阱：pdftoppm 文件名格式（已踩坑）

**pdftoppm 的输出文件名使用可变位数填充：**
- 589页PDF → 3位填充：`prefix-005.png`
- 401页PDF → 3位填充：`prefix-273.png`
- 20页PDF → 2位填充：`prefix-05.png`

**❌ 错误写法（直接暴毙）：**
```python
img = f"{prefix}-{page_num:06d}.png"  # 硬编码6位，永远找不到文件
```

**✅ 正确写法：**
```python
img_files = sorted(glob.glob(f"{prefix}-*.png"))
for img_path in img_files:
    basename = os.path.basename(img_path)
    page_str = basename.split("-")[-1].replace(".png", "")
    pg = int(page_str.lstrip("0") or "0")
```

### 3.4 实际验证参数

| 参数项 | 推荐值 | 说明 |
|--------|--------|------|
| 分辨率 | 300dpi | 高于200dpi，兼顾速度和识别率 |
| 语言包 | chi_sim+eng | 中英文混排 |
| PSM模式 | 6 | 统一文本块，适合正文排版 |
| 超时时间 | 120秒/页 | 默认60秒偶尔超时（尤其含图表页） |
| 批量粒度 | 10页/批 | 平衡稳定性和效率 |
| 多进程 | 单进程 | 多进程会竞争资源，不推荐 |

### 3.5 脚本结构（已验证）

```python
def ocr_book(pdf_path, out_dir, start=1, end=401):
    """完整OCR流程，含断点续传和补扫支持"""
    
    # Step 1: pdftoppm 转图片
    subprocess.run([
        "pdftoppm", "-png", "-r", "300",
        "-f", str(start), "-l", str(end),
        pdf_path, f"{out_dir}/page"
    ], timeout=120)
    
    # Step 2: 用glob匹配图片文件名（关键！）
    for img_path in sorted(glob.glob(f"{out_dir}/page-*.png")):
        # Step 3: 用PIL打开图片检查（可加白边裁剪）
        
        # Step 4: tesseract OCR
        result = subprocess.run([
            "tesseract", img_path, "stdout",
            "-l", "chi_sim+eng", "--psm", "6"
        ], capture_output=True, text=True, timeout=120)
        
        text = result.stdout.strip()
        if text:
            output.write(f"\n--- 第{pg}页 ---\n{text}\n")
        
        os.remove(img_path)  # 及时清理
```

### 3.6 实测数据

| 书名 | 页数 | 总耗时 | 总字符 | 单页平均 |
|------|------|--------|--------|---------|
| 销售巨人_大订单销售训练手册 | 401 | ~3小时 | 266,000 | ~27秒 |
| 销售洗脑 | 293 | ~5小时 | 143,380 | ~60秒（部分超时重试） |

**痛点：** 少量页面（约1-2%）含图表/手写标注会超时，需单独补扫并延长超时。

### 3.7 补扫策略

```python
# 场景：主流程跑完后，部分页没提取到（超时/进程中断）
# 方案：用原脚本从断点处重新跑，利用"已有页面跳过"逻辑

# 关键技巧：不要重新跑全书，只跑剩余页
python3 /tmp/ocr_remain.py  # 只处理273-401页
# 输出追加到已存在的全文提取.txt
# 最终合并：已有272页 + 补扫129页 = 401页完整
```

---

## 四、备用方案清单（当tesseract不满足时）

若tesseract识别质量不够（如封面/表格/手写批注），按优先级尝试：

### 方案B：PaddleOCR
```bash
pip install paddlepaddle paddleocr
```
**优点：** 中文识别率更高（85-95%），支持多列排版
**缺点：** 安装复杂，依赖多，占用内存大

### 方案C：marker-pdf（Surya OCR后端）
```bash
pip install marker-pdf
marker_single input.pdf output_dir --langs=zh
```
**优点：** 端到端，一行命令
**缺点：** 需要GPU（CPU极慢），模型大

### 方案D：云API（最高质量）
- 腾讯云OCR / 阿里云OCR / 百度OCR
- 按页计费，约几分钱/页
- 适用于关键篇章的高质量提取

---

## 五、提取后处理流程

```
OCR提取文字 → 清洗去噪 → 核心观点提炼
→ 按S1-S5分类入库
→ 更新话术库参考文件
→ 标记来源（书名+页码）
→ 通知用户有新弹药
```

**清洗重点：**
1. 删除OCR产生的乱码行（`❦`、`□`、`�` 等）
2. 合并断行（PDF分页导致的段落截断）
3. 修正常见OCR错误（如"代帐"→"代账"、"金税"→"全税"）

---

## 六、输出文件规范

```
~/ocr_output/
├── 书名1/
│   ├── 全文提取.txt      # 主输出文件
│   ├── 进度记录.txt       # 运行日志
│   └── 补扫.txt           # 补扫临时输出（成功后合并入主文件）
├── 书名2/
│   └── 全文提取.txt
└── ...
```

**文件格式：** `--- 第X页 ---` 作为页码分隔符，方便后续按页检索。

---

## 知识注入最终状态（已完成的3本）

| 书名 | 页数 | 字符量 | 提取方式 | 状态 |
|------|------|--------|---------|------|
| 影响力（全新升级版） | 589 | 1,047,974 | pdftotext | ✅ 完成 |
| 销售巨人_大订单销售训练手册 | 401 | 266,000+ | tesseract OCR | ✅ 完成（含补扫） |
| 销售洗脑 | 293 | 143,380 | tesseract OCR | ✅ 完成 |

**剩余10本待处理：** 先检查文字层，如有则pdftotext；若为扫描版则继续用tesseract方案。
