import requests
import datetime
import os

date_format = "%Y%m%d"
boe_diario_base = "https://www.boe.es/diario_borme/xml.php?id=BORME-S-{date}"
export = './export/'

def consum_boe(url):
    return requests.get(url).text

def save_text(text, filename):
    with open(filename, "w+", encoding='iso-8859-1') as f:
        f.write(text)

def generate_xml_files(days_back):
    
    create_export_folder(export)
    
    date = datetime.datetime.now()
    back = datetime.timedelta(1)
    n = days_back
    
    while n > 0:
        date = date - back
        data_format = date.strftime(date_format)
        url = boe_diario_base.format(date=data_format)
        
        try:
            text = consum_boe(url)
            save_text(text, export + data_format + ".xml")
        except Exception as e:
            print(e, n)
            
        n -= 1

def create_export_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)        
        