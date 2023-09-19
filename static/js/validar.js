var correo=document.getElementById('email');
var password=document.getElementById('password');
var error=document.getElementById('error');
error.style.color='red';
/*se declaran las variables*/
function validar(){
    console.log("Enviando formulario");
    var mensajesError=[];
    if(correo.value==null || correo.value==''){
        mensajesError.push('Ingresa tu nombre');
    }
    
    if(password.value==null || password.value==''){
        mensajesError.push('Ingresa tu password');
    }

    error.innerHTML=mensajesError.join(', ');
    
    return false;
}