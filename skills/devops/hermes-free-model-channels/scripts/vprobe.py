#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""视觉能力探针：给指定 provider/model 发一张"已知内容"的图，看它能否正确读出。

用法:
  python3 vprobe.py <图片> <base_url> <KEY的.env变量名> <model>
例:
  python3 vprobe.py /tmp/vtest.png https://aigw.telecomjs.com/v1 TELECOM_DOUBAO_KEY Doubao-Seed-2.1-Pro

判断标准: 图里写的是随机码(如 QX7-7271-BLUE)。模型读对 = 真支持视觉;
读错/报 400 "does not accept input types: image" = 不支持。
注意: 不要用"能描述图"当通过标准 —— 弱模型会顺着提示词编,必须用不可猜的随机内容。

生成测试图:
  python3 -c "
from PIL import Image,ImageDraw,ImageFont
import random
code='QX7-%d-%s'%(random.randint(1000,9999),random.choice(['BLUE','GREEN','ORANGE']))
im=Image.new('RGB',(560,220),'white');d=ImageDraw.Draw(im)
d.rectangle([8,8,552,212],outline='blue',width=8)
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',46)
d.text((35,80),code,fill='black',font=f);d.ellipse([430,60,540,170],fill='blue')
im.save('/tmp/vtest.png');print('CODE=',code)"
"""
import base64
import json
import os
import sys
import urllib.error
import urllib.request

IMG = sys.argv[1]
BASE = sys.argv[2]
KEYENV = sys.argv[3]
MODEL = sys.argv[4]

key = os.environ.get(KEYENV)
if not key:
    envp = os.path.expanduser('~/.hermes/.env')
    if os.path.exists(envp):
        for line in open(envp, encoding='utf-8', errors='ignore'):
            if line.strip().startswith(KEYENV + '='):
                key = line.split('=', 1)[1].strip().strip('"').strip("'")
                break
if not key:
    print('ERR no key for', KEYENV)
    sys.exit(2)

b64 = base64.b64encode(open(IMG, 'rb').read()).decode()
payload = {
    'model': MODEL,
    'max_tokens': 300,
    'messages': [{
        'role': 'user',
        'content': [
            {'type': 'text', 'text': '请读出图中的英文和数字（原样），并说出边框颜色。'},
            {'type': 'image_url', 'image_url': {'url': 'data:image/png;base64,' + b64}},
        ],
    }],
}
req = urllib.request.Request(
    BASE.rstrip('/') + '/chat/completions',
    data=json.dumps(payload).encode(),
    headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key},
)
try:
    with urllib.request.urlopen(req, timeout=180) as r:
        body = r.read().decode()
except urllib.error.HTTPError as e:
    print('HTTP', e.code, e.read().decode()[:300])
    sys.exit(1)
except Exception as e:
    print('ERR', type(e).__name__, e)
    sys.exit(1)

try:
    d = json.loads(body)
    print('OK', MODEL)
    print('ANSWER:', d['choices'][0]['message']['content'][:400])
except Exception:
    print('RAW:', body[:400])
