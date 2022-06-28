from PyPDF2 import PdfReader
import re
from functools import reduce

keywords = ['Disolución', 'Cambio de denominación social', 'Constitución']
reader = PdfReader("BORME-A-2022-121-28.pdf")
number_of_pages = len(reader.pages)
pdf_text = ""

for (i, page) in enumerate(reader.pages):
    pdf_text += page.extract_text()

pattern = re.compile(r"\d{6}\s-(.*?)\(\d{2}\.\d{2}.\d{2}\)", re.DOTALL)
matches = pattern.findall(pdf_text)

print(f"Number of items: {len(matches)}")

def is_target(text, keywords):
    for keyword in keywords:
        if keyword in text:
            return True
    return False

def map_match(text, keywords):
    for keyword in keywords:
        if keyword in text:
            return (keyword, text)
    return ('Otros', text)

labeled_matches = list(map(lambda x: map_match(x, keywords), matches))
group_by_labeled_matches = dict()

def convert(accum, tup):
    a, b = tup
    accum.setdefault(a, []).append(b.strip())
    return accum

mapped_matches_dict = reduce(convert, labeled_matches, group_by_labeled_matches)

print(mapped_matches_dict.keys())
