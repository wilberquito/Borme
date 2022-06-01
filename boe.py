import requests
import xml.etree.ElementTree as ET

date_format = "%Y%m%d"
target_date = "20141006"
non_date = '20180101'
boe_diario_base = "https://www.boe.es/diario_borme/xml.php?id=BORME-S-{date}"


def parse_boe_xml(xml_str):
    root = ET.fromstring(xml_str)
    root_tag = root.tag
    
    if root_tag == 'error':
        description = root.find('descripcion').text
        raise Exception('error: ' + description)


if __name__ == '__main__':
    
    dates = [target_date, non_date]
    
    for date in dates:
        try:
            url = boe_diario_base.format(date=date)
            response = requests.get(url)
            parse_boe_xml(response.text)
        except Exception as e:
            print(str(e) + ' Fecha de consulta', date)