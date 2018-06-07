from xml.dom import minidom

doc = minidom.Document()
root = doc.createElement('StatisticsExportKey')
doc.appendChild(root)
cinema = doc.createElement('Cinema')
cinema.setAttribute('UID', '3002D4CF-8699-4946-BB02-9414348D9892')
cinema.setAttribute('Name', 'RIFTER2.1-CZAKALOV.501-RU')
root.appendChild(cinema)

license = doc.createElement('License')
license.setAttribute('Signature', '...')
root.appendChild(license)

xml_str = doc.toprettyxml(indent="    ")
with open("Stat.xml", "w") as f:
    f.write(xml_str)
