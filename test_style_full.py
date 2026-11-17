import zipfile
import re
import xml.etree.ElementTree as ET

NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"

ET.register_namespace('a', NS_A)
ET.register_namespace('p', NS_P)

with zipfile.ZipFile('research_paper/test_full_level1.pptx') as z:
    for s_idx in [6, 8]:
        root = ET.fromstring(z.read(f'ppt/slides/slide{s_idx}.xml'))
        tables = root.findall(f".//{{{NS_A}}}tbl")
        print(f"Slide {s_idx} tables found: {len(tables)}")
        for tbl in tables:
            rows = tbl.findall(f"{{{NS_A}}}tr")
            print(f"  Rows count: {len(rows)}")
