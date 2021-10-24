import re
import orodja
import os

prva_stran = 'prva_stran.html'
ta_mapa = 'zajem-podatkov'
mapa_znamk = 'zajem-podatkov/znamke'
mapa_modelov_z_generacijami = 'zajem-podatkov/generacije'
mapa_modelov = 'zajem-podatkov/modeli'
mapa_verzij = 'zajem-podatkov/verzije'


''' Naj pojasnim to katastrofo. Ko odpremo stran https://www.ultimatespecs.com/
najdemo vrsto znamk avtomobilov. Vsak od njih nosi povezavo na svojo spletno
stran, ki jih shranimo z naslednjo funkcijo v mapo 'znamke'. ''' 

def ustvari_seznam_znamk(vsebina):
    vzorec_znamk = (
        r'<a href="/car-specs/.*?-models">\n'
        r'<div class="col-md-2 col-sm-3 col-xs-4 col-4">\n'
        r'<div class="home_brand">\n'
        r'<div class="home_brand_over"><h2>(?P<znamka>.*?) ?</h2></div>'
    )
    seznam_datotek = list()
    for zadetek in re.finditer(vzorec_znamk, vsebina):
        # Ustvarim seznam imen datotek znamk, na katerega se bom kasneje sklicovala 
        ime_znamke_v_url = zadetek.group('znamka').replace(' ', '-')
        ime_datoteke = ime_znamke_v_url.lower() + '.html'
        seznam_datotek.append(ime_datoteke)
        # Shranim še spletne strani vsake znamke v posamezno datoteko
        url = rf'https://www.ultimatespecs.com/car-specs/{ime_znamke_v_url}-models'
        orodja.shrani_stran(url, mapa_znamk, ime_datoteke)
    return seznam_datotek


''' Na spletni strani posamezne znamke smo seznanjeni z vsemi njenimi modeli. 
Ker lahko imajo nekateri modeli več generacij, nas klik na le-te popelje na
spletno stran vseh modelov te generacije. Spodnja funkcija shranjuje takšne
spletne stranji. '''

def ustvari_seznam_modelov_z_generacijami(vsebina):
    vzorec_generacij = (
        r'href="/car-specs/(?P<url>(?P<znamka>.*?)[-models]?[/\w*\d*]?/.*?)"> '
        r'<div class="home_models">\n'
        r'<div class="home_models_over">\n'
        r'<h2>\n'
        r'(?P<model>.*?) </h2>\n'
        r'<p>\n'
        r'From \d{4}, \d*? Generations, \d*? Models </p>\n'
        r'</div>\n'
    )
    seznam_datotek_modelov_z_generacijami = list()
    for model in re.finditer(vzorec_generacij, vsebina):
        # Spet ustvarjam seznam imen datotek, na katerega se hočem pol sklicovat
        ime_datoteke = (
            model.group('znamka') + 
            '-' +
            model.group('model') + 
            '.html').replace(' ', '-').replace('/', '-').lower()
        seznam_datotek_modelov_z_generacijami.append(ime_datoteke)
        # Pa še shranjujem html-je v mapo 'generacije'
        url = model.group('url')
        url_gen = rf'https://www.ultimatespecs.com/car-specs/{url}'
        orodja.shrani_stran(url_gen, mapa_modelov_z_generacijami, ime_datoteke)
    return seznam_datotek_modelov_z_generacijami


''' Seveda hočemo shraniti tudi spletne strani modelov vsake generacije.
Naslednja funkcija shranjuje vse modele, ki so našteti v kateremkoli 
dokumentu mape generacije v mapo 'modeli'. '''

def ustvari_seznam_modelov_gen(vsebina):
    vzorec_iz_mape_generacije = (
        r'<div class="home_models_line gene">'
        r'<a name=".*?"></a>'
        r'<h2>.*?</h2>'
        r'<a class=.col-md-3 col-sm-4 col-xs-4 col-4. '
        r'href="(?P<url>.*?)">'
        r'<div class=.home_models.>'
        r'<div class=.home_models_over.><div class=.centered.>'
        r'<h3>(?P<model>.+?)</h3>'
        r'<p>\d* Versions</p></div></div>'
    )
    seznam_datotek_modelov = list()
    for zadetek in re.finditer(vzorec_iz_mape_generacije, vsebina):
        model = zadetek.group('model')
        print(model)
        ime_datoteke = model.lower().replace(' ', '-').replace('/', '-') + '.html'
        seznam_datotek_modelov.append(ime_datoteke)
        url = zadetek.group('url')
        url_mod = rf'https://www.ultimatespecs.com{url}'
        orodja.shrani_stran(url_mod, mapa_modelov, ime_datoteke)
    return seznam_datotek_modelov


''' Nekateri modeli pa niso razdeljeni na generacije. V tem primeru nas 
klik na ikono popelje na podobno spletno mesto kot znamka > generacija > model, 
le da v tem primeru 'zmanjka' izbira generacije. Tudi te shranjujemo v mapo 'modeli'. '''

def ustvari_seznam_modelov_zna(vsebina):
    vzorec_iz_mape_znamke = (
        r'href="(?P<url>/car-specs/(?P<znamka>.*?)[-models]?[/\w*\d*]?/.*?)"> '
        r'<div class="home_models">\n'
        r'<div class="home_models_over">\n'
        r'<h2>\n'
        r'(?P<model>.+?) ?</h2>\n'
        r'<p>\n'
        r'\d*? Versions </p>\n'
        r'</div>\n'
    )
    seznam_datotek_modelov = list()
    for zadetek in re.finditer(vzorec_iz_mape_znamke, vsebina):
        model = zadetek.group('model')
        url = zadetek.group('url')
        ime_datoteke = model.lower().replace(' ', '-').replace('/', '-') + '.html'
        seznam_datotek_modelov.append(ime_datoteke)
        cel_url = rf'https://www.ultimatespecs.com{url}'
        orodja.shrani_stran(cel_url, mapa_modelov, ime_datoteke)
    return seznam_datotek_modelov


''' Zdaj, ko imamo vse modele zbrane v skupni mapi nam še ostane samo
 pobrati vse verzije avtomobilov, ki so na vseh spletnih straneh podane
  na enak način. Shranjujem jih v mapo 'verzije'. '''

def končni_seznam_verzij(vsebina):
    vzorec = (
        r'<td><a href="/car-specs/(?P<url>.*?).html"> (?P<verzija>.+?)</a> Specs</td>'
    )
    seznam_verzij = list()
    #print(list(re.finditer(vzorec, vsebina)))
    for zadetek in list(re.finditer(vzorec, vsebina)):
        verzija = zadetek.group('verzija')
        ime_datoteke = verzija.lower().replace(' ', '-').replace('/', '-').replace('"', '') + '.html'
        seznam_verzij.append(ime_datoteke)
        url = zadetek.group('url')
        cel_url = rf'https://www.ultimatespecs.com/car-specs/{url}.html'
        orodja.shrani_stran(cel_url, mapa_verzij, ime_datoteke)
    return seznam_verzij


def poberi(mapa, funkcija):
    vse_v_mapi = os.listdir(mapa)
    for datoteka in vse_v_mapi:
        funkcija(orodja.preberi_file(mapa, datoteka))

def zagon():
    ''' V to funkcijo je združen celoten proces pobiranja podatkov. '''
    ustvari_seznam_znamk(orodja.preberi_file(ta_mapa, prva_stran))
    poberi(mapa_znamk, ustvari_seznam_modelov_z_generacijami)
    poberi(mapa_znamk, ustvari_seznam_modelov_zna)
    poberi(mapa_modelov_z_generacijami, ustvari_seznam_modelov_gen)
    poberi(mapa_modelov, končni_seznam_verzij)

