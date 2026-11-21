<!-- 盈信漫画分镜 - 角色SVG模板
用于公众号漫画分镜的卡通人物。直接复制下面的SVG代码到分镜HTML里。
每个角色是 <svg viewBox="0 0 100 120"> 内联图形，配合 width/height 属性缩放。

=== 江姐（女会计师，红衫棕长发）===
<svg xmlns="http://www.w3.org/2000/svg" width="150" height="180" viewBox="0 0 100 120">
  <circle cx="50" cy="42" r="30" fill="#F5CBA7"/>
  <path d="M20 36 Q22 10 50 10 Q78 10 80 36 L80 44 L20 44 Z" fill="#4E342E"/>
  <path d="M20 40 Q50 34 80 40 L80 46 Q50 40 20 46 Z" fill="#4E342E"/>
  <circle cx="40" cy="42" r="3.5" fill="#333"/>
  <circle cx="60" cy="42" r="3.5" fill="#333"/>
  <path d="M42 50 Q50 55 58 50" stroke="#B71C1C" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <rect x="28" y="72" width="44" height="42" rx="12" fill="#E53935"/>
  <path d="M50 72 L46 90 L50 86 L54 90 Z" fill="#FFF176"/>
</svg>

=== 徐总（男老板，蓝衫黑发红领带）===
<svg xmlns="http://www.w3.org/2000/svg" width="150" height="180" viewBox="0 0 100 120">
  <circle cx="50" cy="42" r="30" fill="#F8C471"/>
  <path d="M22 32 Q22 12 50 12 Q78 12 78 32 L74 32 Q72 18 50 18 Q30 18 26 32 Z" fill="#37474F"/>
  <circle cx="40" cy="42" r="3.5" fill="#333"/>
  <circle cx="60" cy="42" r="3.5" fill="#333"/>
  <path d="M40 52 Q50 59 60 52" stroke="#333" stroke-width="3" fill="none" stroke-linecap="round"/>
  <rect x="28" y="72" width="44" height="42" rx="12" fill="#1565C0"/>
  <path d="M50 72 L44 90 L50 85 L56 90 Z" fill="#E53935"/>
</svg>

=== 傻老板（客户提问，黄衫褐发张嘴困惑）===
<svg xmlns="http://www.w3.org/2000/svg" width="150" height="180" viewBox="0 0 100 120">
  <circle cx="50" cy="42" r="30" fill="#FDEBD0"/>
  <path d="M22 32 Q22 12 50 12 Q78 12 78 32 L74 32 Q72 18 50 18 Q30 18 26 32 Z" fill="#6D4C41"/>
  <circle cx="40" cy="42" r="3.5" fill="#333"/>
  <circle cx="60" cy="42" r="3.5" fill="#333"/>
  <path d="M38 54 Q50 44 62 54 Q50 62 38 54 Z" fill="#4E342E"/>  <!-- 张嘴困惑 -->
  <rect x="28" y="72" width="44" height="42" rx="12" fill="#F9A825"/>
  <path d="M50 72 L44 90 L50 85 L56 90 Z" fill="#E53935"/>
</svg>

=== 李会计（同行，绿衫戴眼镜）===
<svg xmlns="http://www.w3.org/2000/svg" width="150" height="180" viewBox="0 0 100 120">
  <circle cx="50" cy="42" r="30" fill="#E8D5B7"/>
  <path d="M22 32 Q22 12 50 12 Q78 12 78 32 L74 32 Q72 18 50 18 Q30 18 26 32 Z" fill="#455A64"/>
  <circle cx="40" cy="42" r="3.5" fill="#333"/>
  <circle cx="60" cy="42" r="3.5" fill="#333"/>
  <rect x="34" y="38" width="12" height="10" rx="3" fill="none" stroke="#455A64" stroke-width="2"/>
  <rect x="54" y="38" width="12" height="10" rx="3" fill="none" stroke="#455A64" stroke-width="2"/>
  <line x1="46" y1="43" x2="54" y2="43" stroke="#455A64" stroke-width="2"/>
  <path d="M40 52 Q50 59 60 52" stroke="#333" stroke-width="3" fill="none" stroke-linecap="round"/>
  <rect x="28" y="72" width="44" height="42" rx="12" fill="#2E7D32"/>
  <path d="M50 72 L44 90 L50 85 L56 90 Z" fill="#E53935"/>
</svg>

=== 对话气泡样本 ===
<div class="bubble" style="left:30px; top:120px; width:380px; border-color:#B71C1C;">
  <span class="speaker" style="color:#B71C1C;">江姐：</span>台词文字放这里，22px字号，自动换行。
</div>
<!-- 气泡箭头（weasyprint不支持::before伪元素箭头，用独立div） -->
<div class="arrow" style="left:410px; top:160px; border-right-color:#B71C1C;"></div>
<div class="arrowin" style="left:413px; top:160px;"></div>

对应CSS：
.bubble { position:absolute; background:#fff; border:3px solid #BF360C;
          border-radius:18px; padding:14px 18px; font-size:22px; line-height:1.55; color:#3E2723; }
.speaker { font-weight:bold; }
.arrow { position:absolute; width:0; height:0; border:12px solid transparent; }
.arrowin { position:absolute; width:0; height:0; border:9px solid transparent; border-right-color:#fff; }
-->
