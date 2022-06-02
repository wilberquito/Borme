# author wilberquito

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

def generate_xml_files(n_days_back):
    
    create_export_folder(export)
    
    date = datetime.datetime.now()
    step = datetime.timedelta(1)
    n = n_days_back
    
    while n > 0:
        formatted = date.strftime(date_format)
        url = boe_diario_base.format(date=formatted)
        
        try:
            text = consum_boe(url)
            save_text(text, export + formatted + ".xml")
        except Exception as e:
            print(e, n)
            
        date = date - step
        n -= 1

def create_export_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)        
        