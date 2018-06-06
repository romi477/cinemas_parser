import xml.etree.ElementTree as ET
from xml.dom import minidom


root = ET.Element('StatisticsExportKey')
attr = ET.Element('Cinema')
root.append(attr)
title = ET.SubElement(attr, 'title')
tree = ET.ElementTree(root)



# with open('newstat.xml', 'wb') as xfile:
tree.write("new.xml")





