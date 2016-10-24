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