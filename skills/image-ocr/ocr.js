#!/usr/bin/env node
'use strict';
// image-ocr: 命令行图片文字提取（中文优先）
// 依赖 tesseract.js（已装在 skill 目录 node_modules 内）
// 可选依赖 jimp（已装）：用于图像预处理（灰度/对比度/放大/旋转/反色/二值化）
const Tesseract = require('tesseract.js');
const fs = require('fs');
const path = require('path');

let Jimp = null;
try { Jimp = require('jimp').Jimp || require('jimp').default; } catch (e) { /* 无 jimp 时仅支持原图直识别 */ }

function printHelp() {
  console.log(`image-ocr — 命令行图片文字提取（中文优先）

用法:
  node ocr.js <图片或目录> [选项]

选项:
  --lang <代码>        OCR 语言, 默认 chi_sim (中文简体)
                       可用 chi_sim / eng / chi_sim+eng 等
  --psm <0-13>         页面分割模式, 默认 6 (整块文字, 适合证照/单据)
                       3=自动 4=单列 6=整块 11=稀疏
  --enhance            增强对比度（需 jimp）
  --binarize           二值化(黑白, OTSU 自动阈值)（需 jimp）
  --invert             反色（深底浅字扫描件）（需 jimp）
  --scale <倍率>       放大补像素, 默认 1 (如 2/3)（需 jimp）
  --rotate <角度>      旋转校正(度), 默认 0（需 jimp）
  --out <文件.txt>     结果输出到文件 (默认打印到控制台)
  --recursive, -r      递归处理子目录
  --ext png,jpg,...    指定处理的扩展名 (默认常见图片格式)
  --help, -h           显示帮助

示例:
  node ocr.js 发票.png
  node ocr.js 许可证.jpg --psm 6 --enhance --scale 2
  node ocr.js ./scan_dir --lang chi_sim+eng --recursive --out result.txt
`);
}

function parseArgs(argv) {
  const args = {
    _: [],
    lang: 'chi_sim',
    psm: 6,
    enhance: false,
    binarize: false,
    invert: false,
    scale: 1,
    rotate: 0,
    out: null,
    recursive: false,
    ext: ['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'tif', 'webp', 'gif'],
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--lang') args.lang = argv[++i];
    else if (a === '--psm') args.psm = parseInt(argv[++i], 10) || 6;
    else if (a === '--scale') args.scale = parseFloat(argv[++i]) || 1;
    else if (a === '--rotate') args.rotate = parseFloat(argv[++i]) || 0;
    else if (a === '--enhance') args.enhance = true;
    else if (a === '--binarize') args.binarize = true;
    else if (a === '--invert') args.invert = true;
    else if (a === '--out') args.out = argv[++i];
    else if (a === '--ext') args.ext = argv[++i].split(',').map(s => s.trim().toLowerCase()).filter(Boolean);
    else if (a === '--recursive' || a === '-r') args.recursive = true;
    else if (a === '--help' || a === '-h') { printHelp(); process.exit(0); }
    else args._.push(a);
  }
  return args;
}

function needsPreprocess(args) {
  return !!(Jimp && (args.enhance || args.binarize || args.invert || args.scale > 1 || args.rotate));
}

// 图像预处理：灰度 + 对比度/二值化 + 放大 + 旋转 + 反色，返回 PNG Buffer
async function preprocess(filePath, args) {
  const image = await Jimp.read(filePath);
  if (args.rotate) image.rotate(args.rotate);          // 自动适配外接框，不裁切
  if (args.scale > 1) image.scale(args.scale);
  if (args.invert) image.invert();
  image.greyscale();
  if (args.binarize) {
    const { data, width, height } = image.bitmap;
    const hist = new Array(256).fill(0);
    const N = width * height;
    for (let i = 0; i < data.length; i += 4) hist[data[i]]++;
    let sum = 0; for (let t = 0; t < 256; t++) sum += t * hist[t];
    let sumB = 0, wB = 0, maxVar = 0, thresh = 128;
    for (let t = 0; t < 256; t++) {
      wB += hist[t]; if (wB === 0) continue;
      const wF = N - wB; if (wF === 0) break;
      sumB += t * hist[t];
      const mB = sumB / wB, mF = (sum - sumB) / wF;
      const v = wB * wF * (mB - mF) * (mB - mF);
      if (v > maxVar) { maxVar = v; thresh = t; }
    }
    image.scan(0, 0, width, height, function (x, y, idx) {
      const v = this.bitmap.data[idx] > thresh ? 255 : 0;
      this.bitmap.data[idx] = this.bitmap.data[idx + 1] = this.bitmap.data[idx + 2] = v;
      this.bitmap.data[idx + 3] = 255;
    });
  } else if (args.enhance) {
    image.contrast(0.5);
  }
  return await image.getBuffer('image/png');
}

function listImages(target, args, acc) {
  acc = acc || [];
  let stat;
  try { stat = fs.statSync(target); } catch (e) { return acc; }
  if (stat.isFile()) {
    const ext = path.extname(target).slice(1).toLowerCase();
    if (args.ext.includes(ext)) acc.push(target);
    return acc;
  }
  if (stat.isDirectory()) {
    const entries = fs.readdirSync(target);
    for (const e of entries) {
      const full = path.join(target, e);
      let s;
      try { s = fs.statSync(full); } catch (e2) { continue; }
      if (s.isDirectory()) {
        if (args.recursive) listImages(full, args, acc);
      } else if (args.ext.includes(path.extname(full).slice(1).toLowerCase())) {
        acc.push(full);
      }
    }
  }
  return acc;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args._.length === 0) { printHelp(); process.exit(1); }

  let files = [];
  for (const t of args._) {
    if (!fs.existsSync(t)) { console.error('找不到:', t); continue; }
    listImages(t, args, files);
  }
  files = Array.from(new Set(files));
  if (files.length === 0) { console.error('没有可处理的图片文件'); process.exit(1); }

  const usePre = needsPreprocess(args);
  if (!Jimp && (args.enhance || args.binarize || args.invert || args.scale > 1 || args.rotate)) {
    console.error('[image-ocr] 警告: 未安装 jimp, 预处理选项被忽略, 使用原图直识别。');
  }
  console.error(`[image-ocr] 共 ${files.length} 个文件, 语言=${args.lang}, PSM=${args.psm}, 预处理=${usePre ? '开' : '关'}`);

  const results = [];
  for (let i = 0; i < files.length; i++) {
    const f = files[i];
    console.error(`[${i + 1}/${files.length}] 处理: ${f}`);
    try {
      const input = usePre ? await preprocess(f, args) : f;
      const { data: { text } } = await Tesseract.recognize(input, args.lang, {
        tessedit_pageseg_mode: args.psm,
        logger: m => {
          if (m.status === 'recognizing text') {
            process.stderr.write(`\r  进度 ${(m.progress * 100).toFixed(0)}%`);
          }
        },
      });
      process.stderr.write('\n');
      results.push({ file: f, text: text.trim() });
    } catch (err) {
      console.error(`  识别失败: ${err.message}`);
      results.push({ file: f, text: '' });
    }
  }

  if (args.out) {
    const blocks = results.map(r => `===== ${r.file} =====\n${r.text}\n`).join('\n');
    fs.writeFileSync(args.out, blocks, 'utf8');
    console.error(`[image-ocr] 结果已写入: ${args.out}`);
  } else {
    for (const r of results) {
      console.log(`\n===== ${r.file} =====`);
      console.log(r.text);
    }
  }
}

main().catch(e => { console.error('错误:', e); process.exit(1); });
