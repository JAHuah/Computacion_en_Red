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
def seleccion_de_datos(pagina):
	#try:
		print "########### PAGINA ############"
		print "longitud de la pagina" + str(len(str(pagina)))
		web = pagina.replace('^M','').replace('^m','').replace('\n','').replace('\r','').replace('  ','')
		#print "pagina : "+ str(len(str(web)))
		#print str(web)
		while True:
			buscador_pre = '<tbody>'
			buscador_post = '</tbody>'
			buscador = str(buscador_pre)+'(.*)'+str(buscador_post)
			seleccion = re.findall(buscador,str(web));
			if len(seleccion) != 0:
				#print "seleccion: "+str(seleccion)
				return str(seleccion)
	#except:
	#	print "Error: En la lectura de la pagina"
		
##### buscador dentro de la seleccion
def buscardor_de_datos(pagina, buscador_pre, buscador_post):
#	try:
		#print str(pagina);
		#realizamos la busqueda por parametros de busqueda
		while True:
			buscador = str(buscador_pre)+'(.*)'+str(buscador_post)
			valor = re.match(buscador,pagina);
			if valor is not None:
				print "buscado: "+str(valor.group(1))
				return str(valor)
			else:
				print "volvemos a intentar en buscador de datos"
#	except:
#		print "Error: En la lectura del dato"
			
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
		#try:
			if (guardar_datos() == 1):
				print "%s - %s " % (empresa['Nombre'], empresa['Codigo'])
				#abrimos pagina web
				url = 'http://www.infobolsa.es/acciones/ibex35'
				print "pagina a leer: "+str(url)
				response = urllib2.urlopen(url)
				#leemos el contenido descargado
				pagina = response.read()
				#cerramos el contendio descargado para la proxima vez
				response.close()
				#seleecionamos el framento que queremos
				fragmento = seleccion_de_datos(pagina)
				precio = buscardor_de_datos(fragmento, '<td class="price flop">','</td><td class=')
				porcentaje = buscardor_de_datos(fragmento,'<td class="changeP flop">','</td><td class="max">')
				hora = buscador_de_datos(fragmento,'<td class="hour"><div class="">','</div></td><td class="social">')
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
				# print str(insertar.toDBCollection())
				# db.Cotizaciones.insert_one(insertar.toDBCollection())
				# #insertamos en thing
				# params = urllib.urlencode(
					# {'key': empresa['Write'], 
					# 'field1': float(str(Valor).replace(',', '.')), 
					# 'field2':float(Por_subida.replace(',', '.'))});
				# #usamos la api de thingspeak para usar su servicio post
				# f = urllib2.urlopen("https://api.thingspeak.com/update", data=params)
			time.sleep(120);
		#except AttributeError:
		#	print "Error: No se ha recibido correctamente el dato"

##################################################################
#esperamos a que arranque mongo
#time.sleep(60);
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
	buscar_e_insertar(empresa, db)
	#hilamos para que cada seccion haga su busqueda e inserte
	# t = threading.Thread(target=buscar_e_insertar, args=(empresa,db,))
	# threads.append(t)
	# t.start()
	