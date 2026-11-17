import zipfile
import re
import xml.etree.ElementTree as ET

NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
}

for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)

print("ET registered namespaces successfully")
