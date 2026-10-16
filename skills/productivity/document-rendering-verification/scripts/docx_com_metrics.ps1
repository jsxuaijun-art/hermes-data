# docx_com_metrics.ps1 -- Word COM as the render oracle for a .docx, from WSL.
#
# THIS FILE IS ASCII-ONLY ON PURPOSE.
# Windows PowerShell 5.1 decodes a BOM-less .ps1 as ANSI. A script authored from
# Linux/WSL is UTF-8 without BOM, so any non-ASCII literal here (a Chinese path
# baked in, a Chinese comment) becomes mojibake and Documents.Open fails with
# "cannot find the file" for a file that plainly exists. Keep every literal
# ASCII and pass paths in as arguments.
#
# Usage from WSL (copy a Chinese-named deliverable to an ASCII path first):
#   mkdir -p /mnt/c/Users/<user>/docqa
#   cp "/mnt/c/Users/<user>/Desktop/<cn name>.docx" /mnt/c/Users/<user>/docqa/q.docx
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File \
#     "C:\Users\<user>\docqa\docx_com_metrics.ps1" \
#     "C:\Users\<user>\docqa\q.docx" "C:\Users\<user>\docqa\q.pdf"
#
# Then render the PDF to page images (pdftoppm -r 100 if poppler-utils is present,
# otherwise PyMuPDF/fitz in the venv) and run the visual QA pass in SKILL.md.

param(
  [Parameter(Mandatory=$true)][string]$Src,
  [Parameter(Mandatory=$true)][string]$Pdf
)

$ErrorActionPreference = "Stop"

if (!(Test-Path -LiteralPath $Src)) {
  Write-Output "SRC_NOT_FOUND: $Src"
  exit 2
}

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0

try {
  $doc = $word.Documents.Open($Src, $false, $true)   # (path, ConfirmConversions, ReadOnly)

  $textWidth = $doc.PageSetup.PageWidth - $doc.PageSetup.LeftMargin - $doc.PageSetup.RightMargin
  Write-Output ("PAGES {0}" -f $doc.ComputeStatistics(2))          # 2 = wdStatisticPages
  Write-Output ("PARAGRAPHS {0}" -f $doc.Paragraphs.Count)
  Write-Output ("TABLES {0}" -f $doc.Tables.Count)
  Write-Output ("PAGE_WIDTH_PT {0:N1}" -f $doc.PageSetup.PageWidth)
  Write-Output ("TEXT_WIDTH_PT {0:N1}" -f $textWidth)

  $i = 0
  foreach ($t in $doc.Tables) {
    $i++
    $sum = 0.0
    try {
      foreach ($c in $t.Columns) { $sum += [double]$c.Width }
    } catch {
      $sum = -1.0   # merged / irregular tables can refuse per-column width
    }
    $flag = ""
    if ($sum -gt ($textWidth + 1)) { $flag = "  <== WIDER THAN TEXT COLUMN (Word will re-fit)" }
    if ($sum -lt 0) { $flag = "  (column widths unavailable - merged cells?)" }
    Write-Output ("TABLE {0} rows={1} cols={2} width_pt={3:N1}{4}" -f $i, $t.Rows.Count, $t.Columns.Count, $sum, $flag)
  }

  # Leftover placeholder / unfilled-marker scan straight from the document text.
  $body = $doc.Content.Text
  foreach ($needle in @("TODO", "TBD", "XXX", "FIXME", "PLACEHOLDER", "Lorem")) {
    if ($body -match [regex]::Escape($needle)) {
      Write-Output ("PLACEHOLDER_HIT: {0}" -f $needle)
    }
  }

  $doc.ExportAsFixedFormat($Pdf, 17)   # 17 = wdExportFormatPDF
  Write-Output ("PDF {0}" -f $Pdf)
  $doc.Close($false)
}
finally {
  $word.Quit()
  [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}
