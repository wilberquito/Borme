from PyPDF2 import PdfReader
import re
import time

reader = PdfReader("BORME-A-2022-121-28.pdf")
number_of_pages = len(reader.pages)
pdf_text = ""

for (i, page) in enumerate(reader.pages):
    pdf_text += page.extract_text()

pattern = re.compile(r"\d{6}\s-(.*?)\(\d{2}\.\d{2}.\d{2}\)", re.DOTALL)
matches = pattern.findall(pdf_text)

print(len(matches))

for match in matches:
    print(match)
    print()
    