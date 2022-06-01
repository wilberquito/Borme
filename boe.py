import requests

date_format = "%Y%m%d"
target_date = "20141006"
boe_diario_base = "https://www.boe.es/diario_borme/xml.php?id=BORME-S-{date}"


if __name__ == '__main__':
    url = boe_diario_base.format(date=target_date)
    response = requests.get(url)
    print(response.content)
    