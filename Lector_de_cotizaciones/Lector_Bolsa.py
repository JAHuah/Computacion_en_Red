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

######Funcion para detectar patrones################################
def buscardor_de_datos(pagina, tipo_busca, Empresa):
	try:
		#print str(pagina);
		#definimos buscador pre
		posibles_elementos = ['top','flop','equal']
		
		for elemento in posibles_elementos:
			buscador_pre = ""
			if (tipo_busca == 1):  #buscamos el precio
				buscador_pre = '<div class="price '+str(elemento)+' center">'; #es diferente al resto
			elif (tipo_busca == 2): #buscamos la fecha
				buscador_pre = '<div class="time left">';
			else: #buscamos el porcentaje
				buscador_pre = '<div class="difP '+str(elemento)+' center">'; #es diferente al resto
			###pasamos de buscador post
			buscador_post = '</div>';
			if (tipo_busca == 3): 
				buscador_post = '%</div>';
			#realizamos la busqueda por parametros de busqueda
			buscador = buscador_pre+'(.*)'+buscador_post
			valor = re.search(buscador,pagina);
			if valor is not None:
				return valor.group(1);
			
	except:
		print "Error: En la lectura del dato"
			
###########Funcion comparadora de horas##################################
def guardar_datos():
	d = datetime.datetime.utcnow()
	t = d.time()
	print t.hour,t.minute,t.second
	if ((t.hour+2) >= 9 and (t.hour+2) <=18):
		return 1;
	else:
		return 0;
				
###########FUNCION INSERCCION y BUSQUEDA de CADA EMPRESA ################
def buscar_e_insertar(empresa, db):
	while True:
		try:
			if (guardar_datos() == 1):
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
				insertar = Cotizacion(float(str(Valor).replace(',', '.')), str(empresa['Codigo']),datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S '),float(Por_subida.replace(',', '.')), str(Hora));
				print str(insertar)
				#insertamos el valor en MongoDD
				print str(insertar.toDBCollection())
				db.Cotizaciones.insert_one(insertar.toDBCollection())
				#insertamos en thing
				params = urllib.urlencode(
					{'key': empresa['Write'], 
					'field1': float(str(Valor).replace(',', '.')), 
					'field2':float(Por_subida.replace(',', '.'))});
				#usamos la api de thingspeak para usar su servicio post
				f = urllib2.urlopen("https://api.thingspeak.com/update", data=params)
			time.sleep(120);
		except AttributeError:
			print "Error: No se ha recibido correctamente el dato"

##################################################################
#esperamos a que arranque mongo
time.sleep(60);
# PASO 1: Conexión al Server de MongoDB Pasandole el host y el puerto
#mongoClient = MongoClient('127.0.0.1',27017);
mongoClient = MongoClient('mongodb://jahuah:arppath@ds145868.mlab.com:45868/bolsa')
# PASO 2: Conexión a la base de datos
db = mongoClient.bolsa
db.test_database
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
	
