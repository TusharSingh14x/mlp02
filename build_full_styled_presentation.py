import subprocess
import zipfile
import re
import os
import xml.etree.ElementTree as ET

NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

ET.register_namespace('a', NS_A)
ET.register_namespace('p', NS_P)
ET.register_namespace('r', NS_R)

md_file = "research_paper/PhishGuard_XAI_Full_10_Slides.md"
raw_pptx = "research_paper/raw_full.pptx"
final_pptx = "research_paper/PhishGuard_XAI_10_Slides.pptx"

# 1. Compile with Pandoc enforcing --slide-level=1
print("[*] Compiling full Markdown to raw PPTX with Pandoc...")
cmd = ["pandoc", md_file, "--slide-level=1", "-o", raw_pptx]
subprocess.run(cmd, check=True)

def create_bg(color_hex):
    bg = ET.Element(f"{{{NS_P}}}bg")
    bgPr = ET.SubElement(bg, f"{{{NS_P}}}bgPr")
    solidFill = ET.SubElement(bgPr, f"{{{NS_A}}}solidFill")
    ET.SubElement(solidFill, f"{{{NS_A}}}srgbClr", {'val': color_hex})
    ET.SubElement(bgPr, f"{{{NS_A}}}effectLst")
    return bg

def create_top_bar(color_hex="06B6D4"):
    sp = ET.Element(f"{{{NS_P}}}sp")
    nvSpPr = ET.SubElement(sp, f"{{{NS_P}}}nvSpPr")
    ET.SubElement(nvSpPr, f"{{{NS_P}}}cNvPr", {'id': "301", 'name': "Top Accent Bar"})
    ET.SubElement(nvSpPr, f"{{{NS_P}}}cNvSpPr")
    ET.SubElement(nvSpPr, f"{{{NS_P}}}nvPr")
    
    spPr = ET.SubElement(sp, f"{{{NS_P}}}spPr")
    xfrm = ET.SubElement(spPr, f"{{{NS_A}}}xfrm")
    ET.SubElement(xfrm, f"{{{NS_A}}}off", {'x': "0", 'y': "0"})
    ET.SubElement(xfrm, f"{{{NS_A}}}ext", {'cx': "9144000", 'cy': "70000"})
    prstGeom = ET.SubElement(spPr, f"{{{NS_A}}}prstGeom", {'prst': "rect"})
    ET.SubElement(prstGeom, f"{{{NS_A}}}avLst")
    solidFill = ET.SubElement(spPr, f"{{{NS_A}}}solidFill")
    ET.SubElement(solidFill, f"{{{NS_A}}}srgbClr", {'val': color_hex})
    return sp

def create_footer(slide_num):
    sp = ET.Element(f"{{{NS_P}}}sp")
    nvSpPr = ET.SubElement(sp, f"{{{NS_P}}}nvSpPr")
    ET.SubElement(nvSpPr, f"{{{NS_P}}}cNvPr", {'id': "302", 'name': "Footer"})
    ET.SubElement(nvSpPr, f"{{{NS_P}}}cNvSpPr")
    ET.SubElement(nvSpPr, f"{{{NS_P}}}nvPr")
    
    spPr = ET.SubElement(sp, f"{{{NS_P}}}spPr")
    xfrm = ET.SubElement(spPr, f"{{{NS_A}}}xfrm")
    ET.SubElement(xfrm, f"{{{NS_A}}}off", {'x': "457200", 'y': "4850000"})
    ET.SubElement(xfrm, f"{{{NS_A}}}ext", {'cx': "8229600", 'cy': "220000"})
    
    txBody = ET.SubElement(sp, f"{{{NS_P}}}txBody")
    ET.SubElement(txBody, f"{{{NS_A}}}bodyPr")
    ET.SubElement(txBody, f"{{{NS_A}}}lstStyle")
    p = ET.SubElement(txBody, f"{{{NS_A}}}p")
    
    r1 = ET.SubElement(p, f"{{{NS_A}}}r")
    rPr1 = ET.SubElement(r1, f"{{{NS_A}}}rPr", {'sz': "900"})
    sFill1 = ET.SubElement(rPr1, f"{{{NS_A}}}solidFill")
    ET.SubElement(sFill1, f"{{{NS_A}}}srgbClr", {'val': "64748B"})
    t1 = ET.SubElement(r1, f"{{{NS_A}}}t")
    t1.text = "IIIT Nagpur • CSE | Capstone Presentation"
    
    r2 = ET.SubElement(p, f"{{{NS_A}}}r")
    rPr2 = ET.SubElement(r2, f"{{{NS_A}}}rPr", {'sz': "900", 'b': "1"})
    sFill2 = ET.SubElement(rPr2, f"{{{NS_A}}}solidFill")
    ET.SubElement(sFill2, f"{{{NS_A}}}srgbClr", {'val': "38BDF8"})
    t2 = ET.SubElement(r2, f"{{{NS_A}}}t")
    t2.text = f"                                                                                      Slide {slide_num} of 10"
    return sp

def style_table(tbl):
    rows = tbl.findall(f"{{{NS_A}}}tr")
    for r_idx, row in enumerate(rows):
        # check row text to see if proposed/highlight
        row_text = "".join([t.text for t in row.findall(f".//{{{NS_A}}}t") if t.text])
        is_header = (r_idx == 0)
        is_proposed = ("Top-30" in row_text or "Stacking Ensemble (Proposed)" in row_text or "Homoglyph" in row_text or "Leetspeak" in row_text)
        
        for cell in row.findall(f"{{{NS_A}}}tc"):
            tcPr = cell.find(f"{{{NS_A}}}tcPr")
            if tcPr is None:
                tcPr = ET.SubElement(cell, f"{{{NS_A}}}tcPr")
            for child in list(tcPr):
                if child.tag.endswith('solidFill'):
                    tcPr.remove(child)
            
            fill = ET.SubElement(tcPr, f"{{{NS_A}}}solidFill")
            if is_header:
                ET.SubElement(fill, f"{{{NS_A}}}srgbClr", {'val': "1E3A8A"}) # Navy blue header
            elif is_proposed:
                ET.SubElement(fill, f"{{{NS_A}}}srgbClr", {'val': "0C3854"}) # Glowing dark cyan
            elif r_idx % 2 == 1:
                ET.SubElement(fill, f"{{{NS_A}}}srgbClr", {'val': "131D31"}) # Deep row 1
            else:
                ET.SubElement(fill, f"{{{NS_A}}}srgbClr", {'val': "0F172A"}) # Dark row 2
                
            # Restyle cell text
            for p in cell.findall(f".//{{{NS_A}}}p"):
                for r in p.findall(f".//{{{NS_A}}}r"):
                    rPr = r.find(f"{{{NS_A}}}rPr")
                    if rPr is None:
                        rPr = ET.SubElement(r, f"{{{NS_A}}}rPr")
                    for child in list(rPr):
                        if child.tag.endswith('solidFill'):
                            rPr.remove(child)
                    sFill = ET.SubElement(rPr, f"{{{NS_A}}}solidFill")
                    if is_header:
                        rPr.set('b', '1')
                        rPr.set('sz', '1100')
                        ET.SubElement(sFill, f"{{{NS_A}}}srgbClr", {'val': "FFFFFF"})
                    elif is_proposed:
                        rPr.set('b', '1')
                        rPr.set('sz', '1000')
                        ET.SubElement(sFill, f"{{{NS_A}}}srgbClr", {'val': "38BDF8"})
                    else:
                        rPr.set('sz', '1000')
                        ET.SubElement(sFill, f"{{{NS_A}}}srgbClr", {'val': "CBD5E1"})

def process_slide(xml_data, slide_idx):
    root = ET.fromstring(xml_data)
    cSld = root.find(f"{{{NS_P}}}cSld")
    spTree = cSld.find(f"{{{NS_P}}}spTree")
    
    # 1. Slide Background
    bg_color = "070D18" if slide_idx == 1 else "0B1120"
    cSld.insert(0, create_bg(bg_color))
    
    # 2. Add Top Bar & Footer
    spTree.append(create_top_bar("06B6D4" if slide_idx > 1 else "3B82F6"))
    if slide_idx > 1:
        spTree.append(create_footer(slide_idx))
        
    # 3. Tables Styling
    for tbl in root.findall(f".//{{{NS_A}}}tbl"):
        style_table(tbl)
        
    # 4. Restyle Text
    for sp_elem in spTree.findall(f"{{{NS_P}}}sp"):
        nvSpPr = sp_elem.find(f"{{{NS_P}}}nvSpPr")
        if nvSpPr is None:
            continue
        ph = nvSpPr.find(f".//{{{NS_P}}}ph")
        ph_type = ph.get('type') if ph is not None else None
        
        txBody = sp_elem.find(f"{{{NS_P}}}txBody")
        if txBody is None:
            continue
            
        for p in txBody.findall(f"{{{NS_A}}}p"):
            p_text = "".join([t.text for t in p.findall(f".//{{{NS_A}}}t") if t.text])
            is_subhead = (p_text.startswith("The Phishing Threat") or 
                          p_text.startswith("The Fatal Limitation") or
                          p_text.startswith("Base Literature Surveyed") or
                          p_text.startswith("The 4 Critical Systemic") or
                          p_text.startswith("The 5-Stage") or
                          p_text.startswith("Core Engineering Guarantee") or
                          p_text.startswith("Zero-Network Client-Side") or
                          p_text.startswith("Line-Rate Gateway") or
                          p_text.startswith("3-Way Rank Aggregation") or
                          p_text.startswith("The Empirical Head-to-Head") or
                          p_text.startswith("Two-Tier Heterogeneous") or
                          p_text.startswith("Optimization & Statistical") or
                          p_text.startswith("5-Fold Stratified") or
                          p_text.startswith("Confusion Matrix Breakdown") or
                          p_text.startswith("Adversarial Red-Teaming") or
                          p_text.startswith("Security-Hardened LLM") or
                          p_text.startswith("Production Microservice") or
                          p_text.startswith("Research Conclusion"))
            
            for r in p.findall(f"{{{NS_A}}}r"):
                rPr = r.find(f"{{{NS_A}}}rPr")
                if rPr is None:
                    rPr = ET.SubElement(r, f"{{{NS_A}}}rPr")
                
                # Check if title
                if ph_type in ['ctrTitle', 'title']:
                    rPr.set('b', '1')
                    rPr.set('sz', '2600' if slide_idx == 1 else '2000')
                    for child in list(rPr):
                        if child.tag.endswith('solidFill'):
                            rPr.remove(child)
                    solidFill = ET.SubElement(rPr, f"{{{NS_A}}}solidFill")
                    ET.SubElement(solidFill, f"{{{NS_A}}}srgbClr", {'val': "FFFFFF"})
                    latin = ET.SubElement(rPr, f"{{{NS_A}}}latin", {'typeface': "Trebuchet MS"})
                elif ph_type == 'subTitle':
                    rPr.set('sz', '1500')
                    for child in list(rPr):
                        if child.tag.endswith('solidFill'):
                            rPr.remove(child)
                    solidFill = ET.SubElement(rPr, f"{{{NS_A}}}solidFill")
                    ET.SubElement(solidFill, f"{{{NS_A}}}srgbClr", {'val': "38BDF8"})
                    latin = ET.SubElement(rPr, f"{{{NS_A}}}latin", {'typeface': "Helvetica"})
                elif is_subhead:
                    rPr.set('b', '1')
                    rPr.set('sz', '1250')
                    for child in list(rPr):
                        if child.tag.endswith('solidFill'):
                            rPr.remove(child)
                    solidFill = ET.SubElement(rPr, f"{{{NS_A}}}solidFill")
                    ET.SubElement(solidFill, f"{{{NS_A}}}srgbClr", {'val': "38BDF8"}) # Cyan subhead
                    latin = ET.SubElement(rPr, f"{{{NS_A}}}latin", {'typeface': "Trebuchet MS"})
                else:
                    # Body text
                    is_bold = rPr.get('b') == '1'
                    rPr.set('sz', '1050')
                    for child in list(rPr):
                        if child.tag.endswith('solidFill'):
                            rPr.remove(child)
                    solidFill = ET.SubElement(rPr, f"{{{NS_A}}}solidFill")
                    if is_bold:
                        ET.SubElement(solidFill, f"{{{NS_A}}}srgbClr", {'val': "38BDF8"}) # Accent Cyan for bold keywords
                    else:
                        ET.SubElement(solidFill, f"{{{NS_A}}}srgbClr", {'val': "CBD5E1"}) # Slate silver text
                    latin = ET.SubElement(rPr, f"{{{NS_A}}}latin", {'typeface': "Helvetica"})

    return ET.tostring(root, encoding='utf-8', xml_declaration=True)

# Custom Theme XML
DARK_THEME_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="PhishGuard Dark Cyber">
  <a:themeElements>
    <a:clrScheme name="PhishGuard Dark">
      <a:dk1><a:srgbClr val="FFFFFF"/></a:dk1>
      <a:lt1><a:srgbClr val="0B1120"/></a:lt1>
      <a:dk2><a:srgbClr val="F8FAFC"/></a:dk2>
      <a:lt2><a:srgbClr val="1E293B"/></a:lt2>
      <a:accent1><a:srgbClr val="38BDF8"/></a:accent1>
      <a:accent2><a:srgbClr val="06B6D4"/></a:accent2>
      <a:accent3><a:srgbClr val="10B981"/></a:accent3>
      <a:accent4><a:srgbClr val="F59E0B"/></a:accent4>
      <a:accent5><a:srgbClr val="8B5CF6"/></a:accent5>
      <a:accent6><a:srgbClr val="EF4444"/></a:accent6>
      <a:hlink><a:srgbClr val="38BDF8"/></a:hlink>
      <a:folHlink><a:srgbClr val="A78BFA"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="Office">
      <a:majorFont><a:latin typeface="Trebuchet MS"/></a:majorFont>
      <a:minorFont><a:latin typeface="Helvetica"/></a:minorFont>
    </a:fontScheme>
  </a:themeElements>
</a:theme>"""

print("[*] Applying styling to all 10 slides and tables...")
with zipfile.ZipFile(raw_pptx, 'r') as zin, zipfile.ZipFile(final_pptx, 'w') as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        m = re.match(r'ppt/slides/slide(\d+)\.xml', item.filename)
        if m:
            slide_idx = int(m.group(1))
            styled_xml = process_slide(data, slide_idx)
            zout.writestr(item.filename, styled_xml)
        elif 'theme1.xml' in item.filename or 'theme2.xml' in item.filename:
            zout.writestr(item.filename, DARK_THEME_XML.encode('utf-8'))
        elif 'slideMaster1.xml' in item.filename or 'slideLayout' in item.filename:
            xml_str = data.decode('utf-8')
            if '<p:bg>' in xml_str:
                xml_str = re.sub(r'<p:bg>.*?</p:bg>', '<p:bg><p:bgPr><a:solidFill><a:srgbClr val="0B1120"/></a:solidFill></p:bgPr></p:bg>', xml_str)
            zout.writestr(item.filename, xml_str.encode('utf-8'))
        else:
            zout.writestr(item.filename, data)

print(f"[+] SUCCESS! Built complete 10-slide styled presentation: {final_pptx}")
