#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
#para operar de forma rapida
import numpy as np
#importo libreria para acceso a URL
import urllib2, urllib
#libreria para flask
from flask import Flask, session, render_template, url_for, request, redirect
#importamos libreria de mongo
from pymongo import MongoClient
#para convertir str a diccionario
import ast
#para el tema de autorizaciones
from oauth2client.client import flow_from_clientsecrets
from pydrive.auth import GoogleAuth


#VARIABLES DE USO GENERAL
app = Flask(__name__, template_folder='Template')
#variables para base de datos
mongoClient = MongoClient('127.0.0.1',27017);
db = mongoClient.Bolsa

@app.route('/')
def index():
	#devolvemos el main
	return render_template('index.html')

@app.route('/Validar', methods=['POST','GET'])
def Validar():
	print "session.has_key('id') = "+ str(session.has_key('id'))
	if session.has_key('id') == False:
		parametros = request.form
		respuestas = db.Usuarios.find({"User":parametros['usuario'],"Pass":parametros['pass']});
		if (respuestas.count() == 1):
			for respuesta in respuestas:
				#una vez comprobada que la sesion la tengo yo creada
				session['id'] = str(respuesta['_id'])
				session['Porcentaje'] = respuesta['Porcentaje']
				session['nombre'] = respuesta['User']
				print "Sesion: "+str(session)
				return '1'
				# dir_json = 'json/'+str(respuesta['json'])
				# if (autentificar_con_google(dir_json) == 1):
					# session['id'] = str(respuesta['_id'])
					# session['Porcentaje'] = respuesta['Porcentaje']
					# session['nombre'] = respuesta['User']
					# print "Sesion: "+str(session)
					# return '1'
				# else:
					# return '0'
		else:
			return "Error al Validad los datos" ;
	else:
		return '1';
		
def autentificar_con_google(credenciales):
	try:
		gauth = GoogleAuth()
		# Try to load saved client credentials
		print str(gauth)
		gauth.LoadCredentialsFile(credenciales)
		if gauth.credentials is None:
			# Authenticate if they're not there
			gauth.LocalWebserverAuth()
		elif gauth.access_token_expired:
			# Refresh them if expired
			gauth.Refresh()
		else:
			# Initialize the saved creds
			gauth.Authorize()
		# Save the current credentials to a file
		gauth.SaveCredentialsFile(credenciales)
		return 1
	except (RuntimeError, TypeError, NameError):
		print("Unexpected error:", sys.exc_info()[0])
		print "la autentificacion con google no fue correcta"
		return 0
	
	
	
#comenzamos con la aplicacion web!!!!
		
@app.route('/Principal')
def Principal():
	#devolvemos el main
	if session.has_key('id') == False:
		return redirect(url_for('index'));
	else:
		return render_template('Principal.html')
	
@app.route('/Cotizacion', methods=['POST'])
def cotizacion():
	if session.has_key('id') == False:
		return redirect(url_for('index'));
	else:
		dict = []
		coti = {}
		nombres = []
		cotizacion = {}
		valor = []
		#Primero debemos encontrar las empresas que el usuario quiere ver
		Empresas = db.RelacionUserEmpresa.find({"Id_user": session['nombre']});
		for Empresa in Empresas:
			cotizacion[Empresa["Id_empresa"]] = []
			nombres.append(Empresa["Id_empresa"])
			#segundo buscamos la informacion de la empresa
			Datos_empresa = db.Empresas.find({"Codigo": Empresa["Id_empresa"]});
			for Datos in Datos_empresa:
				dict.append(Datos)
				cotizacion[Empresa["Id_empresa"]].append(Datos['Nombre'])
			#obtenemos datos para la grafica de google
			Cotizaciones = db.Cotizaciones.find({"Id_Empresa": Empresa["Id_empresa"]}).sort("Hora",-1).limit(70);
			coti[Empresa["Id_empresa"]] = []
			for Datos in Cotizaciones:
				coti[Empresa["Id_empresa"]].insert(0, Datos)
			#calculamos ahora los valroes maximo minimo y actual de las empresas que seguimso
			#valor ultimo
			cotizacion[Empresa["Id_empresa"]].append(Empresa["Id_empresa"])
			dato = db.Cotizaciones.find({"Id_Empresa": Empresa["Id_empresa"]}).sort("Hora",-1).limit(1);
			for dat in dato:
				cotizacion[Empresa["Id_empresa"]].append(dat['Valor'])
			#valor maximo
			dato = db.Cotizaciones.find({"Id_Empresa": Empresa["Id_empresa"]}).sort("Valor",-1).limit(1);
			for dat in dato:
				cotizacion[Empresa["Id_empresa"]].append(dat['Valor'])
			#valor minimo
			dato = db.Cotizaciones.find({"Id_Empresa": Empresa["Id_empresa"]}).sort("Valor",1).limit(1);
			for dat in dato:
				cotizacion[Empresa["Id_empresa"]].append(dat['Valor'])
		print "Cotizacion = "+str(cotizacion)
		#devolvemos el main
		return render_template('Cotizacion.html', result = dict, coti = coti, nombres = nombres, cotizaciones = cotizacion)	

@app.route('/Config', methods=['POST'])
def Config():
	if session.has_key('id') == False:
		return redirect(url_for('index'));
	else:
		dict ={}
		#Primero debemos encontrar las empresas que el usuario quiere ver
		Empresas_cliente = db.RelacionUserEmpresa.find({"Id_user": session['nombre']});
		#Todas las empresas
		Empresas = db.Empresas.find();
		dict['Empresas_cliente']=[]
		for Datos in Empresas_cliente:
			datos_empresas = db.Empresas.find({"Codigo": Datos["Id_empresa"]}).limit(1);
			for datos_unicos in datos_empresas:
				#print str(datos_unicos)
				Datos['Nombre'] = datos_unicos['Nombre']
			dict['Empresas_cliente'].append(Datos)
		dict['Empresas'] = []
		for Datos in Empresas:
			dict['Empresas'].append(Datos)
		#devolvemos el main
		return render_template('Config.html', result = dict)

@app.route('/Estadisticas', methods=['POST'])
def Estadisticas():
	print str(session)
	if session.has_key('id') == False:
		return redirect(url_for('index'));
	else:
		coti = {}
		coti_ext = {}
		result = []
		Externa = []
		#primero debemos buscar los datos que queremos
		Empresas = db.RelacionUserEmpresa.find({"Id_user": session['nombre']});
		for Empresa in Empresas:
			#segundo buscamos las cotizaciones de la empresa
			Datos_empresa = db.Empresas.find({"Codigo": Empresa["Id_empresa"]});
			for dato in Datos_empresa:
				#vamos con los valores internos
				Cotizaciones = db.Cotizaciones.find({"Id_Empresa": Empresa["Id_empresa"]}).limit(70);
				coti[Empresa["Id_empresa"]] = []
				for Cotizacion in Cotizaciones:
					coti[Empresa["Id_empresa"]].append(Cotizacion['Valor'])
				#calculamos los estadisticos
				a = np.array(coti[Empresa["Id_empresa"]]);
				result.append([dato['Nombre'],Empresa['Id_empresa'], np.mean(a), np.median(a) ,np.std(a)])
				#una vez tengo lo propio vamos con los externos
				url = "https://api.thingspeak.com/channels/"+str(dato['Graficas'])+"/fields/1.json"
				#leemos los datos
				datos_externos = ast.literal_eval(urllib2.urlopen(url=url).read())
				#ahora lo colocamos para facilitar los datos
				coti_ext[Empresa["Id_empresa"]] = []
				for diccionario in datos_externos["feeds"]:
					coti_ext[Empresa["Id_empresa"]].append(diccionario["field1"])
				a = np.array(coti_ext[Empresa["Id_empresa"]]).astype(np.float);
				Externa.append([dato['Nombre'],Empresa['Id_empresa'], np.mean(a), np.median(a) ,np.std(a)])
		return render_template('Estadisticas.html', result = result, Externa = Externa)
	
@app.route('/poner', methods=['POST'])
def poner():
	parametros = request.form
	respuestas = db.RelacionUserEmpresa.find({"Id_empresa": parametros["Id_empresa"]}).limit(1);
	#si encontramos 1 elemento quiere decir que ya esta asignado por lo tanto no debemos asignarlo
	if (respuestas.count() == 0):
		insertar = {"Id_user":session['nombre'],"Id_empresa": parametros["Id_empresa"]}
		print str(insertar)
		db.RelacionUserEmpresa.insert_one(insertar)
		return 'La operación se ha realizado correctamente'
	else:
		return "No se ha podido realizar la operación, el dato o no es valido o se encuentra ya insertado";

@app.route('/quitar', methods=['POST'])
def quitar():
	parametros = request.form
	respuestas = db.RelacionUserEmpresa.find({"Id_empresa": parametros["Id_empresa"]}).limit(1);
	#si encontramos 1 elemento quiere decir que ya esta asignado por lo tanto no debemos asignarlo
	if (respuestas.count() > 0):
		eliminar = {"Id_user":session['nombre'],"Id_empresa": parametros["Id_empresa"]}
		db.RelacionUserEmpresa.remove(eliminar)
		return 'La operación se ha realizado correctamente'
	else:
		return "No se ha podido realizar la operación, el dato o no es valido o se encuentra ya insertado";

@app.route('/Usuario', methods=['POST'])
def Usuario():
	#obtenemos todos los datos del usuario
	if session.has_key('id') == False:
		return redirect(url_for('index'));
	else:
		respuestas = db.Usuarios.find({"User":session['nombre']});
		for aux in respuestas:
			result = aux
		print str(result)
		return render_template('Usuario.html',result = result)

@app.route('/Actualizar_user', methods=['POST'])
def Actualizar_user():
	#obtenemos los datos
	parametros = request.form
	#obtenemos todos los datos del usuario
	respuestas = db.Usuarios.update({"User":session['nombre']},{"User":session['nombre'], "Pass":parametros['Pass'],"Porcentaje":parametros['Umbral']});
	return "La operación se ha realizado correctamente"

@app.route('/Mensajes', methods=['POST'])
def Mensajes():
	if session.has_key('id') == False:
		return redirect(url_for('index'));
	else:
		maximo = []
		minimo = []
		#primero debemos buscar los datos que queremos
		Datos_User = db.Usuarios.find({"User": session['nombre']}); #con esto sacamos el umbral
		Datos_empresa = db.RelacionUserEmpresa.find({"Id_user": session['nombre']}); #con esto sacamos las empresas
		for Datos in Datos_User:
			#segundo buscamos las cotizaciones de la empresa
			for dato_empresa in Datos_empresa:
				#vamos con los valores internos
				Cotizaciones = db.Cotizaciones.find({"Id_Empresa": dato_empresa["Id_empresa"]}); #.sort({"Porcentaje":-1});
				valor_pos = float(Datos['Porcentaje'])
				valor_negativo = float((-1)*float(Datos['Porcentaje']));
				for Cotizacion in Cotizaciones:
					if (float(Cotizacion["Porcentaje"]) >= float(valor_pos)):
						#print "Porcentaje: "+str(Cotizacion["Porcentaje"])+" Porcentaje: "+str(valor_pos)
						maximo.append(Cotizacion)
					elif float(Cotizacion["Porcentaje"]) <= float(valor_negativo):
						#print "Porcentaje: "+str(Cotizacion["Porcentaje"])+" Porcentaje: "+str(valor_negativo)
						minimo.append(Cotizacion)
		return render_template('Mensajes.html', maximo = maximo, minimo = minimo)

@app.route('/Salir')
def Salir():
	session.pop('id', None);
	print "Session = "+str(session)
	return redirect(url_for('index'));
	
if __name__ == '__main__':
	import uuid
	app.secret_key = str(uuid.uuid4())
	app.debug = True
	app.run(debug=True,host='0.0.0.0',port=80)