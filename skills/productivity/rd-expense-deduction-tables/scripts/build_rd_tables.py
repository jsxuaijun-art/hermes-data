# -*- coding: utf-8 -*-
"""研发费用加计扣除 三张填报模板 — 依据财税〔2015〕119号
用法: python3 build_rd_tables.py [输出目录]
默认输出到用户桌面 <Desktop>/研发费用加计扣除三张调整表.xlsx
"""
import os, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ---- 输出路径 ----
try:
    outdir = sys.argv[1]
except IndexError:
    cands = [d for d in sorted(os.listdir('/mnt/c/Users')) if os.path.isdir('/mnt/c/Users/'+d)]
    desk = None
    for u in cands:
        p = f'/mnt/c/Users/{u}/Desktop'
        if u not in ('Public','Default','Default User','All Users') and os.path.isdir(p):
            desk = p; break
    if not desk:
        desk = '/tmp'
    outdir = desk
out = os.path.join(outdir, '研发费用加计扣除三张调整表.xlsx')

wb = Workbook()

# ---------- 样式 ----------
TITLE_FONT = Font(name='微软雅黑', size=14, bold=True, color='FFFFFF')
HEAD_FONT  = Font(name='微软雅黑', size=10, bold=True, color='FFFFFF')
HEAD_FILL  = PatternFill('solid', fgColor='2F5496')
SUB_FONT   = Font(name='微软雅黑', size=10, bold=True, color='2F5496')
SUB_FILL   = PatternFill('solid', fgColor='D9E2F3')
BODY_FONT  = Font(name='微软雅黑', size=10)
RED_FONT   = Font(name='微软雅黑', size=10, bold=True, color='C00000')
RED_FILL   = PatternFill('solid', fgColor='FBE4E4')
thin = Side(style='thin', color='BFBFBF')
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
CENTER = Alignment(horizontal='center', vertical='center', wrap_text=True)
LEFT   = Alignment(horizontal='left',  vertical='center', wrap_text=True)

def style_row(ws, row, ncol, font=None, fill=None, left_cols=()):
    for c in range(1, ncol+1):
        cell = ws.cell(row=row, column=c)
        cell.font = font or BODY_FONT
        cell.border = BORDER
        cell.alignment = LEFT if c in left_cols else CENTER
        if fill: cell.fill = fill

def header(ws, ncol, title, subs):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncol)
    t = ws.cell(1,1,title); t.font=TITLE_FONT; t.fill=HEAD_FILL; t.alignment=CENTER
    ws.row_dimensions[1].height = 36
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=ncol)
    c2=ws.cell(2,1,subs[0]); c2.font=Font(name='微软雅黑',size=9,color='595959'); c2.alignment=LEFT
    ws.merge_cells(start_row=3, start_column=1, end_row=3, end_column=ncol)
    c3=ws.cell(3,1,subs[1]); c3.font=Font(name='微软雅黑',size=9,color='7F7F7F'); c3.alignment=LEFT
    return 4

def table_head(ws, row, headers):
    for i,h in enumerate(headers,1): ws.cell(row,i,h)
    ws.row_dimensions[row].height = 30
    style_row(ws, row, len(headers), font=HEAD_FONT, fill=HEAD_FILL)
    return row+1

def set_widths(ws, widths):
    for i,w in enumerate(widths,1): ws.column_dimensions[get_column_letter(i)].width = w

# ===== 表一：两口径差异调整明细表 =====
ws1 = wb.active; ws1.title = '表一 两口径差异明细表'
n1 = 8
set_widths(ws1, [6,22,12,12,13,13,32,36])
r = header(ws1, n1, '研发费用：加计扣除口径 vs 高新认定口径 差异调整明细表', [
    '填报范围：会计核算口径→高新技术企业认定口径→研发费用加计扣除口径，三档差异归集（单位：元）',
    '依据：财税〔2015〕119号 / 国家税务总局公告2015年第97号 / 2017年第40号；本表用于存在两口径差异的项目填报'])
hrow = table_head(ws1, r, ['序号','费用项目','差异类别','加计扣除口径','高新认定口径','差异额(加计-高新)','调整说明','政策依据'])

rows1 = [
 ('一、人员人工费用','HEAD','','','','','',''),
 (1,'专职研发人员工资薪金、五险一金、住房公积金','无差异','全额计入','全额计入',0,'专门从事研发活动的人员，其工资薪金、社保、公积金全额计入，两口径一致。','财税〔2015〕119号 第一条第(一)项'),
 (2,'同时从事非研发活动人员(兼岗)','口径差异','按研发工时占比计入','按实际工时占比计入',None,'在研发与非研发活动间按实际工时/工作量分配，只计入对应研发部分；需留存工时记录备查。','财税〔2015〕119号 / 97号公告第二条'),
 (3,'外聘研发人员劳务费(劳务派遣)','无差异','可计入','可计入',0,'企业支付给外聘研发人员的劳务费用，两口径均可计入。','97号公告第一条第(一)项 / 40号公告第十四条'),
 (4,'补充养老、补充医疗保险','口径差异','可加计','按研发人员部分计入',None,'为专门从事研发人员缴纳的补充保险两口径计入；其余人员部分加计口径剔除。','97号公告第一条第(一)项'),
 (5,'纯管理、后勤等非研发部门人员费用','口径差异','不得计入(剔除)','按规定比例计入',None,'加计扣除口径严格剔除纯管理/后勤人员；高新口径可视企业规范按规定比例计入。','财税〔2015〕119号 第一条第(一)项第5目 / 国科发火〔2016〕195号'),
 ('二、直接投入费用','HEAD','','','','','',''),
 (6,'研发活动直接消耗的材料、燃料、动力','无差异','可加计','可计入',0,'直接用于研发活动所耗用的材料、燃料和动力费用计入；若形成产品对外销售本项转下。','财税〔2015〕119号 第一条第(二)项'),
 (7,'研发领用材料形成产品销售部分','口径差异','不得计入(冲减)','计入直接投入',None,'研发形成产品/组成部分对外销售的，相应材料费不得加计，应从事先已计入的直接投入中转出或冲减。','财税〔2015〕119号第六条 / 40号公告第八条'),
 (8,'测试仪器、设备、模具、样品样机购置','无差异','可加计','可计入',0,'用于研发的仪器/设备/模具/样品样机购置费计入。','财税〔2015〕119号 第一条第(二)项'),
 (9,'研发仪器设备经营租赁费','无差异','可加计','可计入',0,'经营租赁的研发用设备租金计入。','财税〔2015〕119号 第一条第(二)项'),
 ('三、折旧与摊销','HEAD','','','','','',''),
 (10,'研发用专用仪器设备折旧','无差异','可加计','可计入',0,'专门用于研发的仪器、设备折旧；双用途按实际工时比例分摊。','财税〔2015〕119号 第一条第(三)项'),
 (11,'研发用无形资产摊销','无差异','可加计','可计入',0,'用于研发的软件、专利权、非专利技术摊销计入。','财税〔2015〕119号 第一条第(四)项'),
 ('四、其他相关费用','HEAD','','','','','',''),
 (12,'与研发直接相关的差旅费、会议费、资料等','口径差异','限10%上限','可计入',None,'加计扣除口径：其他相关费用合计不得超过可加计研发费用总额的10%；高新口径上限较宽。','财税〔2015〕119号 第一条第(五)项 / 40号公告第六条'),
 ('五、特殊收入与产品销售的冲减','HEAD','','','','','',''),
 (13,'下脚料、残次品、中间试制品等特殊收入','加计特有','冲减当年度可加计研发费用','不冲减',None,'研发过程中形成的下脚料、残次品、中间试制品等取得特殊收入，应冲减当年度可加计扣除的研发费用。','财税〔2015〕119号第六条 / 40号公告第七条'),
 (14,'研发形成产品或组成部分销售','加计特有','对应材料费不得加计','计入直接投入',None,'研发形成的产品整体或组成部分对外销售的，对应的材料费用不得加计扣除。','财税〔2015〕119号第六条 / 40号公告第八条'),
]
for item in rows1:
    if item[1]=='HEAD':
        ws1.merge_cells(start_row=hrow,start_column=1,end_row=hrow,end_column=n1)
        c=ws1.cell(hrow,1,item[0]); c.font=SUB_FONT; c.fill=SUB_FILL; c.alignment=LEFT; c.border=BORDER
        for col in range(2,n1+1): ws1.cell(hrow,col).border=BORDER; ws1.cell(hrow,col).fill=SUB_FILL
        hrow+=1; continue
    seq,proj,cat,jk,gx,diff,note,base = item
    vals=[seq,proj,cat,jk,gx,'' if diff is None else diff,note,base]
    for col,v in enumerate(vals,1): ws1.cell(hrow,col,v)
    style_row(ws1,hrow,n1,left_cols=(2,7,8)); ws1.cell(hrow,3).alignment=CENTER
    if cat in ('口径差异','加计特有'):
        wd=ws1.cell(hrow,3); wd.font=RED_FONT; wd.fill=RED_FILL
    for col in (4,5,6): ws1.cell(hrow,col).number_format='#,##0.00'
    hrow+=1
ws1.merge_cells(start_row=hrow,start_column=1,end_row=hrow,end_column=5)
c=ws1.cell(hrow,1,'差异合计（加计口径调整后 = 加计口径±差异）'); c.font=HEAD_FONT; c.fill=HEAD_FILL; c.alignment=LEFT; c.border=BORDER
for col in range(2,n1+1): ws1.cell(hrow,col).fill=HEAD_FILL; ws1.cell(hrow,col).font=HEAD_FONT; ws1.cell(hrow,col).border=BORDER
ws1.cell(hrow,6,'=∑差异额').font=HEAD_FONT

# ===== 表二：产品销售冲减明细表 =====
ws2 = wb.create_sheet('表二 产品销售冲减明细')
n2 = 11
set_widths(ws2, [6,10,16,16,10,13,18,11,15,16,28])
r2 = header(ws2, n2, '研发领用材料形成产品／下脚料销售 冲减研发费用明细表', [
    '填报范围：研发领用材料后形成产品整件/组成部分对外销售，以及形成下脚料、残次品、中间试制品取得收入的部分（单位：元）',
    '依据：财税〔2015〕119号第六条；国家税务总局公告2017年第40号第七、八条'])
h2 = table_head(ws2, r2, ['序号','所属月份','研发项目名称','领用材料品名','领用数量','领用金额','形成产品/特殊产出','销售数量','对应材料成本','特殊收入(下脚料等)','备注'])

SAMPLE = [
 ['2025-01','高精度传感器研发','铝合金壳体',500,25000,'传感器(组成部分)',200,10000,'','产品组成部分销售→该部分材料费不得加计'],
 ['2025-02','高精度传感器研发','感光芯片',300,60000,'传感器(中间试制品)',50,10000,8000,'中间试制品销售收入冲减当年度可加计研发费用'],
 ['2025-03','节能电机优化','铜线',120,38000,'下脚料(边角料)','','',3200,'下脚料收入冲减当年度可加计研发费用'],
 ['2025-04','新能源控制器测试','PCB基板',400,28000,'残次品',0,0,15000,'残次品对外销售取得收入冲减'],
 ['2025-05','高精度传感器研发','封装材料',250,12000,'产品(组成部分)',100,4800,3600,'部分件销售材料成本+残次品收入并冲减'],
]
data_start = h2
for seq,row in enumerate(SAMPLE,1):
    vals=[seq]+row
    for col,v in enumerate(vals,1): ws2.cell(h2,col,v)
    style_row(ws2,h2,n2,left_cols=(3,4,7,11))
    for col in (6,9,10): ws2.cell(h2,col).number_format='#,##0.00'
    h2+=1
data_end = h2-1
for lab,col,letter in [
    ('① 合计——销售产品的对应材料成本（不得加计，转入表一第7项）',9,'I'),
    ('② 合计——特殊收入（下脚料/残次品/中间试制品，冲减当年度可加计研发费用，转入表一第13项）',10,'J')]:
    ws2.merge_cells(start_row=h2,start_column=1,end_row=h2,end_column=8)
    c=ws2.cell(h2,1,lab); c.font=HEAD_FONT; c.fill=HEAD_FILL; c.alignment=LEFT; c.border=BORDER
    for cc in range(2,9): ws2.cell(h2,cc).fill=HEAD_FILL; ws2.cell(h2,cc).font=HEAD_FONT; ws2.cell(h2,cc).border=BORDER
    f=ws2.cell(h2,col,f'=SUM({letter}{data_start}:{letter}{data_end})'); f.font=HEAD_FONT; f.number_format='#,##0.00'
    ws2.cell(h2,11).font=HEAD_FONT; ws2.cell(h2,11).fill=HEAD_FILL; ws2.cell(h2,11).border=BORDER
    h2+=1

# ===== 表三：人员工时及人工费用调整表 =====
ws3 = wb.create_sheet('表三 人员工时及人工费用')
n3 = 13
set_widths(ws3, [6,10,18,11,12,12,12,11,13,13,13,13,28])
r3 = header(ws3, n3, '研发人员工时分配及人工费用调整表', [
    '填报范围：全部从事研发活动人员(专职、兼岗、外聘劳务派遣分别列示)；工时单位=小时，金额单位=元',
    '依据：财税〔2015〕119号第一条第(一)项；97号公告第二条(同时从事非研发活动按实际工时分配)；2017年40号公告'])
h3 = table_head(ws3, r3, ['序号','姓名','岗位/职务','是否专职研发','全年总工时','其中：研发工时','其中：非研发工时','研发工时占比','全年工资薪金','全年社保及公积金','其他人工费用','可加计扣除人工费','备注'])

PE = [
 ('张某某','研发工程师','是',2080,2080,0,'',180000,27000,5000,'','专职研发人员，全额计入'),
 ('李某某','研发工程师','是',2080,2080,0,'',165000,25000,4000,'','专职研发人员，全额计入'),
 ('王某某','结构设计(兼岗)','否',2080,1200,880,'',150000,22000,3000,'','兼非研发，按实际工时分配'),
 ('赵某某','实验室技工','否',2080,1600,480,'',96000,14000,2000,'','兼非研发，按实际工时分配'),
 ('孙某某','外聘(劳务派遣)','否',2080,1000,1080,'',60000,0,0,'','仅按研发工时计入劳务费'),
 ('周某某','研发部门经理','否',2080,1500,580,'',200000,28000,6000,'','兼管理与研发，按工时分配'),
 ('吴某某','纯管理/后勤','否',2080,0,2080,'',80000,11000,1000,'','加计口径剔除；高新口径按比例可计入'),
]
p_start = h3
for seq,(name,post,sp,total,rd,nrd,pct,sal,soc,oth,ded,note) in enumerate(PE,1):
    vals=[seq,name,post,sp,total,rd,nrd,pct,sal,soc,oth,ded,note]
    for col,v in enumerate(vals,1): ws3.cell(h3,col,v)
    style_row(ws3,h3,n3,left_cols=(3,13))
    ws3.cell(h3,8,f'=F{h3}/E{h3}').number_format='0.0%'
    ws3.cell(h3,12,f'=SUM(I{h3}:K{h3})*H{h3}').number_format='#,##0.00'
    for col in (5,6,7,9,10,11): ws3.cell(h3,col).number_format='#,##0'
    if sp=='否': ws3.cell(h3,4).fill=RED_FILL
    h3+=1
p_end = h3-1
ws3.merge_cells(start_row=h3,start_column=1,end_row=h3,end_column=4)
c=ws3.cell(h3,1,'合计'); c.font=HEAD_FONT; c.fill=HEAD_FILL; c.alignment=CENTER; c.border=BORDER
for col in range(2,n3+1): ws3.cell(h3,col).fill=HEAD_FILL; ws3.cell(h3,col).font=HEAD_FONT; ws3.cell(h3,col).border=BORDER
for col,letter in [(5,'E'),(6,'F'),(7,'G'),(9,'I'),(10,'J'),(11,'K'),(12,'L')]:
    f=ws3.cell(h3,col,f'=SUM({letter}{p_start}:{letter}{p_end})'); f.font=HEAD_FONT; f.number_format='#,##0' if col!=12 else '#,##0.00'

for ws in (ws1,ws2,ws3): ws.freeze_panes='A4'
wb.save(out)
print('已生成:', out)
print('表一 行数:', ws1.max_row, '| 表二 行数:', ws2.max_row, '| 表三 行数:', ws3.max_row)
