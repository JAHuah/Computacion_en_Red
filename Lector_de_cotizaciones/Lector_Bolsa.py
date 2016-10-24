#!/usr/bin/python
# -*- coding: utf-8 -*-~
#importamos libreria de busqueda
import re
#importo libreria para acceso a URL
import urllib2, urllib
#importo librerbia de tiempo
import time
import datetime
#importamos libreria de hilos
import threading
#importamos libreria de mongo
from pymongo import MongoClient
#importo mi libreria de parseo
from Cotizacion import Cotizacion

######
def buscardor_de_datos(pagina, tipo_busca, Empresa):
	try:
		#definimos buscador pre
		buscador_pre = ""
		if (tipo_busca == 1):  #buscamos el precio
			if (Empresa == 'BANKIA' or Empresa =='SANTANDER' or Empresa =='ATRESMEDIA'):
					buscador_pre = '<div class="price top center">'; #es diferente al resto
				else:
					buscador_pre = '<div class="price flop center">'; 
		elif (tipo_busca == 2): #buscamos la fecha
			buscador_pre = '<div class="time left">';
		else: #buscamos el porcentaje
			if ( Empresa == 'BANKIA' or Empresa =='SANTANDER' or Empresa =='ATRESMEDIA'):
					buscador_pre = '<div class="difP top center">'; #es diferente al resto
				else:	
					buscador_pre = '<div class="difP flop center">';
		###pasamos de buscador post
		buscador_post = '</div>';
		if (tipo_busca == 3): 
			buscador_post = '%</div>';
		#realizamos la busqueda por parametros de busqueda
		buscador = buscador_pre+'(.*)'+buscador_post
		return re.search(buscador,pagina);
	except:
			print "Error: En la lectura del dato"

###########FUNCION INSERCCION y BUSQUEDA de CADA EMPRESA ################
def buscar_e_insertar(empresa, db):
	while True:
		try:
			print "%s - %s " % (empresa['Nombre'], empresa['Codigo'])
			#abrimos pagina web
			url = 'http://www.infobolsa.es/cotizacion/'+str(empresa['Nombre'])
			print "pagina a leer: "+str(url)
			response = urllib2.urlopen(url)
			#leemos el contenido descargado
			pagina = response.read()
			#cerramos el contendio descargado para la proxima vez
			response.close()
			#buscamos ahora el dato de valor
			Valor = buscardor_de_datos(pagina, 1, empresa['Nombre']);
			#buscamos ahora el dato de valor
			Hora = buscardor_de_datos(pagina, 2, empresa['Nombre']);
			#buscamos ahora el porcentaje
			Por_subida = buscardor_de_datos(pagina, 3, empresa['Nombre']);
			#Parseamos el Resultado
			insertar = Cotizacion(float(str(Valor.group(1)).replace(',', '.')), str(empresa['Codigo']),datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S '),float(Por_subida.group(1).replace(',', '.')), str(Hora.group(1)));
			print str(insertar)
			#insertamos el valor en MongoDD
			print str(insertar.toDBCollection())
			db.Cotizaciones.insert_one(insertar.toDBCollection())
			#insertamos en thing
			params = urllib.urlencode(
				{'key': empresa['Write'], 
				'field1': float(str(Valor.group(1)).replace(',', '.')), 
				'field2':float(Por_subida.group(1).replace(',', '.'))});
			#usamos la api de thingspeak para usar su servicio post
			f = urllib2.urlopen("https://api.thingspeak.com/update", data=params)
			time.sleep(120);
		except AttributeError:
			print "Error: No se ha recibido correctamente el dato"

##################################################################
# PASO 1: Conexión al Server de MongoDB Pasandole el host y el puerto
mongoClient = MongoClient('127.0.0.1',27017);
# PASO 2: Conexión a la base de datos
db = mongoClient.Bolsa
# Obtenemos las empresas que vamos a leer y su respectivos codigo
empresas = db.Empresas.find()
#empezamos a leer datos e introducirlo
#para ellos vamos a hilar cada proceso para asi hacer insercciones en paralelo
#generamos lista de hilos
threads = list()
for empresa in empresas:
	#buscar_e_insertar(empresa, db)
	#hilamos para que cada seccion haga su busqueda e inserte
	t = threading.Thread(target=buscar_e_insertar, args=(empresa,db,))
	threads.append(t)
	t.start()
	