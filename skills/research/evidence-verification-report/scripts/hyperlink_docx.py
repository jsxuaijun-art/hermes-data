#!/usr/bin/env python3
"""Emit a python-docx snippet with clickable hyperlinks, self-contained.
Usage: python hyperlink_docx.py            # prints the add_hyperlink() helper
       python hyperlink_docx.py demo.docx  # builds a demo doc with 2 links
Requires python-docx (pip install python-docx).
"""
import sys
import docx
from docx.oxml.ns import qn
from docx.oxml.shared import OxmlElement
from docx.shared import RGBColor


def add_hyperlink(paragraph, url, text, color=0x1F3B73, underline=True, size=10.5):
    """Add a clickable hyperlink run into an existing paragraph."""
    part = paragraph.part
    r_id = part.relate_to(url,
        docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)

    run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    c = OxmlElement('w:color')
    c.set(qn('w:val'), str(RGBColor(color)))
    rPr.append(c)
    if underline:
        u = OxmlElement('w:u'); u.set(qn('w:val'), 'single'); rPr.append(u)
    if size:
        sz = OxmlElement('w:sz'); sz.set(qn('w:val'), str(int(size * 2)))
        rPr.append(sz)
        szCs = OxmlElement('w:szCs'); szCs.set(qn('w:val'), str(int(size * 2)))
        rPr.append(szCs)
    run.append(rPr)
    t = OxmlElement('w:t')
    t.set(qn('xml:space'), 'preserve')
    t.text = text
    run.append(t)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)
    return hyperlink


def count_hyperlinks(doc):
    return sum(1 for k, v in doc.part.rels.items()
               if getattr(v, 'reltype', '').endswith('hyperlink'))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    doc = docx.Document()
    p = doc.add_paragraph('参考文献：')
    add_hyperlink(p, 'https://www.cdc.gov/shingles/vaccines/index.html',
                  '[1] CDC Shingles Vaccination')
    p2 = doc.add_paragraph()
    add_hyperlink(p2, 'https://www.who.int/',
                  '[2] WHO', size=10.5)
    out = sys.argv[1]
    doc.save(out)
    # verify
    chk = docx.Document(out)
    print(f'saved {out}; hyperlink rels = {count_hyperlinks(chk)}')


if __name__ == '__main__':
    main()
