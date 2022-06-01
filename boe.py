import requests
import xml.etree.ElementTree as ET

date_format = "%Y%m%d"
target_date = "20141006"
non_date = '20180101'
boe_diario_base = "https://www.boe.es/diario_borme/xml.php?id=BORME-S-{date}"



def map_i_parse_boe_xml(root, children_content):
    tag = root.tag
    local_data = {}
    
    match tag:
        case 'meta':
            local_data['meta'] = children_content
        case 'diario':
            pass
        
    return local_data

def i_parse_boe_xml(root):
    
    data = {}
    
    if root is None:
        return data
    
    if len(root) == 0:
        data = {
            'tag': root.tag,
            'attrib': root.attrib,
            'text': root.text
        }
        return data
    
    else:
        for child in root:
            try:
                children_content = i_parse_boe_xml(child)
                data.update(children_content)
            except Exception as e:
                print(e)
    
    return data

def parse_boe_xml(xml_str):
    
    data = {}
    root = ET.fromstring(xml_str)
    root_tag = root.tag
    
    if root_tag == 'error':
        description = root.find('descripcion').text
        raise Exception('error: ' + description)
    else:
        return i_parse_boe_xml(root)
        

if __name__ == '__main__':
    
    dates = [target_date]
    
    for date in dates:
        try:
            url = boe_diario_base.format(date=date)
            response = requests.get(url)
            boe_data = parse_boe_xml(response.text)
            print(boe_data)
            
        except Exception as e:
            print(str(e) + ' Fecha de consulta', date)
    
    # dic = {
    #     'hola': 'hola'
    # } 
    # dic.update({})
    
    # print(dic)       
        