$(function() {
    $("#dialog-message").dialog({
		autoOpen: false,
		model: true,
		width: "auto",
		height: "auto",
		show: {
			effect: "blind",
			duration: 100
		}
    });
});

function volver_inicio_emergente()
{
	$("#dialog-message").html('<div id="dialog-message" title="Solicitud" > <img src="../static/images/loading.gif" alt="" name="logo" /><p id="mensaje"> Procensando su petición </p></div>')
}


function validateEmail($email) {
	var emailReg = /^([\da-z_\.-]+)@([\da-z\.-]+)\.([a-z\.]{2,6})$/;
	if( !emailReg.test( $email ) ) {
		return false;
	} else {
		return true;
	}
}

function justNumbers(e)
{
	var keynum = window.event ? window.event.keyCode : e.which;
	if ((keynum == 8) || (keynum == 46))
	return true;
	 
	return /\d/.test(String.fromCharCode(keynum));
}

function eliminar_caracteres_no_validos(texto){
	var caracteres = new Array("%","'");
	var quitar = "";

	var coincidencias = ""; 
	var numcars = 0; 

	for(i=0; i<2; i++){
		coincidencias = texto.match(caracteres[i]); //Busca todas las 'e'
		numcars = coincidencias ? coincidencias.length : 0;
		for(j=0; j<numcars; j++)
			texto = texto.replace(caracteres[i]," ");
	}
	return texto;
}

function abrir_enlace_user(enlace, accion_realizar)
{
	var parametros = {
	        "accion" : accion_realizar
	    }
	$.ajax({
        url:enlace,
        type: "POST",
        data: parametros,
        success: function(opciones){
    		$( "#formulario" ).html(opciones);
        }
    })
}