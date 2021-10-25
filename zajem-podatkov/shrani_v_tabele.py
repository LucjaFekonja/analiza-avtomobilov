import re
import os 
import orodja


# Mapa od koder jemljemo podatke (v kateri so zbrani vsi avti)
mapa = 'zajem-podatkov/verzije'
# Mapa, v katero shranjujem podatke
mapa_obdelanih = 'zajem-podatkov/obdelani-podatki'
# Glavna csv in json datoteka
csv_datoteka = 'izluščene_informacije.csv'
json_datoteka = 'izluščene_informacije.json'
# csv in json dimenzije
csv_dimenzije = 'dimenzije.csv'
json_dimenzije = 'dimenzije.json'
# csv in json datoteka let izdelave
csv_leta = 'leta.csv'
json_leta = 'leta.json'


vzorec_znamke = r'"position": 2,\n{2}\s*?"name": "(?P<znamka>.*?)",'

vzorec_modela = r'"position": 3,\n{2}\s*?"name": "(?P<model>.*?)",'

# generacija ali verzija
vzorec_genver = r'"position": 4,\n{2}\s*?"name": "(?P<gen_ali_ver>.*?)",'

vzorec_verzije = r'"position": 5,\n{2}\s*?"name": " ?(?P<verzija>.*?)",'

vzorec_prvo_leto_proizvodnje = r'"productionDate": "(?P<prvo_leto_proizvodnje>\d{4})"'

vzorec_leta_proizodnje = r'Model Years (?P<leta>[\d{4},]*?)"'

vzorec_gorivo = r'"fuelType": "(?P<gorivo>.*?)"'

vzorec_poravnave_motorja = (
    r'<td class="tabletd" align="right"> Engine Alignment : </td> '
    r'<td class="tabletd_right"> (?P<poravnava>.*?) </td>'
)

vzorec_prostornine_motorja = r'"unitCode": "CMQ",\n\s*?"value": "(?P<prostornina_motorja>\d*?)"'

vzorec_moci_motorja = (
    r'"enginePower": \{\n\s*?'
	r'"@type": "QuantitativeValue",\n\s*?'
	r'"unitCode": "N12",\n\s*?'
	r'"value": "(?P<moc_motorja>\d*?)"'
)

vzorec_prisilnega_polnjenja_motorja = (
    r'<td class="tabletd" align="right">'
    r' Aspiration : </td> <td class="tabletd_right">'
    r' (?P<aspiracija>.*?) </td>'
)

vzorec_navora = (
    r'"torque": \{\n\s*?'
	r'"@type": "QuantitativeValue",\n\s*?'
	r'"unitCode": "NU",\n\s*?'
	r'"value": "(?P<navor>\d*?)"'
)

vzorec_100_km_h = (
    r'"accelerationTime": \{\n\s*?'
	r'"@type": "QuantitativeValue",\n\s*?'
	r'"unitCode": "SEC",\n\s*?'
	r'"value": "(?P<pospesevanje>[\d\.]*?)"'
)

vzorec_100_km_h_2 = (
    r'<td class="tabletd" align="right"> '
    r'Acceleration 0 to 100 km/h (0 to 62 mph) : '
    r'</td> <td class="tabletd_right"> (?P<pospesevanje>[\d\.]*?) s </td>'
)

vzorec_max_hitrost = (
    r'"speed": \{\n\s*?'
	r'"@type": "QuantitativeValue",\n\s*?'
	r'"unitCode": "KMH", "value": "(?P<max_hitrost>[\d\.]*?)"'
)

vzorec_max_hitrost_2 = (
    r'<td class="tabletd" width="50%" align="right"> '
    r'Top Speed : </td> <td class="tabletd_right" width="50%">'
    r' (?P<max_hitrost>[\d\.]*?) km/h or .*? Mph </td>'
)

vzorec_dimenzije = (
    r'Dimensions: Length:(?P<dolzina>[\d\.]*?) cm .*?; ?'
    r'Width:(?P<sirina>[\d\.]*?) cm .*?; ?'
    r'Height:(?P<visina>[\d\.]*?) cm'
)

vzorec_teze = (
    r'"weight": \{\n\s*?'
	r'"@type": "QuantitativeValue",\n\s*?'
	r'"unitCode": "KGM",\n\s*?'
	r'"value": "(?P<teza>\d*?)"'
)

vzorec_emisije = r'"emissionsCO2": "(?P<emisije>\d*?)"'

vzorec_porabe = r'Average consumption:(?P<poraba>[\d\.]*?) l/100km'

vzorec_porabe_2 = (
    r'"fuelConsumption": \{\n\s*?'
    r'"@type": "QuantitativeValue",\n\s*?'
	r'"unitText": "L/100 km",\n\s*?'
	r'"valueReference": "Average",\n\s*?'
	r'"value": "(?P<poraba>[\d\.]*?)"'
)

####################################################################################

# Ustvarimo slovar, ki ga bom pretvorila v csv
# --------------------------------------------
def ustvari_seznam_lastnosti():
    seznam_lastnosti = list()

    for ime_datoteke in os.listdir(mapa):
        vsebina = orodja.preberi_file(mapa, ime_datoteke)
        slovar = dict()

        verzija = re.search(vzorec_verzije, vsebina)
        genver = re.search(vzorec_genver, vsebina)
        if verzija is not None:
            # Če je avto iz generacije
            slovar['verzija'] = verzija.group('verzija')
            # Dodamo še generacijo
            slovar['generacija'] = genver.group('gen_ali_ver')
        else:
            # Če avto ni iz nobene generacije
            slovar['verzija'] = genver.group('gen_ali_ver')

        # Dodamo znamko avtomobila
        znamka = re.search(vzorec_znamke, vsebina)
        slovar['znamka'] = znamka.group('znamka')

        # Dodamo model avtomobila
        model = re.search(vzorec_modela, vsebina)
        slovar['model'] = model.group('model')

        prvo_leto = re.search(vzorec_prvo_leto_proizvodnje, vsebina)
        slovar['prvo leto proizvodnje'] = int(prvo_leto.group('prvo_leto_proizvodnje'))

        leta_proizvodnje = re.search(vzorec_leta_proizodnje, vsebina)
        slovar['leta proizvodnje'] = leta_proizvodnje.group('leta').split(',')


        gorivo = re.search(vzorec_gorivo, vsebina)
        slovar['gorivo'] = gorivo.group('gorivo')

        if re.search(vzorec_poravnave_motorja, vsebina):
            poravnava_motorja = re.search(vzorec_poravnave_motorja, vsebina)
            slovar['poravnava motorja'] = poravnava_motorja.group('poravnava')

        prostornina_motorja = re.search(vzorec_prostornine_motorja, vsebina)
        slovar['prostornina motorja'] = int(prostornina_motorja.group('prostornina_motorja'))

        moc_motorja =  re.search(vzorec_moci_motorja, vsebina)
        slovar['moč motorja'] = int(moc_motorja.group('moc_motorja'))

        if re.search(vzorec_prisilnega_polnjenja_motorja, vsebina):
            prisilno_polnenje = re.search(vzorec_prisilnega_polnjenja_motorja, vsebina)
            slovar['prisilno polnenje motorja'] = prisilno_polnenje.group('aspiracija').split(' ')[0]

        if re.search(vzorec_100_km_h, vsebina):
            pospesevanje = re.search(vzorec_100_km_h, vsebina)
            slovar['pospesevanje'] = float(pospesevanje.group('pospesevanje'))
        elif re.search(vzorec_100_km_h_2, vsebina):
            pospesevanje_2 = re.search(vzorec_100_km_h, vsebina)
            slovar['pospesevanje'] = float(pospesevanje_2.group('pospesevanje'))

        if re.search(vzorec_max_hitrost, vsebina):
            max_hitrost = re.search(vzorec_max_hitrost, vsebina)
            slovar['max hitrost'] = float(max_hitrost.group('max_hitrost'))
        elif re.search(vzorec_max_hitrost_2, vsebina):
            max_hitrost_2 = re.search(vzorec_max_hitrost_2, vsebina)
            slovar['max hitrost'] = float(max_hitrost_2.group('max_hitrost'))
 

        if re.search(vzorec_navora, vsebina):
            navor = re.search(vzorec_navora, vsebina)
            slovar['navor'] = int(navor.group('navor'))

        visina = re.search(vzorec_dimenzije, vsebina)
        slovar['visina'] = float(visina.group('visina'))

        sirina = re.search(vzorec_dimenzije, vsebina)
        slovar['sirina'] = float(sirina.group('sirina'))

        dolzina = re.search(vzorec_dimenzije, vsebina)
        slovar['dolzina'] = float(dolzina.group('dolzina'))
        
        if re.search(vzorec_teze, vsebina):
            teza = re.search(vzorec_teze, vsebina)
            slovar['teza'] = int(teza.group('teza'))

        if re.search(vzorec_emisije, vsebina):
            emisije = re.search(vzorec_emisije, vsebina)
            slovar['emisije'] = float(emisije.group('emisije'))

        poraba1 = re.search(vzorec_porabe, vsebina)
        poraba2 = re.search(vzorec_porabe_2, vsebina)
        if poraba1:
            poraba = poraba1.group('poraba')
        elif poraba2:
            poraba = poraba2.group('poraba')
        if not poraba == '':
            slovar['poraba'] = float(poraba)
        
        seznam_lastnosti.append(slovar)
    return seznam_lastnosti


def leta_proizvodnje():
    leta = []
    for slovar in ustvari_seznam_lastnosti():
        leta_proizvodnje = slovar['leta proizvodnje']
        verzija = slovar['verzija']

        for leto in leta_proizvodnje:
            leta.append(
                {'verzija' : verzija,
                'leto' : int(leto)}
            )
    return leta


orodja.naredi_csv(
        ['znamka', 
        'model', 
        'generacija', 
        'verzija', 
        'prvo leto proizvodnje', 
        'gorivo',
        'poravnava motorja',
        'prostornina motorja',
        'moč motorja',
        'prisilno polnenje motorja',
        'pospesevanje',
        'max hitrost',
        'navor',
        'emisije',
        'poraba'],    
        ustvari_seznam_lastnosti(),
        mapa_obdelanih, 
        csv_datoteka
        )

#orodja.naredi_csv(
#    ['verzija', 'visina', 'sirina', 'dolzina', 'teza'],
#    ustvari_seznam_lastnosti(),
#    mapa_obdelanih,
#    csv_dimenzije
#)

#orodja.naredi_csv(
#    ['verzija', 'leto'],
#    leta_proizvodnje(),
#    mapa_obdelanih, 
#    csv_leta
#)
#