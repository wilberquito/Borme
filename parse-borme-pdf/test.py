import re

s = 'BOLETÍN OFICIAL DEL REGISTRO MERCANTIL Núm. 121 Lunes 27 de junio de 2022 Pág. 31440 cve: BORME-A-2022-121-28  Verificable en https://www.boe.es  3.100,00'
regex = r'BOLETÍN OFICIAL DEL REGISTRO MERCANTIL(.*?)https://www.boe.es'

s = re.sub(regex, '', s)

print(s)