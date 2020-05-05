from bs4 import BeautifulSoup
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import react
from requests_threads import AsyncSession
import json
import sys
import getopt
import random
import string

BASE_URL = 'https://www.smartmaterials3d.com/index.php'
TOKEN = ''.join([random.choice(string.ascii_letters) for i in range(15)])

SMARTMATERIALS_DATA = json.load(open('./data.json', encoding='utf-8'))


def get_key(dictionary, val):
    for key, value in dictionary.items():
        if val == value:
            return key


def getTamanos():
    return [str(SMARTMATERIALS_DATA['tamanos'][tamano]['tamano']) for tamano in SMARTMATERIALS_DATA['tamanos'].keys()]


@inlineCallbacks
def _run(reactor, opts):
    session = AsyncSession()
    urls = []
    extractedData = []
    filteredData = []

    for material in SMARTMATERIALS_DATA['materiales'].keys():
        for color in SMARTMATERIALS_DATA['materiales'][material]['colores']:
            for tamano in SMARTMATERIALS_DATA['materiales'][material]['tamanos']:
                param = {
                    'controller': 'product',
                    'token': TOKEN,
                    'id_product': SMARTMATERIALS_DATA['materiales'][material]['id'],
                    'id_customization': 0,
                    'group[3]': SMARTMATERIALS_DATA['colores'][color]['color'],
                    'group[1]': SMARTMATERIALS_DATA['tamanos'][tamano]['tamano'],
                    'group[2]': SMARTMATERIALS_DATA['materiales'][material]['diametro']
                }

                urls.append({'request': session.post(BASE_URL, data=param),
                             'material': material, 'tamano': tamano, 'color': color})

    for response in urls:
        r = yield response['request']

        soup = BeautifulSoup(r.text, 'html.parser')

        group1 = soup.find('select', id='group_1')
        group1_options = group1.findAll('option')

        group1_options_values = []

        for option_value in group1_options:
            if option_value['value'] in getTamanos():
                group1_options_values.append(option_value['value'])

        # Se comprueba si el tamano realmente existe para el producto
        if str(SMARTMATERIALS_DATA['tamanos'][response['tamano']]['tamano']) in group1_options_values:
            group3 = soup.find('ul', id='group_3')
            color = group3.find('input', {'checked': 'checked'})['value']

            div_availability = soup.find('span', id='product-availability')

            # Se comprueba si el producto esta disponible
            if div_availability is None:
                material = get_key(
                    SMARTMATERIALS_DATA['materiales'], SMARTMATERIALS_DATA['materiales'][response['material']])
                color = get_key(
                    SMARTMATERIALS_DATA['colores'], SMARTMATERIALS_DATA['colores'][response['color']])
                tamano = get_key(
                    SMARTMATERIALS_DATA['tamanos'], SMARTMATERIALS_DATA['tamanos'][response['tamano']])

                extractedData.append(
                    {'material': material, 'color': color, 'tamano': tamano})

    # Filtrado de los datos obtenidos
    if len(opts) >= 0:
        for opt, arg in opts:
            if len(filteredData) == 0:
                filteredData = extractedData

            if opt == '-h':
                print('main.py -c <color> -m <material> -t <tamaño>')
            if opt in ('-m', '--material'):
                dataMaterial = []
                for mat in ''.join(arg.split()).split(','):
                    for x in list(filter(lambda d: d['material'].lower() in mat.lower(), filteredData)):
                        dataMaterial.append(x)
                filteredData = dataMaterial
            if opt in ('-c', '--color'):
                dataColor = []
                for col in ''.join(arg.split()).split(','):
                    for x in list(filter(lambda d: d['color'].lower() in col.lower(), filteredData)):
                        dataColor.append(x)
                filteredData = dataColor
            if opt in ('-t', '--tamano'):
                dataTamano = []
                for tam in ''.join(arg.split()).split(','):
                    for x in list(filter(lambda d: d['tamano'].lower() in tam.lower(), filteredData)):
                        dataTamano.append(x)
                filteredData = dataTamano

    print(filteredData if len(filteredData) > 0 else extractedData)


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hc:m:t:', [
                                   'color=', 'material=', 'tamano='])

        for opt, arg in opts:
            if opt in ('-h', '--help'):
                print('main.py -c <color> -m <material> -t <tamaño>')
                sys.exit(0)

        react(_run, (opts,))
    except getopt.GetoptError:
        print('main.py -c <color> -m <material> -t <tamaño>')
        sys.exit(2)
