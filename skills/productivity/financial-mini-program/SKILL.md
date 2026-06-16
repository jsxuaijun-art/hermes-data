---
name: financial-mini-program
description: "Build WeChat mini-programs for tax/financial calculation tools — Chinese IIT calculator, corporate tax tools, salary estimators. Covers project structure, tax logic, UI patterns, and icon fallback."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [wechat, mini-program, tax, chinese-tax, iit, calculator]
    related_skills: [short-video-ad, short-video-industry-flow]
---

# Financial Mini-Program Development

Build complete WeChat mini-programs for tax/financial calculation. Covers 2026 Chinese Individual Income Tax (IIT) rates, mini-program architecture, and rapid development patterns.

## When to Use

- User asks for a WeChat mini-program for tax/accounting calculation
- User wants to build a tax calculator tool for their clients
- User says "帮我写一个计算XXX的小程序" (financial/tax related)
- User says "做个税计算器" / "微信小程序"

## Workflow

### Step 1: Confirm the Tax/Financial Rules

Always start by verifying the latest rates — don't assume from memory. For Chinese IIT:

1. **Search** for the latest tax rate table (confirm current year rates)
2. **Extract** from authoritative sources (税务总局/财政部官网优先)
3. **Confirm** 7-level progressive rate brackets + 速算扣除数
4. **Document** the formula explicitly

**Key formulas to implement:**
- `calcAnnualTax()` — annual settlement
- `calcMonthlyTax()` — monthly cumulative withholding
- `calcYearlySimulation()` — full 12-month simulation
- `calcBonusTax()` — year-end bonus standalone tax

### Step 2: Create Project Structure

```
项目名称/
├── app.json              # global config + tabBar
├── app.js                # app logic
├── app.wxss              # global styles
├── sitemap.json          # search config
├── images/
│   ├── tab_xxx.png
│   └── tab_xxx_active.png
├── utils/
│   └── taxCalc.js        # core calculation module
└── pages/
    ├── index/            # home (nav cards + quick trial)
    ├── calculator/       # monthly cumulative withholding
    ├── yearly/           # annual settlement
    ├── bonus/            # year-end bonus comparison
    └── taxrate/          # rate table quick reference
```

**Per-page file structure:**
```
pages/xxx/
├── xxx.wxml   # template
├── xxx.wxss   # styles
├── xxx.js     # logic
└── xxx.json   # page config
```

### Step 3: Build the Utility Module

Core calculation logic goes in `utils/taxCalc.js` as an independent module:

```javascript
// 7-level progressive tax table
const TAX_TABLE = [
  { min: 0, max: 36000, rate: 0.03, quickDeduction: 0 },
  { min: 36000, max: 144000, rate: 0.10, quickDeduction: 2520 },
  { min: 144000, max: 300000, rate: 0.20, quickDeduction: 16920 },
  { min: 300000, max: 420000, rate: 0.25, quickDeduction: 31920 },
  { min: 420000, max: 660000, rate: 0.30, quickDeduction: 52920 },
  { min: 660000, max: 960000, rate: 0.35, quickDeduction: 85920 },
  { min: 960000, max: Infinity, rate: 0.45, quickDeduction: 181920 },
]

function getTaxBracket(taxableIncome) { ... }
function calcAnnualTax(args) { ... }
function calcMonthlyTax(args) { ... }
function calcYearlySimulation(salaries, socials, specials, others) { ... }
function calcBonusTax(bonus) { ... }

module.exports = { TAX_TABLE, getTaxBracket, calcAnnualTax, calcMonthlyTax, calcYearlySimulation, calcBonusTax }
```

### Step 4: Design UI Patterns

**Tab bar layout:**
- Tab 1: 计算 (calculator entry)
- Tab 2: 税率表

**Card-based layout for data input:**
- Card with emoji + title
- Form rows (label + input/picker)
- Quick-fill example tags (10K, 15K, 25K, 50K)
- Calculate button (emerald green theme #1a6b4c)
- Result card with prominent number display

**Key UI components:**
- 专项附加扣除 selector (toggle checklist)
- Monthly trend table (header + data rows)
- Scheme comparison cards (side-by-side or VS layout)
- Quick-fill tags for one-tap input
- Month slider for year progression

### Step 5: Generate Tab Bar Icons (Fallback)

When `image_generate` tool is unavailable (balance exhausted), generate simple PNG icons using pure Python:

```python
import struct, zlib

def create_solid_png(width, height, r, g, b, a=255):
    def write_chunk(chunk_type, data):
        chunk = chunk_type + data
        return struct.pack('>I', len(data)) + chunk + struct.pack('>I', zlib.crc32(chunk) & 0xffffffff)
    
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    ihdr = write_chunk(b'IHDR', ihdr_data)
    
    raw_data = b''
    for y in range(height):
        raw_data += b'\x00'
        for x in range(width):
            raw_data += struct.pack('BBBB', r, g, b, a)
    
    idat = write_chunk(b'IDAT', zlib.compress(raw_data))
    iend = write_chunk(b'IEND', b'')
    return sig + ihdr + idat + iend
```

## Common Pitfalls

### Mini-Program Specific

1. **WXML condition syntax**: Use `==` not `=`
   - Correct: `wx:if="{{activeTab=='annual'}}"`
   - Wrong: `wx:if="{{activeTab='annual'}}"` (assignment, not comparison)

2. **Tab bar icons required**: Must be real image files. Cannot use emoji or text in tab icons.

3. **Picker bindchange**: `bindchange` event returns `e.detail.value` as 0-based index. Convert: `monthCount = parseInt(e.detail.value) + 1`

4. **onLoad receives options**: Page `onLoad(options)` receives query params from navigation. Use for "quick calc" redirect.

5. **Page methods**: Helper methods must be inside `Page({...})`, not outside as globals.

### Tax Logic

1. **年终奖单独计税**: Use monthly table for rate lookup (bonus/12), but calculate tax using FULL bonus: bonus * rate - quickDeduction.

2. **速算扣除数** is annual-level even for monthly cumulative calculations.

3. **起征点**: 5000元/月 = 60,000元/年.

4. **7项专项附加扣除**: 子女教育(1000/月), 继续教育(400/月), 大病医疗(据实), 房贷利息(1000/月), 住房租金(800-1500/月), 赡养老人(2000/月), 婴幼儿照护(1000/月).

## Verification Checklist

- [ ] Test with known values (e.g., 月薪15,000, 社保3,000, 专项附加4,000 -> 1月个税84元)
- [ ] Verify tab bar navigation between all pages
- [ ] Check input -> calc -> reset flow on each page
- [ ] Test quick-fill example tags work
- [ ] Verify bonus scheme comparison shows both options clearly
- [ ] Check branding footer displays correctly

## Branding

For user's clients, always include:
```
苏州盈信企业管理 出品
```
in the page footer. This is a natural lead generation channel — clients use the tool and see the branding.
