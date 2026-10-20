'use strict';

// Fills templates/gallery.html from a zagens-image manifest.
// Does not search, download, or open the network.

const fs = require('fs');
const os = require('os');
const path = require('path');

const VERSION = '0.1.6';

function fail(code, error, suggestion) {
  const payload = { ok: false, code, error };
  if (suggestion) payload.suggestion = suggestion;
  process.stdout.write(JSON.stringify(payload) + '\n');
  process.exitCode = 1;
}

function escapeHtml(value) {
  return String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function escapeJson(value) {
  return JSON.stringify(value)
    .replace(/&/g, '\\u0026')
    .replace(/</g, '\\u003c')
    .replace(/>/g, '\\u003e')
    .replace(/\u2028/g, '\\u2028')
    .replace(/\u2029/g, '\\u2029');
}

function fill(template, queryHtml, dataJson) {
  const parts = template.split('__DATA__');
  if (parts.length !== 2) {
    throw Object.assign(new Error('画廊模板必须只有一处 __DATA__'), { codeName: 'template' });
  }
  const query = (part) => part.split('__QUERY__').join(queryHtml);
  return query(parts[0]) + dataJson + query(parts[1]);
}

function baseName(filePath) {
  const name = String(filePath || '').replace(/\\/g, '/').split('/').pop();
  return name || 'image';
}

function resultOf(payload) {
  if (payload && Array.isArray(payload.assets)) return payload;
  if (payload && payload.result && Array.isArray(payload.result.assets)) return payload.result;
  throw Object.assign(new Error('清单里没有 assets'), { codeName: 'validation' });
}

function toItem(asset, index) {
  const abs = asset.path || '';
  return {
    source: asset.source || '',
    title: asset.title || '',
    w: Number(asset.width || asset.w || 0),
    h: Number(asset.height || asset.h || 0),
    file: baseName(asset.relative_path || abs),
    file_abs: abs,
    license: asset.license || null,
    license_url: asset.license_url || null,
    license_status: asset.license_status || 'unknown',
    author: asset.author || null,
    attribution: asset.attribution || '',
    source_page: asset.source_page || null,
    source_label: '#' + (index + 1),
    suitability_score: Number(asset.suitability_score || 0),
    match_reasons: asset.match_reasons || [],
    risk_flags: asset.risk_flags || [],
  };
}

function templatePath() {
  return path.join(__dirname, '..', 'templates', 'gallery.html');
}

function renderManifest(manifestPath, outPath) {
  const template = fs.readFileSync(templatePath(), 'utf8');
  const payload = resultOf(JSON.parse(fs.readFileSync(manifestPath, 'utf8')));
  const items = payload.assets.map(toItem);
  const query = payload.query || '图片素材';
  const html = fill(template, escapeHtml(query), escapeJson(items));
  const target = outPath || path.join(path.dirname(path.resolve(manifestPath)), 'index.html');
  const tmp = target + '.' + process.pid + '.tmp';
  fs.writeFileSync(tmp, html);
  try {
    if (fs.existsSync(target)) fs.rmSync(target, { force: true });
    fs.renameSync(tmp, target);
  } catch (error) {
    fs.rmSync(tmp, { force: true });
    throw error;
  }
  return {
    ok: true,
    op: 'render_gallery',
    version: VERSION,
    query,
    count: items.length,
    html: target.replace(/\\/g, '/'),
  };
}

function selfCheck() {
  const template = fs.readFileSync(templatePath(), 'utf8');
  if (template.split('__DATA__').length !== 2) throw new Error('data slot');
  if (!template.includes('__QUERY__')) throw new Error('query slot');
  if (!template.includes('复制选中图片路径')) throw new Error('copy control');
  if (!template.includes('按宽高比（横向优先）')) throw new Error('sort control');
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'zagens-gallery-'));
  const manifest = path.join(root, 'image-manifest.json');
  fs.writeFileSync(
    manifest,
    JSON.stringify({
      query: '<script>',
      assets: [
        {
          source: 'wikimedia',
          title: '</script><img>',
          path: path.join(root, 'tower.jpg'),
          relative_path: 'tower.jpg',
          width: 1920,
          height: 1080,
          license: 'CC BY 4.0',
          author: 'Author',
          attribution: '"Tower" — Author — CC BY 4.0',
          source_page: 'https://commons.wikimedia.org/wiki/File:Tower.jpg',
          license_status: 'verified',
          suitability_score: 90,
        },
      ],
    })
  );
  const rendered = renderManifest(manifest);
  const html = fs.readFileSync(rendered.html, 'utf8');
  if (!html.includes('&lt;script&gt;')) throw new Error('query escape');
  if (html.includes('</script><img>')) throw new Error('title broke out of script');
  if (!html.includes('\\u003c/script\\u003e')) throw new Error('json escape');
  if (!html.includes('查看来源')) throw new Error('source link');
  if (!html.includes('tower.jpg')) throw new Error('image src');
  const weird = path.join(root, 'weird.json');
  fs.writeFileSync(
    weird,
    JSON.stringify({
      query: '__DATA__',
      assets: [{ source: 'wikimedia', title: 'Keep', path: path.join(root, 'keep.jpg'), width: 8, height: 8 }],
    })
  );
  const second = renderManifest(weird);
  const secondHtml = fs.readFileSync(second.html, 'utf8');
  if (!secondHtml.includes('keep.jpg')) throw new Error('payload swallowed');
  fs.rmSync(root, { recursive: true, force: true });
  process.stdout.write(JSON.stringify({ ok: true, op: 'self_check', version: VERSION }) + '\n');
}

function main() {
  const args = process.argv.slice(2);
  if (args.includes('--self-check')) {
    selfCheck();
    return;
  }
  let manifest = null;
  let out = null;
  for (let i = 0; i < args.length; i += 1) {
    if (args[i] === '--manifest') manifest = args[++i];
    else if (args[i] === '--out') out = args[++i];
    else {
      fail('validation', '未知参数 ' + args[i], '只接受 --manifest 与可选的 --out。本脚本不搜图、不下载。');
      return;
    }
  }
  if (!manifest) {
    fail('validation', '缺少 --manifest', '把 zagens-image 写出的 image-manifest.json 传给 --manifest');
    return;
  }
  if (!fs.existsSync(manifest)) {
    fail('validation', '找不到清单 ' + manifest, '先用 zagens-image download 写出 image-manifest.json');
    return;
  }
  try {
    process.stdout.write(JSON.stringify(renderManifest(manifest, out)) + '\n');
  } catch (error) {
    fail(error.codeName || 'template', error.message, '确认清单是引擎 download 的结果，且 templates/gallery.html 还在。');
  }
}

if (require.main === module) {
  try {
    main();
  } catch (error) {
    fail('internal', error.message, '把这条错误原样回报，不要改写页面或下载脚本。');
  }
}

module.exports = { fill, escapeHtml, escapeJson, toItem };
