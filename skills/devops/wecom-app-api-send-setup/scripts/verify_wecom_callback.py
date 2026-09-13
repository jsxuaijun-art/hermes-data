#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""端到端验证企微「接收消息」回调 URL 是否验签通过（无需控制台）。
用法: python verify_wecom_callback.py <TOKEN> <AES_KEY> <CORP_ID> <URL>
构造企业微信「安全模式」的一次真实 GET 验签请求；响应 body == 明文 echostr 即通过。
依赖: pip install wechatpy requests   (需在装有 wechatpy 的 venv 里跑)
"""
import sys, hashlib, time, base64, requests
from wechatpy.enterprise.crypto import PrpCrypto

def main():
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(2)
    TOKEN, AES, CORP, URL = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

    echostr = 'verify_test_ec7f9a_' + str(int(time.time()) * 1000 % 10**9)

    # 1) AES 加密 echostr（安全模式 GET 的 echostr 是密文）。key 须先 base64 解码成 bytes！
    key = base64.b64decode(AES + '=')
    pc = PrpCrypto(key)
    encrypted = pc.encrypt(echostr, CORP)
    if isinstance(encrypted, bytes):
        encrypted = encrypted.decode()  # 参与排序/签名前要转 str

    # 2) msg_signature = sha1( sort(token,timestamp,nonce,encrypted) )
    timestamp = str(int(time.time()))
    nonce = 'wx_verify_nonce'
    signature = hashlib.sha1(
        ''.join(sorted([TOKEN, timestamp, nonce, encrypted])).encode()
    ).hexdigest()

    # 3) 打真实回调 URL
    r = requests.get(URL, params={
        'msg_signature': signature,
        'timestamp': timestamp,
        'nonce': nonce,
        'echostr': encrypted,
    }, timeout=15, verify=False)

    ok = (r.text == echostr)
    print(f"HTTP {r.status_code} | len={len(r.text)} | MATCH={ok}")
    if ok:
        print("URL 验证通过：可回控制台点[保存]")
    else:
        print("验签未通过，回包前60字符:", r.text[:60])
        sys.exit(1)

if __name__ == '__main__':
    main()
