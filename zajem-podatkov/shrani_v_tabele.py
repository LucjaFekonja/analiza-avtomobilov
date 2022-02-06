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

vzorec_prostornine_motorja = r'"unitCode": "CMQ",\n\s*?"value": "(?P<prostornina_motorja>.*?)"'

vzorec_prostornine_motorja_2 = (
    r'"engineDisplacement": \{\n\s*?'
	r'"@type": "QuantitativeValue"\n\s*?,'
	r'"unitCode": "CMQ",\n\s*?'
	r'"value": "(?P<prostornina_motorja>[\d\.]*?)"'
)

vzorec_moci_motorja = (
    r'"enginePower": \{\n\s*?'
	r'"@type": "QuantitativeValue",\n\s*?'
	r'"unitCode": "N12",\n\s*?'
	r'"value": "(?P<moc_motorja>[\d\.]*?)"'
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
    r'Dimensions: Length:(?P<dolzina>[\d\.]+?) cm .*?'
    r'Width:(?P<sirina>[\d\.]+?) cm .*?'
    r'Height:(?P<visina>[\d\.]+?) cm'
)

vzorec_teze = (
    r'"weight": \{\n\s*?'
	r'"@type": "QuantitativeValue",\n\s*?'
	r'"unitCode": "KGM",\n\s*?'
	r'"value": "(?P<teza>\d*?)"'
)

vzorec_emisije = r'"emissionsCO2": "(?P<emisije>[\d\.]*?)"'

vzorec_emisije_2 = (
    r'<td class="tabletd" align="right"> '
    r'CO2 emissions : </td> '
    r'<td class="tabletd_right"> (?P<emisije>[\d\.]*?) g/Km \(estimate\) </td>'
)

vzorec_porabe = r'Average consumption:(?P<poraba>[\d\.]*?) l/100km'

vzorec_porabe_2 = (
    r'"fuelConsumption": \{\n\s*?'
    r'"@type": "QuantitativeValue",\n\s*?'
	r'"unitText": "L/100 km",\n\s*?'
	r'"valueReference": "Average",\n\s*?'
	r'"value": "(?P<poraba>[\d\.]*?)"'
)

####################################################################################

def dodaj_v_slovar(vzorec, ime_grupe, vsebina, slovar, ključ):
    if re.search(vzorec, vsebina):
        x = re.search(vzorec, vsebina)
        slovar[str(ključ)] = x.group(str(ime_grupe))

def dodaj_v_slovar_float(vzorec, ime_grupe, vsebina, slovar, ključ):
    if re.search(vzorec, vsebina):
        x = re.search(vzorec, vsebina)
        if x.group(str(ime_grupe)) != '':
            slovar[str(ključ)] = float(x.group(str(ime_grupe)))


# Ustvarimo slovar, ki ga bom pretvorila v csv
# --------------------------------------------
def ustvari_seznam_lastnosti():
    seznam_lastnosti = list()

    for ime_datoteke in os.listdir(mapa):
        vsebina = orodja.preberi_file(mapa, ime_datoteke)
        slovar = dict()

        verzija = re.search(vzorec_verzije, vsebina)
        generacija_ali_verzija = re.search(vzorec_genver, vsebina)
        if verzija is not None:
            # Če je avto iz generacije
            slovar['verzija'] = verzija.group('verzija')
            # Dodamo še generacijo
            slovar['generacija'] = generacija_ali_verzija.group('gen_ali_ver')
        else:
            # Če avto ni iz nobene generacije
            slovar['verzija'] = generacija_ali_verzija.group('gen_ali_ver')

        # Dodamo znamko avtomobila
        dodaj_v_slovar(vzorec_znamke, 'znamka', vsebina, slovar, 'znamka')
        # Dodamo model avtomobila
        dodaj_v_slovar(vzorec_modela, 'model', vsebina, slovar, 'model')

        dodaj_v_slovar_float(vzorec_prvo_leto_proizvodnje, 'prvo_leto_proizvodnje', vsebina, slovar, 'prvo leto proizvodnje')
        dodaj_v_slovar(vzorec_leta_proizodnje, 'leta', vsebina, slovar, 'leta proizvodnje')
        dodaj_v_slovar(vzorec_gorivo, 'gorivo', vsebina, slovar, 'gorivo')
        dodaj_v_slovar(vzorec_poravnave_motorja, 'poravnava', vsebina, slovar, 'poravnava motorja')
        dodaj_v_slovar_float(vzorec_prostornine_motorja, 'prostornina_motorja', vsebina, slovar, 'prostornina motorja')
        dodaj_v_slovar_float(vzorec_moci_motorja, 'moc_motorja', vsebina, slovar, 'moč motorja')
        dodaj_v_slovar(vzorec_prisilnega_polnjenja_motorja, 'aspiracija', vsebina, slovar, 'prisilno polnenje motorja')
        dodaj_v_slovar_float(vzorec_100_km_h, 'pospesevanje', vsebina, slovar, 'pospesevanje')
        dodaj_v_slovar_float(vzorec_100_km_h_2, 'pospesevanje', vsebina, slovar, 'pospesevanje')
        dodaj_v_slovar_float(vzorec_max_hitrost, 'max_hitrost', vsebina, slovar, 'max hitrost')
        dodaj_v_slovar_float(vzorec_max_hitrost_2, 'max_hitrost', vsebina, slovar, 'max hitrost')
        dodaj_v_slovar_float(vzorec_navora, 'navor', vsebina, slovar, 'navor')
        dodaj_v_slovar_float(vzorec_emisije, 'emisije', vsebina, slovar, 'emisije')
        dodaj_v_slovar_float(vzorec_emisije_2, 'emisije', vsebina, slovar, 'emisije')
        dodaj_v_slovar(vzorec_porabe, 'poraba', vsebina, slovar, 'poraba')
        dodaj_v_slovar(vzorec_porabe_2, 'poraba', vsebina, slovar, 'poraba')
        if slovar['poraba'] != '':
            slovar['poraba'] = float(slovar['poraba'])

        dodaj_v_slovar(vzorec_dimenzije, 'visina', vsebina, slovar, 'višina')
        dodaj_v_slovar(vzorec_dimenzije, 'sirina', vsebina, slovar, 'širina')
        dodaj_v_slovar(vzorec_dimenzije, 'dolzina', vsebina, slovar, 'dolžina')
        dodaj_v_slovar(vzorec_teze, 'teza', vsebina, slovar, 'teža')
        

        seznam_lastnosti.append(slovar)
    return seznam_lastnosti


def leta_proizvodnje():
    leta = []
    for slovar in ustvari_seznam_lastnosti():
        leta_proizvodnje = slovar['leta proizvodnje'].split(',')
        znamka = slovar['znamka']
        model = slovar['model']
        if 'generacija' in slovar.keys():
            generacija = slovar['generacija']
        else:
            generacija = ''
        verzija = slovar['verzija']


        for leto in leta_proizvodnje:
            leta.append(
                {
                    'znamka' : znamka,
                    'model' : model,
                    'generacija' : generacija,
                    'verzija' : verzija,
                    'leto' : int(leto)
                }
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

orodja.naredi_csv(
    ['znamka', 
    'model', 
    'generacija',
    'verzija', 
    'višina', 
    'širina', 
    'dolžina', 
    'teža'],
    ustvari_seznam_lastnosti(),
    mapa_obdelanih,
    csv_dimenzije
)

orodja.naredi_csv(
   ['znamka', 
    'model', 
    'generacija',
    'verzija', 
    'leto'],
    leta_proizvodnje(),
    mapa_obdelanih, 
    csv_leta
)