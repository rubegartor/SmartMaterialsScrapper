from bs4 import BeautifulSoup
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import react
from requests_threads import AsyncSession
import json

BASE_URL = 'https://www.smartmaterials3d.com/index.php'

SMARTMATERIALS_DATA = json.load(open('./data.json', encoding='utf-8'))

def get_key(dictionary, val): 
    for key, value in dictionary.items(): 
           if val == value: 
               return key 

@inlineCallbacks
def _run(reactor):
    urls = []
    session = AsyncSession()

    for material in SMARTMATERIALS_DATA['materiales'].keys():
        for color in SMARTMATERIALS_DATA['materiales'][material]['colores']:
            for tamano in SMARTMATERIALS_DATA['materiales'][material]['tamanos']:
                param = {
                    'controller': 'product',
                    'token': SMARTMATERIALS_DATA['token'],
                    'id_product': SMARTMATERIALS_DATA['materiales'][material]['id'],
                    'id_customization': 0,
                    'group[3]': SMARTMATERIALS_DATA['colores'][color]['color'],
                    'group[1]': SMARTMATERIALS_DATA['tamanos'][tamano]['tamano'],
                    'group[2]': SMARTMATERIALS_DATA['materiales'][material]['diametro']
                }

                urls.append({'request': session.post(BASE_URL, data=param), 'material': material, 'tamano': tamano, 'color': color})

    for response in urls:
        r = yield response['request']

        soup = BeautifulSoup(r.text, 'html.parser')

        div = soup.find('span', id="product-availability")

        if div is None:
            material = get_key(SMARTMATERIALS_DATA['materiales'], SMARTMATERIALS_DATA['materiales'][response['material']])
            color = get_key(SMARTMATERIALS_DATA['colores'], SMARTMATERIALS_DATA['colores'][response['color']])
            tamano = get_key(SMARTMATERIALS_DATA['tamanos'], SMARTMATERIALS_DATA['tamanos'][response['tamano']])
            # TrEmEnDo FoRmAtEaDo dE tExTo OwO
            print('[DISPONIBLE][{}][{}gr] - {}'.format(material, tamano, color))


if __name__ == "__main__":
    react(_run)