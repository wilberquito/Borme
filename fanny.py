# coding=utf-8
from xml.etree import ElementTree
import requests
import datetime
import random
import time
import json

def get_today_data():
    today = datetime.date.today()
    return today.strftime(date_format)

date_format = "%Y%m%d"
start_date = "20180101"
end_date = get_today_data()
url_base = "https://www.boe.es"
get_borme_stream_url = url_base + "/diario_borme/xml.php?id=BORME-S-"

def str_time_prop(start, end, time_format, prop):
    """Get a time at a proportion of a range of two formatted times.
    start and end should be strings specifying times formatted in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """
    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))
    ptime = stime + prop * (etime - stime)
    return time.strftime(time_format, time.localtime(ptime))

def get_random_data():
    return str_time_prop(start_date, end_date, '%Y%m%d', random.random())

def get_borme_stream(url):
    borme_info_array = []
    response = requests.get(url, stream=True)
    response.raw.decode_content = True
    events = ElementTree.iterparse(response.raw)
    for event, elem in events:
        if elem.tag == "emisor":
            name = elem.attrib['nombre']
            type = elem.attrib['etq']
            item = elem.findall('item')
            for item_element in item:
                if item_element is not None:
                    url_xml = item_element.find('urlXml')
                    titulo = item_element.find('titulo')
                    if url_xml is not None and titulo is not None:
                        borme_info_array.append({
                            'url': url_xml.text,
                            'title': titulo.text,
                            'name': name,
                            'type': type
                        })
    return borme_info_array

def get_anuncios_stream(url):
    response = requests.get(url, stream=True)
    response.raw.decode_content = True
    events = ElementTree.iterparse(response.raw)
    anuncio_info = {}
    p_info = ""
    for event, elem in events:
        if elem.tag != 'td' and elem.tag != 'tr' and elem.tag != 'p':
            anuncio_info[elem.tag] = elem.text
        # end if
        elif elem.tag == 'p' and elem.text is not None:
            p_info = p_info + " " + elem.text
    # end for
    anuncio_info['info_extra'] = p_info
    anuncio_info['url'] = url
    return anuncio_info

if __name__ == '__main__':
    print ('Init program')
    array_date = []
    borme_data_array = []
    x = range(250)
    index = 0
    for i in x:
        date = get_random_data()
        if date not in array_date:
            print (date)
            borme_data_array = borme_data_array + get_borme_stream(get_borme_stream_url + get_random_data())
            """ for info in borme_data_array:
            
                info = dict(info, **get_anuncios_stream(url_base + info['url']))
                with open("test.txt", "a") as myfile:
                    if index > 0:
                        myfile.write(",")
                    myfile.write(json.dumps(info))
                index += 1
            # end
            """
            index += 1
            array_date.append(date)

    with open("test.txt", "a") as myfile:
        myfile.write(json.dumps(borme_data_array))
    print ('End program')