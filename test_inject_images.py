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

# Check if raw_full.pptx exists
if not os.path.exists("research_paper/raw_full.pptx"):
    print("raw_full.pptx not found")
else:
    print("raw_full.pptx exists")
