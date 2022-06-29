import re

def take_submission_date(text):
    pass
s = '''
300894 - 2020 MOLINA INSTALACIONES ELECTRICAS SL.
Constituci�n.  Comienzo de operaciones: 1.07.22. Objeto social: Instalaciones el�ctricas. Domicilio: CALLE ATLANTIDA N�mero79
(VALDEMORO). Capital: 3.000,00 Euros.  Nombramientos.  Adm. Unico: MOLINA DUE�AS SERGIO.  Datos registrales. T 43689 , F
75, S 8, H M 771237, I/A 1 (20.06.22).
'''
regex = r'\(\s*\d{2}\.\d{2}\.\d{2}\s*\)'

s = re.search(regex, s)

print(s)