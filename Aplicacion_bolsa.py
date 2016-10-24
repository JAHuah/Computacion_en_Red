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


#import httplib2
# from apiclient import discovery
# from oauth2client import client

#VARIABLES DE USO GENERAL
app = Flask(__name__, template_folder='Template')
mongoClient = MongoClient('127.0.0.1',27017);
db = mongoClient.Bolsa


@app.route('/')
def index():
	#devolvemos el main
	return render_template('index.html', result = dict)
	
@app.route('/Config', methods=['POST'])
def Config():
	dict ={}
	#Primero debemos encontrar las empresas que el usuario quiere ver
	Empresas_cliente = db.RelacionUserEmpresa.find({"Id_user": session['nombre']});
	#Todas las empresas
	Empresas = db.Empresas.find();
	dict['Empresas'] = Empresas
	dict['Empresas_cliente'] = Empresas_cliente
	print str(dict['Empresas'])
	#devolvemos el main
	return render_template('Config.html', result = dict, pos = 0)

@app.route('/Cotizacion', methods=['POST'])
def cotizacion():
	dict = []
	coti = {}
	nombres = []
	#Primero debemos encontrar las empresas que el usuario quiere ver
	Empresas = db.RelacionUserEmpresa.find({"Id_user": session['nombre']});
	for Empresa in Empresas:
		nombres.append(Empresa["Id_empresa"])
		#segundo buscamos la informacion de la empresa
		Datos_empresa = db.Empresas.find({"Codigo": Empresa["Id_empresa"]});
		for Datos in Datos_empresa:
			dict.append(Datos)
		Cotizaciones = db.Cotizaciones.find({"Id_Empresa": Empresa["Id_empresa"]}).limit(70);
		coti[Empresa["Id_empresa"]] = []
		for Cotizacion in Cotizaciones:
			coti[Empresa["Id_empresa"]].append(Cotizacion)
	#devolvemos el main
	return render_template('Cotizacion.html', result = dict, coti = coti, nombres = nombres)
	
@app.route('/Principal')
def Principal():
	#devolvemos el main
	return render_template('Principal.html')
	
@app.route('/Estadisticas', methods=['POST'])
def Estadisticas():
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

@app.route('/Validar', methods=['POST'])
def Validar():
	parametros = request.form
	respuestas = db.Usuarios.find({"User":parametros['usuario'],"Pass":parametros['pass']});
	if (respuestas.count() == 1):
		for respuesta in respuestas:
			session['id'] = str(respuesta['_id'])
			session['Porcentaje'] = respuesta['Porcentaje']
			session['nombre'] = respuesta['User']
			print "Sesion: "+str(session)
			return '1'
	else:
		return '0';
	
	
# @app.route('/oauth2callback')
# def oauth2callback():
	# flow = client.flow_from_clientsecrets(
	# 'client_secrets.json',
	# scope='https://www.googleapis.com/auth/drive.metadata.readonly',
	# redirect_uri=flask.url_for('oauth2callback', _external=True),
	# include_granted_scopes=True)
	# if 'code' not in flask.request.args:
		# auth_uri = flow.step1_get_authorize_url()
		# return flask.redirect(auth_uri)
	# else:
		# auth_code = flask.request.args.get('code')
		# credentials = flow.step2_exchange(auth_code)
		# flask.session['credentials'] = credentials.to_json()
		# print str(flask.session)
		# return flask.redirect(flask.url_for('index'))

if __name__ == '__main__':
	import uuid
	app.secret_key = str(uuid.uuid4())
	app.debug = True
	app.run(debug=True,host='0.0.0.0',port=80)