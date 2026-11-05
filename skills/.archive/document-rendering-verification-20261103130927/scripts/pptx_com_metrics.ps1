# Dump REAL PowerPoint render metrics for every text shape in a .pptx.
#
# Why: LibreOffice is often unavailable, and the model may not accept images,
#   but on a Windows host PowerPoint itself is the ground truth renderer.
#   Run from WSL:
#     powershell.exe -NoProfile -ExecutionPolicy Bypass -File \
#       "C:\path\pptx_com_metrics.ps1" -Deck "C:\path\deck.pptx" -Out "C:\path\metrics.tsv"
#   Then read metrics.tsv from WSL at /mnt/c/path/metrics.tsv
#
# TRUSTWORTHY: Lines().Count, per-line BoundLeft/BoundWidth, Font.Size,
#              ParagraphFormat.LineRuleWithin / LineSpacing / SpaceAfter.
# NOT TRUSTWORTHY: BoundTop / BoundHeight on multi-line text (BoundHeight
#              collapses to ~1pt and BoundTop is nonsense). Deliberately NOT
#              emitted here - compute vertical extents arithmetically instead:
#                line_height = fontSize * 1.2 * lineSpacingMultiple
#                text_height = sum(lines_in_para * line_height)
#                            + spaceAfter * (num_paragraphs - 1)
param(
  [Parameter(Mandatory=$true)][string]$Deck,
  [string]$Out = "$env:TEMP\pptx_metrics.tsv"
)
$ErrorActionPreference = "Stop"

$app = New-Object -ComObject PowerPoint.Application

# ReadOnly=$true, Untitled=$false, WithWindow=$true (a real window gives the
# most complete layout; try $false if this throws in a headless context).
# NOTE: setting $app.Visible afterwards throws - don't bother, WithWindow is enough.
$pres = $app.Presentations.Open($Deck, $true, $false, $true)

$rows = New-Object System.Collections.Generic.List[string]
$rows.Add((@("slide","name","left","top","w","h","fontSize","lineRule",
             "lineSpacing","spaceAfter","lines","maxBoundW","minBoundL","text") -join "`t"))

foreach ($slide in $pres.Slides) {
  foreach ($sh in $slide.Shapes) {
    $hasText = $false
    try { $hasText = [bool]$sh.HasTextFrame -and [bool]$sh.TextFrame.HasText } catch {}
    if (-not $hasText) { continue }

    $tr = $sh.TextFrame.TextRange
    $n  = $tr.Lines().Count

    $maxW = 0.0
    $minL = [double]::MaxValue
    for ($i = 1; $i -le $n; $i++) {
      $ln = $tr.Lines($i)
      if ($ln.BoundWidth -gt $maxW) { $maxW = $ln.BoundWidth }
      if ($ln.BoundLeft  -lt $minL) { $minL = $ln.BoundLeft }
    }
    if ($minL -eq [double]::MaxValue) { $minL = 0 }

    $pf  = $tr.ParagraphFormat
    $txt = ($tr.Text -replace "[`r`n`t]", " ").Trim()
    if ($txt.Length -gt 40) { $txt = $txt.Substring(0, 40) }

    $rows.Add((@(
      $slide.SlideIndex, $sh.Name,
      [math]::Round($sh.Left, 1),  [math]::Round($sh.Top, 1),
      [math]::Round($sh.Width, 1), [math]::Round($sh.Height, 1),
      $tr.Font.Size,
      $pf.LineRuleWithin,   # -1 = multiple-based, 0 = point-based
      $pf.LineSpacing,
      $pf.SpaceAfter,
      $n,
      [math]::Round($maxW, 1), [math]::Round($minL, 1),
      $txt
    ) -join "`t"))
  }
}

Set-Content -Path $Out -Value $rows -Encoding UTF8

try { $pres.Close() } catch {}
try { $app.Quit() } catch {}
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($app) | Out-Null

Write-Output "WROTE $Out ($($rows.Count - 1) text shapes)"
