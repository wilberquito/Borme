from ast import pattern
from base64 import decode
from PyPDF2 import PdfReader
import re
from functools import reduce
import json

otros = 'Otros'
keywords = ['Disolución', 'Cambio de domicilio social', 'Constitución']
pattern = r'\d{6}\s*-'

dissolution = 'disolution'
registerd_office = 'registeredOffice'
constitution = 'constitution'
others = 'others'
submission_date = 'submissionDate'
bussines_name = 'bussinesName'
cause = 'cause'
address = 'address'
operations_start = 'operationsStart'
social_object = 'socialObject'
domicile = 'domicile'
capital = 'capital'
appointments = 'appointments'
registry_data = 'registryData'

mapping_keywords = {
    'Disolución': dissolution,
    'Cambio de domicilio social': registerd_office,
    'Constitución': constitution,
    'Comienzo de operaciones': operations_start,
    'Objeto social': social_object,
    'Domicilio': domicile,
    'Capital': capital,
    'Nombramientos': appointments,
    'Datos registrales': registry_data,
    'Otros': others
}

def is_target(text, keywords):
    '''
    Search if any keyword is in the text
    '''
    for keyword in keywords:
        if keyword in text:
            return True
    return False

def labeled_text(text, keywords):
    '''
    return a labeled tuple with the text and the keyword
    '''
    for keyword in keywords:
        if keyword in text:
            return (keyword, text)
    return (otros, text)

def convert(accum, tup):
    '''
    Search the first element of the tuple in the accumulator 
    and add the second element to the list
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
    bussiness_name = re.sub(r'\d{6}\s-\s', '', bussiness_name)
    bussiness_name = re.sub(r'\.$', '', bussiness_name)
    return bussiness_name.strip()

def take_submission_date(text):
    submission_date_regex = r'\(\s*\d{2}\.\d{2}\.\d{2}\s*\)'
    match = re.search(submission_date_regex, text)
    if not match:
        raise Exception('Submission date not found in text')
    start, end = match.span()
    submission_date = text[start:end]
    submission_date = submission_date.replace('(', '')
    submission_date = submission_date.replace(')', '')
    return submission_date.strip()

def map_inner_word(text, keyword, next_keyword, match):
    prefix = r'^{}\.\s*'.format(keyword) if keyword in ['Nombramientos', 'Cambio de domicilio social'] else r'^{}:\s*'.format(keyword)
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
    Extracts the constitucion data from the text
    '''
    if not 'Constitución' in text:
        raise Exception('Word Constitución not found in text')

    constituciones_keywords = ['Comienzo de operaciones', 'Objeto social', 'Domicilio', 'Capital', 'Nombramientos', 'Datos registrales']
    data = take_metadata(text)
    text = text.replace('\n', ' ')
    for index in range(len(constituciones_keywords) - 1):
        keyword = constituciones_keywords[index]
        next_keyword = constituciones_keywords[index + 1]
        regex = r'{}(.*?){}'.format(keyword, next_keyword)
        match = re.search(regex, text, re.DOTALL)
        if match:
            data[mapping_keywords[keyword]] = map_inner_word(text, keyword, next_keyword, match)
    return data

def map_change_of_registered_office(text):
    if not 'Cambio de domicilio social' in text:
        raise Exception('Word Constitución not found in text')
    
    start = 'Cambio de domicilio social'
    end = 'Datos registrales'
    data = take_metadata(text)
    match = re.search(r'{}(.*?){}'.format(start, end), text, re.DOTALL)
    if match:
        data[address] = map_inner_word(text, start, end, match)
    return dict() if data is None else data

def map_disolucion(text):
    if not 'Disolución' in text:
        raise Exception('Word Disolución not found in text')
    
    start = 'Disolución'
    end = 'Datos registrales'
    data = take_metadata(text)
    match = re.search(r'{}(.*?){}'.format(start, end), text, re.DOTALL)
    if match:
        data[cause] = map_inner_word(text, start, end, match)
    return dict() if data is None else data

def take_metadata(text):
    '''
    Extracts 'negocio' and 'fecha de envio' from the text
    '''
    metadatada = dict()
    metadatada[bussines_name] = take_bussiness_name(text)
    metadatada[submission_date] = take_submission_date(text)
    return metadatada

def take_bussinesses(text):
    '''
    Returns a list of paragraphs, where each paragraph represents bussiness movement
    '''
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

def map_labeled_bussinesses(dic):
    label, paragraphs = dic
    bussiness_label = mapping_keywords[label]
    data = dict()
    for paragraph in paragraphs:
        match label:
            case 'Constitución':
                data.setdefault(bussiness_label, []).append(map_constitucion(paragraph))
            case 'Cambio de domicilio social':
                data.setdefault(bussiness_label, []).append(map_change_of_registered_office(paragraph))
            case 'Disolución':
                data.setdefault(bussiness_label, []).append(map_disolucion(paragraph))
    return data

if __name__ == '__main__':
    reader = PdfReader('BORME-A-2022-121-28.pdf')
    number_of_pages = len(reader.pages)
    pdf_text = ''

    for (i, page) in enumerate(reader.pages):
        pdf_text += page.extract_text()
        
    bussinesses = take_bussinesses(pdf_text)
    labeled_paragraphs = list(map(lambda x: labeled_text(x, keywords), bussinesses))
    dict_paragraphs = dict()
    dict_paragraphs = reduce(convert, labeled_paragraphs, dict_paragraphs)

    data = dict()
    for label, bussinesses in dict_paragraphs.items():
        data.update(map_labeled_bussinesses((label, bussinesses)))
    
    with open('dump.json', 'w+', encoding='utf-8') as file:
        dump = json.dumps(data, ensure_ascii=False, indent=4).encode('utf-8')
        file.write(dump.decode('utf-8'))