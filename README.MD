# SmartMaterialsScrapper

Web Scrapper para obtener los productos disponibles en la tienda web de SmartMaterials3D (https://www.smartmaterials3d.com/)

## Instalacion:
```bash-script
pip3 install -r requirements.txt
```

## Configuración:
Para poder ejecutar el proceso necesitamos obtener un token que nos proporciona la web.

1. Abre las herrmientas de desarrollador (F12) y colocate sobre la pestaña "Network"
2. Abre el enlace: https://www.smartmaterials3d.com/pla-filamento y selecciona uno de los colores disponibles.
3. En el panel lateral de la pestaña "Network", aparecerá un nuevo item con nombre: "index.php?controller=....." seleccionalo.
4. En el apartado: "Query String Parameters" copia el token.
5. En el archivo data.json sustituye "token": "TU_TOKEN" por el token que has copiado