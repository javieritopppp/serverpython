from selenium import webdriver
from urlparse import urlparse
import datetime
import pymongo
import random
import string

import time

CHROMEDRIVER_PATH="/app/.chromedriver/bin/chromedriver"
GOOGLE_CHROME_BIN="/app/.apt/usr/bin/google-chrome"


# Realiza una busqueda por nombre en milanuncios
# Devuelve el enlace encontrado o 0 en caso de no encontrarlo
def buscar_milanuncios(articulo, max_price, driver, low_price=0):
    driver.get("https://www.milanuncios.com/anuncios/" + articulo + ".htm?fromSearch=1&desde=" + str(
        low_price) + "&hasta=" + str(max_price))

    time.sleep(2)

    try:
        return driver.find_elements_by_class_name("aditem-detail-title")
    except:
        return 0


# Realiza una busqueda por nombre en wallapop
# Devuelve el enlace encontrado o 0 en caso de no encontrarlo
def buscar_wallapop(articulo, max_price, driver, low_price=0):
    driver.get(
        "https://es.wallapop.com/search?dist=400&publishDate=any&kws=" + articulo + "&order=salePrice-asc&minPrice=" + str(
            low_price) + "&maxPrice=" + str(max_price))

    time.sleep(3)

    try:
        return driver.find_elements_by_xpath("//a[.//div[@class='card-product-content']]")
    except:
        return 0


# Realiza una busqueda por nombre en cash converters
# Devuelve el enlace encontrado o 0 en caso de no encontrarlo
def buscar_cashconverters(articulo, max_price, driver, low_price=0):
    driver.get("https://www.cashconverters.es/es/es/search/?q=" + articulo + "&lang=es&pmin=" + str(
        low_price) + "&pmax=" + str(max_price))

    time.sleep(2)

    try:
        return driver.find_elements_by_class_name("main-link")
    except:
        return 0


# Comprueba el precio de un articulo
# Devuelve el precio o 0 en caso de error
def check_precio(link, driver):
    driver.get(link)
    o = urlparse(link)
    if o.hostname == "www.milanuncios.com":
        try:
            time.sleep(2)
            return driver.find_element_by_class_name("pagAnuPrecioTexto").get_attribute("innerHTML").split(" ")[0]
        except:
            return 0
    elif o.hostname == "es.wallapop.com":
        try:
            time.sleep(3)
            return driver.find_element_by_class_name("card-product-detail-price").get_attribute("innerHTML").split(" ")[
                0]
        except:
            return 0
    elif o.hostname == "www.cashconverters.es":
        try:
            time.sleep(2)
            return driver.find_element_by_class_name("price-sales").get_attribute("innerHTML").split(",")[
                0]
        except:
            return 0


# Devuelve la lista de deseos de la base de datos
def descargar_deseos():
    myclient = pymongo.MongoClient("mongodb://javieritopppp:javi123456@ds237848.mlab.com:37848/miapp-arqsoft")
    mydb = myclient["miapp-arqsoft"]
    mycol = mydb["Deseo"]

    return mycol


# Elimina un deseo de la base de datos
def borrar_deseo(id):
    myclient = pymongo.MongoClient("mongodb://javieritopppp:javi123456@ds237848.mlab.com:37848/miapp-arqsoft")
    mydb = myclient["miapp-arqsoft"]
    mycol = mydb["deseos"]
    myquery = {"_id": id}

    mycol.delete_one(myquery)


def randomString(stringLength=10):
    letras = string.ascii_lowercase
    return ''.join(random.choice(letras) for i in range(stringLength))

# Guarda un aviso en la base de datos
def crear_aviso(link, id):
    myclient = pymongo.MongoClient("mongodb://javieritopppp:javi123456@ds237848.mlab.com:37848/miapp-arqsoft")
    mydb = myclient["miapp-arqsoft"]
    mycol = mydb["avisos"]

    mydict = {"link": link, "id": id, "visto": False, "_id": randomString(10), "block":False}

    mycol.insert_one(mydict)


def existe_aviso(link, id):
    myclient = pymongo.MongoClient("mongodb://javieritopppp:javi123456@ds237848.mlab.com:37848/miapp-arqsoft")
    mydb = myclient["miapp-arqsoft"]
    mycol = mydb["avisos"]

    if mycol.find_one({"id": id, "link": link}):
        return True
    else:
        return False


# Devuelve los seguimientos de la base de datos
def descargar_seguimientos():
    myclient = pymongo.MongoClient("mongodb://javieritopppp:javi123456@ds237848.mlab.com:37848/miapp-arqsoft")
    mydb = myclient["miapp-arqsoft"]
    mycol = mydb["Seguimiento"]

    return mycol


# Almacena el valor de un articulo en el momento
def crear_valor_seg(id, valor):
    myclient = pymongo.MongoClient("mongodb://javieritopppp:javi123456@ds237848.mlab.com:37848/miapp-arqsoft")
    mydb = myclient["miapp-arqsoft"]
    mycol = mydb["valorSeg"]

    mydict = {"id": id, "valor": valor, "fecha": unicode(datetime.datetime.now())}

    mycol.insert_one(mydict)

def realizar_busqueda():
    options = webdriver.ChromeOptions()
    options.binary_location = GOOGLE_CHROME_BIN
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument("headless")
    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,chrome_options=options)
    deseos = descargar_deseos()
    seguimientos = descargar_seguimientos()

    for deseo in deseos.find():
        articulo = deseo["articulo"]
        low_price = deseo["lowPrice"]
        max_price = deseo["maxPrice"]
        wallapop = deseo["wallapop"]
        milanuncios = deseo["milanuncios"]
        cash = deseo["cash"]
        id = deseo["_id"]
        print "deseo: ",articulo
        if wallapop:
            links = buscar_wallapop(articulo, max_price, driver, low_price)
            if links != 0:
                for link in links:
                    if not existe_aviso(link.get_attribute("href"), id):
                        crear_aviso(link.get_attribute("href"), id)

        if milanuncios:
            links = buscar_milanuncios(articulo, max_price, driver, low_price)
            if links != 0:
                for link in links:
                    if not existe_aviso(link.get_attribute("href"), id):
                        crear_aviso(link.get_attribute("href"), id)

        if cash:
            links = buscar_cashconverters(articulo, max_price, driver, low_price)
            if links != 0:
                for link in links:
                    if not existe_aviso(link.get_attribute("href"), id):
                        crear_aviso(link.get_attribute("href"), id)

    for seg in seguimientos.find():
        link = seg["URL"]
        precio = seg["price"]
        id = seg["_id"]
        print("seg: ",link)
        res = check_precio(link, driver)
        
        print "res: ",res
        if res != 0:
            crear_valor_seg(id, res)
            if res <= precio and not existe_aviso(link, id):
                crear_aviso(link, id)
                
    driver.close()


print "Inicio" 

while true:
    try:
        realizar_busqueda()
    except Exception as e:
        print e
        pass


#realizar_busqueda()

#options = webdriver.ChromeOptions()
#options.add_argument("headless")
#driver = webdriver.Chrome(chrome_options=options)


# print check_precio("https://www.cashconverters.es/es/es/segunda-mano/sony-ps3-super-slim-500-gb/CC082_E290046_0.html",driver)
