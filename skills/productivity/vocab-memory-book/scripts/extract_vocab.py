# -*- coding: utf-8 -*-
"""基于词频筛选提取考试词汇（中考/高考/四级等）"""
import re

def extract_by_frequency(freq_path, vocab_path, top_n=1800, output_path='/tmp/vocab_extracted.txt', label='考试词汇'):
    """从源词库中按词频提取 top_n 个最常用词。"""
    # 1. 加载词频数据
    freq = {}
    with open(freq_path, 'r') as f:
        for l in f:
            l = l.strip()
            if not l: continue
            parts = l.split(None, 1)
            if len(parts) == 2:
                freq[parts[0].lower()] = int(parts[1])
    
    # 2. 按词频排序取 top_n
    sorted_w = sorted(freq.items(), key=lambda x: -x[1])
    top = [w for w,f in sorted_w if w.isalpha() and len(w)>1][:top_n]
    
    # 3. 加载词汇源文件，建立查找表
    with open(vocab_path, 'r', errors='replace') as f:
        lines = f.read().strip().split('\n')
    # 跳过表头行（通常前2-3行是标题）
    start = 0
    for i, l in enumerate(lines):
        m = re.match(r'[a-zA-Z\-\(\)]+\s', l)
        if m and i > 0:  # 找到第一个单词行
            start = i
            break
    
    vocab = {}
    for l in lines[start:]:
        m = re.match(r'([a-zA-Z\-\(\)]+)\s', l)
        if m:
            w = m.group(1).lower().rstrip(',)')
            vocab[w] = l
    
    # 4. 取交集
    common = [w for w in top if w in vocab]
    print(f"Extracted {len(common)} words from top {top_n}")
    
    # 5. 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f'{label}表（{len(common)}词）\n')
        f.write('基于词频筛选\n')
        f.write('='*60 + '\n\n')
        for w in common:
            f.write(vocab[w] + '\n')
    
    return output_path

if __name__ == '__main__':
    extract_by_frequency(
        freq_path='en_50k.txt',
        vocab_path='/mnt/c/Users/Admin/Desktop/高考英语词汇表3817词.txt',
        top_n=1800,
        label='苏州中考英语词汇'
    )
