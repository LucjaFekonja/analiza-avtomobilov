import csv
import json
import os
import requests


def url_v_niz(url):
    ''' Sprejme niz (url), vrne vsebino spletne strani kot niz '''
    try:
        odziv = requests.get(url)                   # Če je odziv 200, ne potrebuje exceptiona
    except requests.exceptions.ConnectionError:
        print('Napaka pri povezovanju do:', url)    # Če pride do napake pri povezovanju
        return None
    
    if odziv.status_code == requests.codes.ok:      # Če ni bilo errorja
        return odziv.text                           # Vrne vsebino spletne strani
    else:
        print('Napaka pri prenosu strani:', url)


def niz_v_file(niz, mapa, datoteka):
    ''' niz pretvori v datoteko in so shrani v mapo, če že obstaja, naredi novo'''
    os.makedirs(mapa, exist_ok=True)      
    path = os.path.join(mapa, datoteka)    # Ustvari path do datoteke v katero shranjujemo
    with open(path, 'w', encoding='utf-8') as dat:
        dat.write(niz)                     # V datoteko vpiši niz
    return None


def shrani_stran(url, mapa, datoteka):
    ''' Vrne vsebino datoteke kot niz '''
    niz = url_v_niz(url)
    niz_v_file(niz, mapa, datoteka)
    return None


def preberi_file(mapa, datoteka):
    path = os.path.join(mapa, datoteka)
    with open(path, 'r', encoding='utf-8') as dat:
        return dat.read()


def naredi_csv(imena_lastnosti, seznam_slovarjev, mapa, datoteka):
    """
    Funkcija v csv datoteko shrani vrednosti iz slovarja,
    shrani v vrstice v istem vrstnem redu kot v parametru 'imena_lastnosti'.
    """
    os.makedirs(mapa, exist_ok=True)
    path = os.path.join(mapa, datoteka)

    with open(path, 'w', encoding='utf-8') as csv_dat:
        writer = csv.DictWriter(csv_dat, fieldnames=imena_lastnosti, extrasaction="ignore")
        writer.writeheader()
        for slovar in seznam_slovarjev:
            writer.writerow(slovar)
    return None


def zapisi_json(slovar, mapa, datoteka):
    '''Iz danega objekta ustvari JSON datoteko.'''
    os.makedirs(mapa, exist_ok=True)
    path = os.path.join(mapa, datoteka)

    with open(path, 'w', encoding='utf-8') as json_datoteka:
        json.dump(slovar, json_datoteka, indent=4, ensure_ascii=False)