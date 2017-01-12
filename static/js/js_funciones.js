function Sacamos_Grafica(url)
{
	//1º Activamos el aviso para que sea visible
	$( "#dialog-message" ).dialog( "open" );
	grafica = '<iframe width="450" height="250" style="border: 1px solid #cccccc;" src="'+url+'"></iframe>'
	$("#dialog-message").html(grafica)
}

function solicitud(web)
{	
	//volvemos a poner todo en su sitio para hacer el loading
	volver_inicio_emergente()
	//poner visible el loading
	$( "#dialog-message" ).dialog( "open" );
	//podimos lo que necesitamos
	$.ajax({
		url: web,
		type: 'POST',
		success: function(response) {
			$("#intercambio").html(response)
			$( "#dialog-message" ).dialog( "close" );
			setInterval(function(){$('#intercambio').load(web)}, 120000) /* time in milliseconds (ie 2 seconds)*/
		}, 
		error: function(req, status, err) {
			$( "#mensaje" ).dialog( req+"->"+status+"->"+err );
		}
	});
}

function registro()
{
	var caracteres = new Array(" ","%","'");
	var usuario = $("#txt_user").val();
	var pass = $("#txt_pass").val();
	var correcto = 1;
	//1º Activamos el aviso para que sea visible
	$( "#dialog-message" ).dialog( "open" );

	//para eviatar lios quitamos los espacios
	for (i=0; i<3;i++)
	{
		usuario = usuario.replace(/caracteres[i]/gi,"");
		pass = pass.replace(/caracteres[i]/gi,"");
	}

	//validaciones previas: comprobar que se ha introducido el usuario y la password
	if(pass.length == 0 || usuario.length == 0){
		$( "#dialog-message" ).dialog( "open" );
		$("#mensaje").html("Error: El usuario y/o clave no pueden estar vacios");
		correcto = 0;
	}
	if(correcto == 1)
	{
		//2º mandamos la información para validar el user/pass
		parametros= {"usuario" : usuario, "pass" : pass}
		$.ajax({
	        url:"/Validar",
	        dataType : "json",//el tipo de datos
	        data : parametros,
	        type: "POST",
	        success: function(opciones){
	        	if(opciones == 1){ //todo correcto
	        		$( "#dialog-message" ).dialog( "close" );
	        		document.location.href="/Principal";
	        	}
	        	else
	        	{
	        		$("#mensaje").html("Error: El usuario y/o clave no son correcto");
	        	}
	        }
	    })
	}
}

function onSignIn(googleUser) {
	var profile = googleUser.getBasicProfile();
	console.log('ID: ' + profile.getId()); // Do not send to your backend! Use an ID token instead.
	console.log('Name: ' + profile.getName());
	console.log('Image URL: ' + profile.getImageUrl());
	console.log('Email: ' + profile.getEmail());
	//2º mandamos la información para validar el user/pass
	parametros= {"Name" : profile.getName(), "Email" : profile.getEmail()}
	$.ajax({
		url:"/autentificar_con_google",
		dataType : "json",//el tipo de datos
		data : parametros,
		type: "POST",
		success: function(opciones){
			if(opciones == 1){ //todo correcto
				$( "#dialog-message" ).dialog( "close" );
				document.location.href="/Principal";
			}
			else
			{
				$("#mensaje").html("Error: El usuario y/o clave no son correcto");
			}
		}
	})
}

function Seguir_quitar_valor(accion, elemento)
{	
	//volvemos a poner todo en su sitio para hacer el loading
	volver_inicio_emergente()
	//poner visible el loading
	$( "#dialog-message" ).dialog( "open" );
	//podimos lo que necesitamos
	if (accion == 1)
	{
		parametros = {"Id_empresa" : $('#select_cod_empresa').val() }
		web = "/poner";
	}
	else
	{
		parametros = {"Id_empresa" : elemento}
		web = "/quitar";
	}
	$.ajax({
		url: web,
		data: parametros,
		type: 'POST',
		success: function(response) {
			$( "#dialog-message" ).dialog( "close" );
			$("#empresas_seguidas").html(response)
		},
		error: function(req, status, err) {
			$( "#mensaje" ).dialog( req+"->"+status+"->"+err );
		}
	});
}

function Actualizar_user( User )
{
	var caracteres = new Array(" ","%","'");
	//volvemos a poner todo en su sitio para hacer el loading
	volver_inicio_emergente()
	var umbral = $("#txt_umbral").val();
	var pass = $("#txt_pass").val();
	//poner visible el loading
	$( "#dialog-message" ).dialog( "open" );
	//podimos lo que necesitamos
	//para eviatar lios quitamos los espacios
	for (i=0; i<3;i++)
		pass = pass.replace(/caracteres[i]/gi,"");

	//validaciones previas: comprobar que se ha introducido el usuario y la password
	if(pass.length == 0 || umbral <= 0){
		$( "#dialog-message" ).dialog( "open" );
		$("#mensaje").html("Error: la pass no pueden estar vacios ni el umbral ser menor o igual que 0");
		return
	}
	
	parametros = {"User" : User, "Pass":pass, "Umbral":umbral}
	web = "/Actualizar_user";
	$.ajax({
		url: web,
		data: parametros,
		type: 'POST',
		success: function(response) {
			$("#mensaje").html(response)
		},
		error: function(req, status, err) {
			$( "#mensaje" ).dialog( req+"->"+status+"->"+err );
		}
	});
}
function nueva_compra()
{
	//volvemos a poner todo en su sitio para hacer el loading
	volver_inicio_emergente()
	var suelo = parseFloat($("#txt_suelo").val());
	var techo = parseFloat($("#txt_techo").val());
	var valor = parseFloat($("#txt_valor").val());
	var codigo = $("#select_empresa").val();
	//poner visible el loading
	$( "#dialog-message" ).dialog( "open" );
	//validaciones previas: comprobar que se ha introducido el usuario y la password
	if(codigo == 0 ||(suelo.length == 0 || suelo <= 0) || (valor.length == 0 || valor <= 0) || (techo.length == 0 || techo <= 0)){
		$( "#dialog-message" ).dialog( "open" );
		$("#mensaje").html("Error: Los valores introducidos son incorrectos");
		return
	}
	
	parametros = {"Empresa" : codigo, "Valor":valor, "Techo":techo, "Suelo":suelo}
	web = "/insertar_compra";
	$.ajax({
		url: web,
		data: parametros,
		type: 'POST',
		success: function(response) {
			$( "#dialog-message" ).dialog( "close" );
			$("#elementos_comprados_art").html(response)
		},
		error: function(req, status, err) {
			$( "#mensaje" ).dialog( req+"->"+status+"->"+err );
		}
	});
}

function eliminar_compra(Fecha){
	volver_inicio_emergente()
	//poner visible el loading
	$( "#dialog-message" ).dialog( "open" );
	parametros = {"Fecha" : Fecha}
	web = "/eliminar_compra";
	$.ajax({
		url: web,
		data: parametros,
		type: 'POST',
		success: function(response) {
			$( "#dialog-message" ).dialog( "close" );
			$("#elementos_comprados_art").html(response)
		},
		error: function(req, status, err) {
			$( "#mensaje" ).dialog( req+"->"+status+"->"+err );
		}
	});
}

function seleccion_grafica_compra()
{
	volver_inicio_emergente()
	//poner visible el loading
	$( "#dialog-message" ).dialog( "open" );
	var Empresa = $("#select_empresa").val();
	
	if(Empresa == 0){
		$( "#dialog-message" ).dialog( "open" );
		$("#mensaje").html("Error: Los valores introducidos son incorrectos");
		return
	}

	parametros = {"Fecha" : Empresa}
	web = "/selecciongraficacompra";
	$.ajax({
		url: web,
		data: parametros,
		type: 'POST',
		success: function(response) {
			$("#pos_grafica").html(response)
			$( "#dialog-message" ).dialog( "close" );
		},
		error: function(req, status, err) {
			$( "#mensaje" ).dialog( req+"->"+status+"->"+err );
		}
	});
}