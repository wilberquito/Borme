from ast import pattern
import math
import time
from PyPDF2 import PdfReader
import re
from functools import reduce

from numpy import mat

others = 'Otros'
keywords = ['Disolución', 'Cambio de denominación social', 'Constitución']
pattern = r'\d{6}\s*-'

def is_target(text, keywords):
    '''
    text: string
    keywords: list of strings
    
    search if any keyword is in the text
    '''
    for keyword in keywords:
        if keyword in text:
            return True
    return False

def labeled_text(text, keywords):
    '''
    text: string
    keywords: list of strings
    
    return a labeled tuple with the text and the keyword
    '''
    for keyword in keywords:
        if keyword in text:
            return (keyword, text)
    return (others, text)

def convert(accum, tup):
    '''
    accum: dict
    tup: tuple

    search the first element of the tuple in the accumulator and add the second element to the list
    '''
    try:
        a, b = tup
        accum.setdefault(a, []).append(b.strip())
        return accum
    except Exception as e:
        print(e)
    return accum

def take_bussiness_name(text):
    bussiness_name_regex = r'\d{6}\s-\s(.*?)\.\n'
    match = re.search(bussiness_name_regex, text)
    if not match:
        raise Exception('Bussiness name not found in text')
    start, end = match.span()
    bussiness_name = text[start:end]
    bussiness_name = re.sub(r"\d{6}\s-\s", "", bussiness_name)
    bussiness_name = re.sub(r'\.$', "", bussiness_name)
    return bussiness_name

def map_inner_word(text, keyword, next_keyword, match):
    prefix = r'^{}\.\s*'.format(keyword) if keyword == 'Nombramientos' else  r'^{}:\s*'.format(keyword)
    suffix = r'\.\s*{}$'.format(next_keyword)
    boe_footer = r'BOLETÍN OFICIAL DEL REGISTRO MERCANTIL(.*?)https://www.boe.es'
    start, end = match.span()
    inner_text = text[start:end]
    inner_text = re.sub(prefix, '', inner_text)
    inner_text = re.sub(suffix, '', inner_text)
    inner_text = re.sub(boe_footer, '', inner_text)
    if keyword == 'Capital':
        inner_text = inner_text[:inner_text.find('Euros')]
    stripped_text = inner_text.strip()
    return stripped_text

def map_constitucion(text):
    '''
    text: string
    '''
    if not 'Constitución' in text:
        raise Exception('Word Constitución not found in text')

    constituciones_keywords = ['Comienzo de operaciones', 'Objeto social', 'Domicilio', 'Capital', 'Nombramientos', 'Datos registrales']
    data = dict()
    data = {
        'Negocio': take_bussiness_name(text).strip(),
    }
    text = text.replace('\n', ' ')
    for index in range(len(constituciones_keywords) - 1):
        keyword = constituciones_keywords[index]
        next_keyword = constituciones_keywords[index + 1]
        regex = r'{}(.*?){}'.format(keyword, next_keyword)
        match = re.search(regex, text, re.DOTALL)
        if match:
            data[keyword] = map_inner_word(text, keyword, next_keyword, match)
    return data

def take_bussiness(text):
    bussinesses_information = list(re.finditer(pattern, text, re.DOTALL))
    last_start = 0
    bussinesses = list()
    for start_business_information in range(len(bussinesses_information) - 1) :
        start_1, _ = bussinesses_information[start_business_information].span()
        start_2, _ = bussinesses_information[start_business_information + 1].span()
        last_start = start_2
        ss = text[start_1:start_2]
        bussinesses.append(ss)
    bussinesses.append(text[last_start:])
    return bussinesses

if __name__ == '__main__':
    reader = PdfReader("BORME-A-2022-121-28.pdf")
    number_of_pages = len(reader.pages)
    pdf_text = ""

    for (i, page) in enumerate(reader.pages):
        pdf_text += page.extract_text()
        
    bussinesses = take_bussiness(pdf_text)
    labeled_matches = list(map(lambda x: labeled_text(x, keywords), bussinesses))
    group_by_labeled_matches = dict()
    group_by_labeled_matches = reduce(convert, labeled_matches, group_by_labeled_matches)

    for label, bussinesses in group_by_labeled_matches.items():
        match label:
            case 'Constitución':
                for bussiness in bussinesses:
                    print(map_constitucion(bussiness))
                    time.sleep(1)
    
    