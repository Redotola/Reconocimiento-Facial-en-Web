'''
Autores: Axl Armando Castrejon Ocampo && Eduardo David Salgado Luna
Grupo: C Grado: 7 Cuatrimestre
Materia: Estancia 2
Profesora: Dra. Deny Lizbeth Hernández Rabadán
'''

from flask import Flask,  render_template, request, redirect, url_for, session,flash, Response # pip install Flask
from flask_mysqldb import MySQL # pip install Flask-MySQLdb
from notifypy import Notify # pip install notifypy y pip install notify-py
from reconocimiento import capturarostros, entrenandoRF, reconocimientofacial # importamos funciones de codigo
from os import remove # pip install os
from shutil import rmtree #pip install shutil
from fpdf import FPDF #pip install fpdf
#funciones de reconocimiento facial
'''
En el apartado de reconocimiento necesitaremos de las siguientes librerias
pip install imutils
pip install contrib-opencv-python
pip install numpy
'''

app = Flask(__name__) #nombramos nuestro aplicativo como "app"
app.config['MYSQL_HOST'] = 'localhost' #puerto o direccion en donde se conecta la base de datos
app.config['MYSQL_USER'] = 'root' #usuario con el que conectamos nuestra base de datos
app.config['MYSQL_PASSWORD'] = '' #contrasena de la base de datos
app.config['MYSQL_DB'] = 'test' #nombre de la base de datos
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' #nombre del cursor que se usara dentro de la base para realizar las operaciones
mysql = MySQL(app) #mandamos nuestros datos de aplicacion a la funcion MySQL para la conexion y manejo de base de datos


#SESION#
app.secret_key = "mysecretkey" #contrasena de la aplicacion para acceder al manejo de la base

# Funcion que obtiene los datos del formulario en login y valida usuarios y acceso a plataforma
@app.route('/login', methods= ["GET", "POST"]) #usamos el metodo POST y GET para 
def login():
    try:
        notificacion = Notify()# crear objeto Notify que emitira mensajes durante la ejecucion del codigo
        if request.method == 'POST':# Si el metodo es POST realiza la obtencion del formulario los datos del usuario
            email = request.form['email']
            password = request.form['password']

            cur = mysql.connection.cursor()#abre un nuevo cursor para realizar operaciones en sql
            cur.execute("SELECT * FROM users WHERE email=%s",(email,)) # Consulta todos los usuarios en la base con correo
            user = cur.fetchone() #obtener el resultado de la consulta dentro de la variable
            cur.close() #cierra el cursor

            if len(user)>0: #evalua si la consulta tiene mayor longitud a 0 quiere decir que contiene datos
                if password == user["password"] and email==user['email']: #Evalua si concuerda el usuario y contrasenia
                    session['name'] = user['name'] #obtiene todos los datos del usuario
                    session['email'] = user['email']
                    session['password'] = user['password']
                    session['tipo'] = user['id_tip_usu']
                    if session['tipo'] == 1: #evalua el tipo de sesion para redireccionar al menu de cada tipo de usuario
                        flash("Acceso al sistema correctamente")
                        return render_template("homeAdministrador.html")
                    elif session['tipo'] == 2:
                        flash("Acceso al sistema correctamente")
                        return render_template("homeEmpleado.html")
                    elif session['tipo'] == 3:
                        flash("Acceso al sistema correctamente")
                        return render_template("homeRecursosHumanos.html")
                else:# De lo contrario emite un mensaje de error para el usuario retornando a la pagina de login 
                    flash("Error de acceso")
                    notificacion.title = "Error de Acceso"
                    notificacion.message="Correo o contraseña no valida"
                    notificacion.send()
                    return render_template("login.html")
            else:
                notificacion.title = "Error de Acceso"
                notificacion.message="No existe el usuario"
                notificacion.send()
                flash("Error de acceso no existe el usuario")
                return render_template("login.html")
        else:
            return render_template("login.html")
    except Exception as e: #en caso de algun error en el sistema regresa a la pagina de inicio emitiendo un mensaje de error
        notificacion.title="Error de sistema"
        notificacion.message=f"Error de tipo {e}"
        notificacion.send()
        flash(f"Error de acceso: {e}")
        return render_template("login.html")

#ruta de inicio cuando iniciamos el servidor
@app.route('/')
def home():#función para redireccionar al inicio de la pagina
    session.clear()# limpia la variable sesion
    return render_template("login.html")# Renderiza el html login
    
#funcion que redirecciona a menu del administrador
@app.route('/menu')
def menu():#definición de la función para el menu de Administrador
    try: #interceptamos errores en la seccion de codigo
        if session['tipo']==1:#Validación para el inicio de sesión de solo Administradores
            return render_template('homeAdministrador.html')
        else:#Si no se cumple se manda un mensaje
            flash("Error de inicio de sesion, no cuetas con las credenciales necesarias")
            return render_template('login.html')#Y hace la carga hacia el login
    except Exception as e:#Hacemos la excepción que se envia hacia tipo Exception hacia e
        flash(f"Error de tipo {e} consulte a su administrador")#Mandamos mensaje diciendo el tipo de error aguardado en e
        return render_template("login.html")#Y hacemos la carga hacia login
    
#funcion que redirecciona a menu del director de recursos humanos
@app.route('/menu_Recu')
def menu_Recu():#Definición de la función
    try:
        if session['tipo']==1 or session['tipo']==3:#Se compara los datos de las sesiones tipo admin y recursos
            return render_template('homeRecursosHumanos.html')
        else: 
            flash("Error de acceso, no tienes las credenciales para acceder") #Emite un error de acceso en caso contrario
            return render_template("login.html")
    except Exception as e: #Guarda errores en variable para su consulta con mensaje
        flash(f"Error de tipo {e}, consulte con su administrador")
        return render_template("login.html") #Redirecciona a login en caso de error
        
    
#Funcion que redirecciona a menu del empleado
@app.route('/menu_Empe') 
def menu_Empe():
    try:
        if session['tipo']==2:# Realiza una comparación de tipo de usuario empleado
            return render_template('homeEmpleado.html')#Al cumplir se manda al template del home del empleado
        else: #En caso de no ser empleado redirecciona a login
            flash("No cuentas con las credenciales para acceder")#envia mensaje de error por credenciales
            return render_template("login.html")
    except Exception as e: #guardamos errores en caso de que existan
        flash(f"Error de tipo {e}, consulte con su administrador") #se manda mensaje mediante flash con la variable que contiene el error (e)       
        return render_template("login.html")
            
##REGISTRA EMPLEADOS-ADMINISTRADOR    
@app.route('/registro', methods = ["GET", "POST"]) #Ruta de la función en html
def registro():# Definición de función de registro de usuarios
    try:
        if session['tipo']==1:
            cur = mysql.connection.cursor()#creamos un cursor para operaciones sql
            cur.execute("SELECT * FROM tip_usu")#Ejecutamos el cursor con la operación sql designada
            tipo = cur.fetchall()#creamos una variable para almacenar el resultado de la busqueda en el cursor
            cur.close()#cerramos el cursor

            cur = mysql.connection.cursor()#creamos un cursor para operaciones sql
            cur.execute("SELECT * FROM horario")
            hora = cur.fetchall()
            cur.close()

            if request.method == 'GET':#si el metodo es GET renderizamos la plantilla y obtenemos los datos
                return render_template("registro.html", tipo = tipo, hora = hora ) 
            else:
                #obtenemos del formulario los datos por medio de la supervariable GET
                #creamos variables para obtener los valores del formulario mediante request.form
                name = request.form['name']
                email = request.form['email']
                password = request.form['password']
                tip = request.form['tipo']
                hor = request.form['hora']

                cur=mysql.connection.cursor()#obtengo los correos de los usuarios
                cur.execute("Select email from users")#consultamos en la base de datos los usuarios
                val=cur.fetchall()#obtenemos todos los resultados de la consulta
                cur.close()#cerramos el cursor
                if request.form['name']!='' or request.form['name']!='' or request.form['passsword']!='' or request.form['tipo']!='' or request.form['hora']!='':#Se realiza una comparación hacia los campos, si son diferentes de vacio
                    cur = mysql.connection.cursor()#creamos un cursir para hacer la conexion a mysql al cursor
                    cur.execute("INSERT INTO users (name, email, password, id_tip_usu,id_hora) VALUES (%s,%s,%s,%s,%s)", (name, email, password,tip,hor))#Realizamos una insersión hacia la tabla users, donde pedimos los valores de la tabla y los valores almacenados en las variables del formulario
                    mysql.connection.commit()#
                    flash("Registro Exitoso")
                    return redirect(url_for("registro"))
                else:
                    flash("Registro Fallido campos vacios")
                    return redirect(url_for('registro'))
        else:#en caso de no realizarse se manda mensaje de error en login al no contar con las credenciales necesarias
            Notificacion=Notify()
            Notificacion.title("Error de Login")
            Notificacion.message("Error de credenciales")
            flash("No cuentas con las credenciales necesarias para acceder")
            return render_template("login.html")
    except Exception as e:#en caso de algun error en el sistema regresa a la pagina de registro emitiendo un mensaje de error
        flash(f"Error de sistema de tipo {e}")
        return redirect(url_for("registro"))
    

#Funcion cerrar sesión y limpiar la variable 
@app.route('/logout')#ruta para 
def logout():
    session.clear()
    return render_template('login.html')


#### EDITAR REGISTROS EMPLEADOS-ADMINISTRADOR
@app.route('/editar')#ruta para el redireccionamiento de editar registro en administrador
def redirect_update():#definición de la función editar administrador
    try:    
        if session['tipo']==1:#comparación de hacia el tipo de usuario administrador
            redirect(url_for('editar'))
            return render_template('editar.html')#si se cumple se redirecciona a la ruta de editar y carga el template de editar
        else:#Si no lo hace manda mensaje de error al no contar con las credenciales necesarias y retorna al tempkate de login
            flash("No cuentas con las credenciales necesarias para acceder")
            return render_template("login.html")
    except Exception as e:#en caso de algun error en el sistema regresa a la pagina de login emitiendo un mensaje de error
        flash(f"Ocurrio un error de tipo {e} consulte con su administrador")
        return render_template("login.html")
        
    
@app.route('/editar', methods=['GET','POST'])#ruta para editar registro en administador con los metodos de get y post
def update():#definimos con un nombre la función
    try:#hacemos un try para ser a prueba de errores
        if session['tipo']==1:#comparación sobre el tipo de usuario administrador
            if request.method == 'POST' or request.method=='GET':#comparación sobre los metodos post y get
                redirect(url_for('mostrar'))#Si se cumple hace redireccionamiento hacia la ruta de mostrar, se crea variables para obtener los valores del formulario
                email = request.form['email']
                username=request.form['username']
                password = request.form['password']
                tipo = request.form['tipo']
                cur = mysql.connection.cursor()#creación del cursor y haciendo la conexión hacia este
                
                query='Select * from users'#creamos la variable query que almacenara la sentencia sql de seleccion hacia la tabla usuarios
                cur.execute(query)#con el cursor hacemos la ejecución del query
                d=cur.fetchall()#asignamos la variable d al cursor para hacer un diccionario con los valores obtenidos en la selección de toda la sentencia sql
                mysql.connection.commit()
                
                if tipo=='3' or tipo=='2' or tipo=='1':#comparacion sobre los 3 diferentes tipos de usuarios  
                    cur.execute('UPDATE users SET name = %s,password = %s,id_tip_usu=%s where email=%s', (username, password, tipo, email))#cursor con la ejecución de la sentencia sql update
                    flash('USUARIO EDITADO SATISFACTORIAMENTE')
                    return render_template('editar.html', data=d)#obtención de datos y el template de editar al cumplir 
                else:
                    flash("ERROR DE EDICION USUARIO NO EDITADO DEBIDO EL TIPO DE EMPLEADO INSERTADO")#Mensaje de error al introducir tipo de empleado mal, obtencion de datos al no cumplirse
                    return render_template('editar.html', data=d)
            else:
                return render_template('login.html')#al no cumplirse lo anterior se renderizara el template de login
        else:
            flash("Error de acceso, no cuentas con las credenciales para entrar")#Si se sigue sin cumplir lo anterior se manda mensaje en pantalla y renderiza el template de login
            return render_template('login.html')
    except Exception as e:#en caso de algun error en el sistema regresa a la pagina de login emitiendo un mensaje de error
        flash(f"Error de tipo {e} consulte a su administrador")
        return render_template('login.html')

### MOSTRAR REGISTROS EMPLEADOS-ADMINISTRADOR
@app.route('/mostrar')#ruta para mostrar en administrador
def mostrar():#definición del metodo
    try:
        if session['tipo']==1:#comparación para tipo de usuario
            cur = mysql.connection.cursor()#creación del cursor con la conexión el delacara la ejecuón hacia la sentencia sql
            cur.execute("SELECT * FROM users")
            d = cur.fetchall()
            return render_template('editar.html', data=d)#al hacer el diccionario con la variable d obtenemos los datos con la renderización del template editar
        else:
            flash("Error de acceso, no cuentas con las credenciales para entrar")#Si no se cumple mandamos error de acceso, y en el sistema mandamos la excepción si llega a tener algun erro de tipo sistema
            return render_template("login.html")
    except Exception as e:
        flash(f"Ocurrio un error de tipo {e}, consulte con su administrador")
        return render_template("login.html")#renderizamos el template si sucede algín error de sistema
    
    


#### ELIMINAR PERMISO VACACIONES EMPLEADOS-ADMINISTRADOR
@app.route('/delete/<string:id>/<string:name>/<string:email>')#ruta en la eliminacoón de permisos, se pide a llamar el id,nombre y correo del usuario
def delete_vacaiones(id, name, email):#definición para la función con la llamada hacia el id,nombre y correo
    try:
        cur = mysql.connection.cursor()#creación de cursor y conexión para hacer la ejecución de deletes hacia los usuarios y asistencias 
        cur.execute('DELETE FROM users WHERE id = {0}'. format(id))#eliminación mediante el id del usuario
        cur.execute('delete from asistencia where email_emp=%s', (email,))#eliminación mediante el correo del usuario
        mysql.connection.commit()
        remove('modelo{}.xml'.format(name))#se remueve el modelo.xml del usuario mediante su nombre y se remueve tambien de la carpeta data
        path2=("C:/Users/AXL/Downloads/ESTANCIA V 1.7.10/reconocimiento/Data{}".format(name))
        rmtree(path2)#removiendolo del directorio medante la llamada de la variable path2
        flash('USUARIO ELIMANDO SATISFACTORIAMENTE')#muestra de mensaje y redireccionando a la ruta de mostrar, así cargando de nuevo el template de editar
        return redirect(url_for("mostrar"))
    except Exception as e:#en caso de algun error en el sistema regresa a la pagina de login emitiendo un mensaje de error
        flash(f"Error de tipo {e} consulte su adminisrador")
        return render_template("login.html")
        
##REGISTRA EMPLEADOS-RECURSOS HUMANOS    
@app.route('/registro_Recu', methods = ["GET", "POST"]) #Usamos los metodos POST y GET para manipular datos
def registro_Recu():
    try:
        if session['tipo']==3 or session['tipo']==1:# Validamos tipos de usuarios para permitir el acceso
            cur = mysql.connection.cursor()#Consultamos todos los horarios
            cur.execute("SELECT * FROM horario")
            hora = cur.fetchall()
            cur.close()
            notificacion = Notify()#Creamos objeto Notify para enviar mensajes en ordenador local

            if request.method == 'GET':
                return render_template("registro_Recu.html", hora = hora ) #Enviamos los datos al html
            else:
                name = request.form['name'] #Obtenemos los datos de los formularios
                email = request.form['email']
                password = request.form['password']
                hor = request.form['hora']
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO users (name, email, password, id_tip_usu,id_hora) VALUES (%s,%s,%s,%s,%s)", (name, email, password,2,hor))
                mysql.connection.commit()   
                flash("Registro Exitoso") #Envia mensaje de registro exitoso
                notificacion.message="USUARIO YA REGISTRADO."
                notificacion.send()
                return redirect(url_for('registro_Recu'))
        else:
            flash("Error de acceso, no cuentas con las credenciales para entrar") #Mensaje de error de acceso
            return render_template("login.hmtl") #Retorna al templata con el mensaje respectivo
    except Exception as e:#Obtenemos el tipo de error y los mostramos en pantalla
        flash(f"Error de sistema de tipo: {e} consulte con su administrador")
        return render_template("login.html")

#### EDITAR REGISTROS EMPLEADOS-RECURSOS HUMANOS
#Funcion de edicion en el template los datos en recursos humanos y redireccionar
@app.route('/editar_Recu')
def redirect_update_Recu():
        try:
            if session['tipo']==3:#Permite solo el acceso al usuario de recursos humanos
                redirect('/editar_Recu')
                return render_template('editar_Recu.html')
            else:
                notificacion=Notify()#De lo contrario devuelve a la pagina de inicio de sesion
                notificacion.message="Acceso denegado no tienes permiso"
                notificacion.send()
                flash('Usuario no logeado con aterioridad')
                return render_template('login.html')
        except Exception as e:#Capturamos errores en caso de existir
            flash(f'Error de tipo {e} consulte a su adminstrador')
            return render_template('login.html')
   
#Funcion que muestra los datos y obtiene los datos del formulario para su edicion en base de datos
@app.route('/editar_Recu', methods=['GET','POST'])
def update_Recu():
    try:    
        if session['tipo']==3:# Valida que el usuario sea de tipo Recursos Humanos
            if request.method == 'POST' or request.method=='GET': #Obtiene los datos
                redirect('/editar_Recu') #Redireccionamos a la funcion para actualizar los datos
                email = request.form['email']#Obtenemos los datos del formulario
                username=request.form['username']
                password = request.form['password']
                cur = mysql.connection.cursor()#Inicializamos el oobjeto de tipo cursor
                cur.execute('UPDATE users SET name = %s,password = %s,id_tip_usu=%s where email=%s', (username, password, 2, email))
                query='Select * from users where id_tip_usu=2' #Contruimos el query para la base de datos
                cur.execute(query) #Ejecutamos el query 
                d=cur.fetchall() #Obtenemos los datos dentro de la variable como un diccionario de datos
                mysql.connection.commit() #Procuramos que la sentencia SQL inicie y termine correctamente liberando el cursor
                flash('USUARIO EDITADO SATISFACTORIAMENTE') #Enviamos mensaje de 
                return render_template('editar_Recu.html', data=d)
        else:
            flash(f"Error de acceso {e}")
            return render_template('login.html')# Obtenemos el tipo de error que exista
    except Exception as e:
            flash(f"Error de tipo {e} consulte con su administrador") #Enviamos errores en login en caso de 
            return render_template('login.html')

        
### MOSTRAR REGISTROS EMPLEADOS-RECURSOS HUMANOS
@app.route('/mostrar_Recu') #Muestra en la tabla de recursamiento los datos
def mostrar_Recu():
    try:    
        if session['tipo']==3:# Valida el acceso para el tipo de usuario
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM users where id_tip_usu=2") #Construimos el query para obtener los usuarios de tipo empleado
            d = cur.fetchall() #Obtenemos el resultado en la variable "d"
            return render_template('editar_Recu.html', data=d)# Devolvemos los datos de la consulta en el template
        else:
            flash("Error de acceso, no cuentas con las credenciales para entrar") #Enviamos mensaje de error
            return render_template("login.html")
    except Exception as e:
        flash(f"Ocurrio un error de tipo {e}, consulte con su administrador")
        return render_template("login.html")
    
#### ELIMINAR REGISTROS EMPLEADOS-RECURSOS HUMANOS
#Ruta y definición de la función para hacer eliminación en recursos humanos
@app.route('/delete_Recu/<string:id>/<string:name>/<string:email>')
def delete_usuario_Recu(id,name,email):
    try:
        cur=mysql.connection.cursor()
        cur.execute('delete from users where id={0}'.format(id))
        cur.execute('delete from asistencia where email_emp=%s', (email,))
        mysql.connection.commit()
        remove('modelo{}.xml'.format(name))
        path2=("C:/Users/AXL/Downloads/ESTANCIA V 1.7.8/reconocimiento/Data/{}".format(name))
        rmtree(path2)
        flash('USUARIO ELIMANDO SATISFACTORIAMENTE')
        return redirect(url_for('mostrar_Recu'))
    except Exception as e:
        flash(f"Error de tipo {e} consulte a su administrador")
    
### REGISTRO EMPLEADO-JUSTIFICANTE
#Valida el acceso del tipo de usuario y conforme ello 
@app.route('/emple_justificante') 
def emple_justificante():
    try:
        if session['tipo']==2:
            flash(f"Exito al acceder {session['name']}")
            return render_template('registro_Emple_Justificante.html')
        else:
            flash("Error de acceso, no cuentas con las credenciales para entrar")
            return render_template("login.html")
    except Exception as e:
        flash(f"Ocurrio un error de tipo {e}, consulte con su administrador")
        return render_template("login.html")
    
#Entrando en la funcion muestra los justificantes del usuario y valida la entrada conforme el usuario
@app.route('/mostrar_justificante')
def mostrar_emple_Justificante():
    try:
        if session['tipo']==2:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM justificantes where empcorreo=%s", (session['email'],))
            d = cur.fetchall()
            return render_template('editar_Emple_Justificante.html', data=d)
        else:
            flash("Error de acceso, no cuentas con las credenciales para entrar")
            return render_template("login.html")
    except Exception as e:
        flash(f"Ocurrio un error de tipo {e}, consulte con su administrador")
    
#Funcion para subir una justificacion
#Valida el ingreso por medio del tipo de usuario y envia los datos para insertarlos en la base de datos
@app.route('/subir_justificante', methods=['GET','POST'])
def subir_justificante():
    try:
        if session['tipo']==2:
            app.logger.warning(f"Entrada a la funcion")
            ids=''
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM justificantes")
            d=cur.fetchall()
            cur.close()
            if request.method == 'GET':
                return render_template("registro_Emple_Justificante.html",data=d) 
            else:
                fecha = request.form['fecha']
                mensaje = request.form['mensaje']

                curl=mysql.connection.cursor()
                curl.execute('Select id from users where email=%s', (session['email'],))
                ids=curl.fetchone()
                if ids!='':
                    cur = mysql.connection.cursor()
                    cur.execute("INSERT INTO justificantes (empcorreo,fecha,motivo,id_emp) VALUES (%s,%s,%s,%s)", (session['email'],fecha,mensaje,ids,))
                    mysql.connection.commit()   
                    mensaje='Exito al enviar el justificante'
                    flash(mensaje)
                    return render_template("registro_Emple_Justificante.html",data=d) 
                else:
                    flash('Registro de justificante no valido o no existe el usuario')
                    return render_template("registro_Emple_Justificante.html",data=d)
        else:
            flash("Error de acceso, no cuentas con las credenciales para entrar")
            return render_template("login.html") 
    except Exception as e:
        flash(f"Error de sistema en justificante {e}")
        return redirect(url_for("subir_justificante"))


#Visualizar asistencias del empleado por medio del reconocimiento facial buscando por medio del correo
@app.route("/visualizar_asistencias")
def asistencias():
    try:
        curl=mysql.connection.cursor()
        curl.execute("SELECT * FROM asistencia where email_emp=%s", (session['email'],))
        a = curl.fetchall()
    except Exception as e:
        flash(f"Error de tipo : {e}")
    finally:
        return render_template("asistencias.html", asistencias=a)

#Pase de lista por medio del reconocimiento facial
@app.route('/pase_asistencia_emp')
def asistencia():
    try:
        flash(f"El reconocimiento funciona {session['name']}")
        val=capturarostros.captura(session['name'])#devuelve 1 cuando el usuario ya tiene un modelo registrado
        if val==0: #En caso de que no exista el modelo iniciara el proceso de captura y creacion de modelo de rostros
            flash(f"Estamos entrenando la IA para reconocer tu rostro {session['name']}")
            flash(f"Presiona otra vez el boton para registrar la asistencia")
            entrenandoRF.entrenar(session['name'])#entranara la inteligencia artificial
            return redirect(url_for('asistencias'))
        else:#En el caso contrario solo iniciara el reconoicmiento facial
            flash(f"Reconociendo tu rostro {session['name']}")
            reconocimientofacial.facial(session['name'])
            cur = mysql.connection.cursor()
            cur.execute("insert into asistencia (email_emp) values (%s)", (session['email'],))
            cur.execute('select estado (%s)',(session['email'],))
            cur.close()
            return redirect(url_for('asistencias'))
        
    except Exception as e:#en caso de existir errores informara al usuario de estos en un mensaje de error
        error=f'El reconocimiento ha fallado debido a un error de libreria {e}'
        flash(error)
        app.logger.warning(f"Error de tipo {e}")
        return redirect(url_for("asistencias"))
    
    
#Visualizar asistencias del empleado por medio del reconocimiento facial
@app.route("/visualizar_asistencias_admin")
def asistencias_admin():
    try:
        curl=mysql.connection.cursor()
        curl.execute("SELECT * FROM asistencia where email_emp=%s", (session['email'],))
        a = curl.fetchall()
    except Exception as e:
        flash(f"Error de tipo : {e}")
    finally:
        return render_template("asistencias_admin.html", asistencias=a)

#Pase de lista por medio del reconocimiento facial
@app.route('/pase_asistencia_admin')
def asistencia_admin():
    try:
        flash(f"El reconocimiento funciona {session['name']}")
        val=capturarostros.captura(session['name'])#devuelve 1 cuando ya existe
        if val==0:
            flash(f"Estamos entrenando la IA para reconocer tu rostro {session['name']}")
            flash(f"Presiona otra vez el boton para registrar la asistencia")
            entrenandoRF.entrenar(session['name'])
            return redirect(url_for('asistencias_admin'))
        else:
            flash(f"Reconociendo tu rostro {session['name']}")
            reconocimientofacial.facial(session['name'])
            cur = mysql.connection.cursor()
            cur.execute("insert into asistencia (email_emp) values (%s)", (session['email'],))
            cur.execute('select estado (%s)',(session['email'],))
            cur.close()
            return redirect(url_for('asistencias_admin'))
        
    except Exception as e:
        error=f'El reconocimiento ha fallado debido a un error de libreria {e}'
        flash(error)
        app.logger.warning(f"Error de tipo {e}")
        return redirect(url_for("asistencias_admin"))
    
#Visualizar asistencias del empleado por medio del reconocimiento facial
@app.route("/visualizar_asistencias_Recu")
def asistencias_Recu():
    try:
        curl=mysql.connection.cursor()
        curl.execute("SELECT * FROM asistencia where email_emp=%s", (session['email'],))
        a = curl.fetchall()
    except Exception as e:
        flash(f"Error de tipo : {e}")
    finally:
        return render_template("asistencias_Recu.html", asistencias=a)

#Pase de lista por medio del reconocimiento facial en el usuario de recursos humanos
@app.route('/pase_asistencia_Recu')
def asistencia_Recu():
    try:
        flash(f"El reconocimiento funciona {session['name']}")
        val=capturarostros.captura(session['name'])#devuelve 1 cuando ya existe
        if val==0:
            flash(f"Estamos entrenando la IA para reconocer tu rostro {session['name']}")
            flash(f"Presiona otra vez el boton para registrar la asistencia")
            entrenandoRF.entrenar(session['name'])
            return redirect(url_for('asistencias_Recu'))
        else:
            flash(f"Reconociendo tu rostro {session['name']}")
            reconocimientofacial.facial(session['name'])
            cur = mysql.connection.cursor()
            cur.execute("insert into asistencia (email_emp) values (%s)", (session['email'],))
            cur.execute('select estado (%s)',(session['email'],))
            cur.close()
            return redirect(url_for('asistencias_Recu'))
        
    except Exception as e:
        error=f'El reconocimiento ha fallado debido a un error de libreria {e}'
        flash(error)
        app.logger.warning(f"Error de tipo {e}")
        return redirect(url_for("asistencias"))

#Funciones de horarios que obtiene las horas y puede crear el horario de empleado
@app.route('/registro_Hora', methods = ["GET", "POST"])
def registro_Hora():

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM horainicial")
    inicial = cur.fetchall()
    cur.close()
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM horafinal")
    final = cur.fetchall()
    cur.close()
    
    
    if request.method == 'GET':
        return render_template("registro_Hora.html", inicial = inicial, final = final ) 
    else:
        
        email = request.form['email']
        horaini = request.form['inicial']
        horafinal = request.form['final']
        
        ini=horaini+':00:00'
        fin=horafinal+':00:00'
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO horas (email,ini,fin) VALUES (%s,%s,%s)", (email,ini, fin))
        mysql.connection.commit()   
        flash("Registro Exitoso")
        return redirect(url_for("registro_Hora"))


###EDITAR HORARIO EMPLEADOS-ADMINISTRADOR
@app.route('/editar_Hora')
def redirect_update_Hora():
    redirect(url_for('editar_Hora'))
    return render_template('editar_Hora')
    
#Valida el tipo de usuario y consulta los horarios de los empleados
@app.route('/editar_Hora', methods=['GET','POST'])
def update_Hora():
    try:
        if session['tipo']==1:
            if request.method == 'POST' or request.method=='GET':
                redirect('/editar_Hora')

                email=request.form['email']
                ini=request.form['inicial']
                fin=request.form['final']

                cur=mysql.connection()
                cur.execute('select hora_inicial from horainicial')
                inicial=cur.fetchall()

                curl=mysql.connection()
                curl.execute('select hora_final from horafinal')
                final=curl.fetchall()

                cu=mysql.connection()
                cu.execute('select * from horas')
                d=cu.fetchall()

                ini=ini+'::0000'    
                fin=fin+':00:00'
                
                curl.execute('update horas set ini=%s where email=%s', (ini,email))
                curl.execute('update horas set fin=%s where email=%s', (fin, email))
                
                flash('USUARIO EDITADO SATISFACTORIAMENTE')
                return render_template('editar_Hora.html', inicial=inicial, final=final, data=d)
                
    except Exception as e:
        flash(f"Error de tipo {e} contacte a su administrador")
        return render_template('editar_Hora.html', inicial=inicial, final=final, data=d)
        
### MOSTRAR HORARIOS EMPLEADOS-ADMINISTRADOR
# Muestra todas las horas disponibles de la base de datos para la creacion de horarios para empleados
@app.route('/mostrar_Hora')
def mostrar_Hora():
    try:
        if 'email' in session and 'password' in session:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM horas")
            d = cur.fetchall()
            return render_template('editar_Hora.html', data=d)
        else:
            notificacion=Notify()
            notificacion.message="Acceso denegado no tienes permiso"
            notificacion.send()
            flash('Usuario no logeado con aterioridad')
            return render_template("login.html")
    except Exception as e:
        flash(f"Error de tipo {e} contacte con su administrador")
        return render_template("editar_Hora.html", data=d)
        
#### ELIMINAR HORARIOS EMPLEADOS-ADMINISTRADOR
#Obtiene el id del horario y elimina conforme este
@app.route('/delete_Hora/<string:id>')
def delete_Hora(id):
    if 'email' in session and 'password' in session:
        try:
            cur = mysql.connection.cursor()
            cur.execute('DELETE FROM horas WHERE id = {0}'. format(id))
            mysql.connection.commit()
            flash('USUARIO ELIMANDO SATISFACTORIAMENTE')
            return redirect(url_for("mostrar_Hora"))
        except Exception as e:
            flash(f'Error de tipo: {e} consulte a su administrador')
            return redirect(url_for("mostrar_Hora"))
    else:
        notificacion=Notify()
        notificacion.message="Acceso denegado no tienes permiso"
        notificacion.send()
        flash('Usuario no logeado con anterioridad')
        return render_template("login.html")

### REGISTRO EMPLEADO-JUSTIFICANTE
#Valida los campos de usuario y sesion para validar el acceso a la funcion
@app.route('/emple_vacaciones')
def emple_vacaciones():
    if 'email' in session and 'password' in session:
        return render_template('registro_Emple_Vacaciones.html')
    else:
        notificacion=Notify()
        notificacion.message="Acceso denegado no tienes permiso"
        notificacion.send()
        flash('Usuario no logeado con aterioridad')
        return render_template("login.html")


#Entrando en la funcion para mostrar las vacaciones
#Muestra los permisos de vacaciones y su estado de aprobacion
@app.route('/mostrar_vacaciones')
def mostrar_emple_Vacaciones():
    if 'email' in session and 'password' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM vacaciones where empcor=%s", (session['email'],))
        d = cur.fetchall()
        return render_template('editar_Emple_Vacaciones.html', data=d)
    else:
        notificacion=Notify()
        notificacion.message="Acceso denegado no tienes permiso"
        notificacion.send()
        flash('Usuario no logeado con aterioridad')
        return render_template("login.html")
    
#### REGISTRAR VACACIONES EMPLEADO
#Registra permisos de vacaciones con todos sus campos, validando al igual el acceso a la funcion
@app.route('/subir_vacaciones', methods=['GET','POST'])
def subir_vacaciones():
    try:
        if 'email' in session and 'password' in session:
            app.logger.warning(f"Entrada a la funcion")
            ids=''
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM vacaciones")
            d=cur.fetchall()
            cur.close()

            if request.method == 'GET':
                return render_template("registro_Emple_Vacaciones.html",data=d) 
            else:
                fecha = request.form['fecha']
                mensaje = request.form['mensaje']

                curl=mysql.connection.cursor()
                curl.execute('Select id from users where email=%s', (session['email'],))
                ids=curl.fetchone()
                if ids!='':
                    cur = mysql.connection.cursor()
                    cur.execute("INSERT INTO vacaciones (empcor,fecha,moti,id_emplea) VALUES (%s,%s,%s,%s)", (session['email'],fecha,mensaje,ids,))
                    mysql.connection.commit()   
                    mensaje='Exito al enviar el vacaciones'
                    flash(mensaje)
                    return render_template("registro_Emple_Vacaciones.html",data=d) 
                else:
                    flash('Registro de vacaciones no valido o no existe el usuario')
                    return render_template("registro_Emple_Vacaciones.html",data=d) 
        else:
            notificacion=Notify()
            notificacion.message="Acceso denegado no tienes permiso"
            notificacion.send()
            flash('Usuario no logeado con aterioridad')
            return render_template("login.html")
    except Exception as e:
        flash(f"Error de sistema en vacaciones {e}")
        return redirect(url_for("subir_vacaciones"))

##MOSTRAR VACACIONES EN ADMINISTRADOR
#Entrando en la funcion para mostrar las vacaciones    
@app.route('/mostrar_admin_vacaciones')
def mostrar_admin_vacaciones():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM vacaciones")
    d = cur.fetchall()
    return render_template('editar_Admin_Vacaciones.html', data=d)

#### ACEPTAR VACACIONES EMPLEADOS-ADMINISTRADOR
#Conforme el id del permiso de vacaciones acepta las vacaciones
@app.route('/aceptadovacaciones/<string:id>')
def aceptado_vacaciones(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('UPDATE vacaciones set estado="Aceptado" where id=%s', (id,))
        mysql.connection.commit()
        flash('USUARIO ACTUALIZADO SATISFACTORIAMENTE')
        return redirect(url_for("mostrar_admin_vacaciones"))
    except Exception as e:
        flash(f"Error de tipo {e} consulte su administrador")
        return render_template("login.html")

#### ACEPTAR VACACIONES EMPLEADOS-ADMINISTRADOR
#Rechaza el permiso de vacaciones
@app.route('/rechazadovacaciones/<string:id>')
def rechazado_vacaciones(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('UPDATE vacaciones set estado="Rechazado" where id=%s', (id,))
        mysql.connection.commit()
        flash('USUARIO ACTUALIZADO SATISFACTORIAMENTE')
        return redirect(url_for("mostrar_admin_vacaciones"))
    except Exception as e:
        flash(f"Error de tipo {e} consulte su administrador")
        return render_template("login.html")

##MOSTRAR JUSTIFICACIÓN EN ADMINISTRADOR
#Entrando en la funcion para mostrar las justificaciones    
@app.route('/mostrar_admin_justificaciones')
def mostrar_admin_justificaciones():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM justificantes")
    d = cur.fetchall()
    return render_template('editar_Admin_Justificante.html', data=d)

#### ACEPTAR JUSTIFICANTES EMPLEADOS-ADMINISTRADOR
#Acepta los justificantes
@app.route('/aceptadojustificantes/<string:id>')
def aceptado_justificantes(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('UPDATE justificantes set estado="Aceptado" where id=%s', (id,))
        mysql.connection.commit()
        flash('USUARIO ACTUALIZADO SATISFACTORIAMENTE')
        return redirect(url_for("mostrar_admin_justificaciones"))
    except Exception as e:
        flash(f"Error de tipo {e} consulte su administrador")
        return render_template("login.html")

#### RECHAZAR JUSTIFICANTES EMPLEADOS-ADMINISTRADOR
#Rechaza los justificantes dependiendo de su ID
@app.route('/rechazadojustificantes/<string:id>')
def rechazado_justificantes(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('UPDATE justificantes set estado="Rechazado" where id=%s', (id,))
        mysql.connection.commit()
        flash('USUARIO ACTUALIZADO SATISFACTORIAMENTE')
        return redirect(url_for("mostrar_admin_justificaciones"))
    except Exception as e:
        flash(f"Error de tipo {e} consulte su administrador")
        return render_template("login.html")

##MOSTRAR PERMISOS EN ADMINISTRADOR
#Entrando en la funcion para mostrar las justificaciones    
@app.route('/mostrar_admin_permisos')
def mostrar_admin_permisos():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM permisos")
    d = cur.fetchall()
    return render_template('editar_Admin_Permisos.html', data=d)

#### ACEPTAR PERMISOS EMPLEADOS-ADMINISTRADOR
#Acepta permisos dependiendo del ID
@app.route('/aceptadopermisos/<string:id>')
def aceptado_permisos(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('UPDATE permisos set estado="Aceptado" where id=%s', (id,))
        mysql.connection.commit()
        flash('USUARIO ACTUALIZADO SATISFACTORIAMENTE')
        return redirect(url_for("mostrar_admin_permisos"))
    except Exception as e:
        flash(f"Error de tipo {e} consulte su administrador")
        return render_template("login.html")

#### RECHAZAR PERMISOS EMPLEADOS-ADMINISTRADOR
#Rechaza los permisos dependiendo el ID
@app.route('/rechazadopermisos/<string:id>')
def rechazado_permisos(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('UPDATE permisos set estado="Rechazado" where id=%s', (id,))
        mysql.connection.commit()
        flash('USUARIO ACTUALIZADO SATISFACTORIAMENTE')
        return redirect(url_for("mostrar_admin_permisos"))
    except Exception as e:
        flash(f"Error de tipo {e} consulte su administrador")
        return render_template("login.html")


##MOSTRAR VACACIONES EN RECURSOS HUMANOS
#Entrando en la funcion para mostrar las vacaciones    
@app.route('/mostrar_recu_vacaciones')
def mostrar_recu_vacaciones():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM vacaciones")
    d = cur.fetchall()
    return render_template('editar_Recu_Vacaciones.html', data=d)

#### ACEPTAR VACACIONES EMPLEADOS-RECURSOS HUMANOS
#Aceptar permisos dependiendo del ID
@app.route('/aceptadovacacionesrh/<string:id>')
def aceptado_vacaciones_recu(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('UPDATE vacaciones set estado="Aceptado" where id=%s', (id,))
        mysql.connection.commit()
        flash('USUARIO ACTUALIZADO SATISFACTORIAMENTE')
        return redirect(url_for("mostrar_recu_vacaciones"))
    except Exception as e:
        flash(f"Error de tipo {e} consulte su administrador")
        return render_template("login.html")

#### RECHAZADO VACACIONES EMPLEADOS-RECURSOS HUMANOS
#Rechaza justificantes dependiendo del ID
@app.route('/rechazadovacacionesrh/<string:id>')
def rechazado_vacaciones_recu(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('UPDATE vacaciones set estado="Rechazado" where id=%s', (id,))
        mysql.connection.commit()
        flash('USUARIO ACTUALIZADO SATISFACTORIAMENTE')
        return redirect(url_for("mostrar_recu_vacaciones"))
    except Exception as e:
        flash(f"Error de tipo {e} consulte su administrador")
        return render_template("login.html")


##MOSTRAR JUSTIFICACIÓN EN RECURSOS HUMANOS
#Entrando en la funcion para mostrar las justificaciones
@app.route('/mostrar_recu_justificaciones')
def mostrar_recu_justificaciones():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM justificantes")
    d = cur.fetchall()
    return render_template('editar_Recu_Justificante.html', data=d)


#### ACEPTAR JUSTIFICANTES EMPLEADOS-RECURSOS HUMANOS
#Acepta justificantes dependiendo del ID
@app.route('/aceptadojustificantesrh/<string:id>')
def aceptado_justificantes_recu(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('UPDATE justificantes set estado="Aceptado" where id=%s', (id,))
        mysql.connection.commit()
        flash('USUARIO ACTUALIZADO SATISFACTORIAMENTE')
        return redirect(url_for("mostrar_recu_justificaciones"))
    except Exception as e:
        flash(f"Error de tipo {e} consulte su administrador")
        return render_template("login.html")

#### RECHAZADO JUSTIFICANTES EMPLEADOS-RECURSOS HUMANOS
#Rechaza el justificante dependiendo del ID
@app.route('/rechazadojustificantesrh/<string:id>')
def rechazado_justificaciones_recu(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('UPDATE justificantes set estado="Rechazado" where id=%s', (id,))
        mysql.connection.commit()
        flash('USUARIO ACTUALIZADO SATISFACTORIAMENTE')
        return redirect(url_for("mostrar_recu_justificaciones"))
    except Exception as e:
        flash(f"Error de tipo {e} consulte su administrador")
        return render_template("login.html")

##MOSTRAR PERMISOS EN RECURSOS HUMANOS
#Entrando en la funcion para mostrar las permisos
@app.route('/mostrar_recu_permisos')
def mostrar_recu_permisos():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM permisos")
    d = cur.fetchall()
    return render_template('editar_Recu_Permisos.html', data=d)

#### ACEPTAR VACACIONES EMPLEADOS-RECURSOS HUMANOS
#Acepta los permisos dependiendo del ID
@app.route('/aceptadopermisosrh/<string:id>')
def aceptado_permisos_recu(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('UPDATE permisos set estado="Aceptado" where id=%s', (id,))
        mysql.connection.commit()
        flash('USUARIO ACTUALIZADO SATISFACTORIAMENTE')
        return redirect(url_for("mostrar_recu_permisos"))
    except Exception as e:
        flash(f"Error de tipo {e} consulte su administrador")
        return render_template("login.html")

#### RECHAZADO VACACIONES EMPLEADOS-RECURSOS HUMANOS
#Rechaza los permisos dependiendo del ID
@app.route('/rechazadopermisosrh/<string:id>')
def rechazado_permisos_recu(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('UPDATE permisos set estado="Rechazado" where id=%s', (id,))
        mysql.connection.commit()
        flash('USUARIO ACTUALIZADO SATISFACTORIAMENTE')
        return redirect(url_for("mostrar_recu_permisos"))
    except Exception as e:
        flash(f"Error de tipo {e} consulte su administrador")
        return render_template("login.html")

#### REGISTRO PERMISOS-EMPLEADO
#Permite el acceso a la funcion de los permisos de empleado
@app.route('/emple_permisos')
def emple_permisos():
    return render_template('registro_Emple_Permisos.html')

#Muestra los justificantes y permisos
@app.route('/mostrar_permisos')
def mostrar_emple_Permisos():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM permisos where correo=%s", (session['email'],))
    d = cur.fetchall()
    return render_template('editar_Emple_Permisos.html', data=d)

#### REGISTRAR PERMISOS EMPLEADO dependiendo de su correo insertado
@app.route('/subir_permisos', methods=['GET','POST'])
def subir_permisos():
    try:
        app.logger.warning(f"Entrada a la funcion")
        ids=''
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM permisos")
        d=cur.fetchall()
        cur.close()
        
        if request.method == 'GET':
            return render_template("registro_Emple_Permisos.html",data=d) 
        else:
            fecha = request.form['fecha']
            mensaje = request.form['mensaje']
            
            curl=mysql.connection.cursor()
            curl.execute('Select id from users where email=%s', (session['email'],))
            ids=curl.fetchone()
            if ids!='':
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO permisos (correo,fecha,motivo,id_empleado) VALUES (%s,%s,%s,%s)", (session['email'],fecha,mensaje,ids,))
                mysql.connection.commit()   
                mensaje='Exito al enviar el permiso'
                flash(mensaje)
                return render_template("registro_Emple_Permisos.html",data=d) 
            else:
                flash('Registro de vacaciones no valido o no existe el usuario')
                return render_template("registro_Emple_Permisos.html",data=d) 
    except Exception as e:
        flash(f"Error de sistema en vacaciones {e}")
        return redirect(url_for("subir_permisos"))

####REPORTES
#definimos primero el renderizado del template hacia reportes.html
@app.route('/reporte')#definición de la ruta para reportes
def reporte():
    return render_template('reportes.html')#aquí hacemos el renderizado del template

#definimos la función para el boton que hara la descarga del reporte
@app.route('/download/report/pdf')#definición para la ruta, mandamos a llamar a la función
def download_report():#función
    try:#abrimos un try para contener cualquier error
        cur = mysql.connection.cursor()#abrimos un cursor y hacemos la conexión con MySQL al cursor
        cur.execute("SELECT * FROM horas")#con el cursor hacemos la sentencia del sql
        result = cur.fetchall()#creamos una variable que se convertira de tipo diccionario, ya que almacenará los resultados de la sentencia sql

        pdf = FPDF()#Se crea una variable llamada pdf para meter dentro de ellá la biblioteca FPDF
        pdf.add_page()#con la variable mandamos a llamar la función para agregar una pagina

        page_width = pdf.w - 2 * pdf.l_margin #Hacemos los margin del reporte
        #Asignamos un tipo de letra
        pdf.set_font('Times','B',14.0)
        pdf.cell(page_width,0.0,'Usuarios',align='C')#Con cell hacemos una celda para poner el titulo y lo centramos
        pdf.ln(10)#Hacemos salto de linea

        pdf.set_font('Courier','',12)

        col_width = page_width/4#Hacemos 4 columnas

        pdf.ln(1)

        th = pdf.font_size
        #creamos un diccionario para poder mostrar los resultados que sacamos de la base de datos
        #hacemos las celdas para mostrar los resultados del sql
        for row in result:
            pdf.cell(col_width, th, str(row['idhoras']), border=1)
            pdf.cell(col_width, th, row['email'], border=1)
            pdf.cell(col_width, th, str(row['ini']), border=1)
            pdf.cell(col_width, th, str(row['fin']), border=1)
            pdf.ln(th)
        pdf.ln(10)

        pdf.set_font('Times','',10.0)
        pdf.cell(page_width, 0.0, '- end of report -', align='C')
        #Retornamos y hacemos el archivo a pdf con un nombre
        return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf', headers={'Content-Disposition':'attachment;filename=horario_report.pdf'})
    except Exception as e:#para mostrar la excepción por si sale algún error
        print(e)
    finally:
        cur.close()#Finalizamos cerrando el cursor


####REPORTES ASISTENCIA
#Reporte para asistencia, se sigue la misma sintaxis que horarios
@app.route('/reporte_asistencia')
def reporte_asistencia():
    return render_template('reportes_asistencia.html')

@app.route('/download/report/asistencia/pdf')
def download_report_asistencia():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM asistencia")
        result = cur.fetchall()

        pdf = FPDF()
        pdf.add_page()

        page_width = pdf.w - 2 * pdf.l_margin

        pdf.set_font('Times','B',14.0)
        pdf.cell(page_width,0.0,'Usuarios',align='C')
        pdf.ln(5)

        pdf.set_font('Courier','',12)

        col_width = page_width/4

        pdf.ln(1)

        th = pdf.font_size

        for row in result:
            pdf.cell(col_width, th, str(row['id']), border=1)
            pdf.cell(col_width, th, str(row['hora']), border=1)
            pdf.cell(col_width, th, str(row['fecha']), border=1)
            pdf.cell(col_width, th, (row['email_emp']), border=1)
            pdf.ln(th)
        pdf.ln(5)

        pdf.set_font('Times','',10.0)
        pdf.cell(page_width, 0.0, '- end of report -', align='C')

        return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf', headers={'Content-Disposition':'attachment;filename=asistencia_report.pdf'})
    except Exception as e:
        print(e)
    finally:
        cur.close()

####REPORTES ASISTENCIA PARA RECURSOS HUMANOS
#Reporte para asistencia, se sigue la misma sintaxis que horarios
@app.route('/reporte_asistencia_recu')
def reporte_asistencia_recu():
    return render_template('reportes_asistencia_Recu.html')

@app.route('/download/report/asistencia/recu/pdf')
def download_report_asistencia_recu():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM asistencia")
        result = cur.fetchall()

        pdf = FPDF()
        pdf.add_page()

        page_width = pdf.w - 2 * pdf.l_margin

        pdf.set_font('Times','B',14.0)
        pdf.cell(page_width,0.0,'Usuarios',align='C')
        pdf.ln(5)

        pdf.set_font('Courier','',12)

        col_width = page_width/4

        pdf.ln(1)

        th = pdf.font_size

        for row in result:
            pdf.cell(col_width, th, str(row['id']), border=1)
            pdf.cell(col_width, th, str(row['hora']), border=1)
            pdf.cell(col_width, th, str(row['fecha']), border=1)
            pdf.cell(col_width, th, (row['email_emp']), border=1)
            pdf.ln(th)
        pdf.ln(5)

        pdf.set_font('Times','',10.0)
        pdf.cell(page_width, 0.0, '- end of report -', align='C')

        return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf', headers={'Content-Disposition':'attachment;filename=asistencia_report.pdf'})
    except Exception as e:
        print(e)
    finally:
        cur.close()

####REPORTES ASISTENCIA PARA EMPLEADOS
@app.route('/reporte_asistencia_emple')
def reporte_asistencia_emple():
    return render_template('reportes_asistencia_Emple.html')

@app.route('/download/report/asistencia/emple/pdf')
def download_report_asistencia_emple():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM asistencia")
        result = cur.fetchall()

        pdf = FPDF()
        pdf.add_page()

        page_width = pdf.w - 2 * pdf.l_margin

        pdf.set_font('Times','B',14.0)
        pdf.cell(page_width,0.0,'Usuarios',align='C')
        pdf.ln(5)

        pdf.set_font('Courier','',12)

        col_width = page_width/4

        pdf.ln(1)
    
        th = pdf.font_size
        for row in result:
            pdf.cell(col_width, th, str(row['id']), border=1)
            pdf.cell(col_width, th, str(row['hora']), border=1)
            pdf.cell(col_width, th, str(row['fecha']), border=1)
            pdf.cell(col_width, th, (row['email_emp']), border=1)
            pdf.ln(th)
        pdf.ln(5)

        pdf.set_font('Times','',10.0)
        pdf.cell(page_width, 0.0, '- end of report -', align='C')

        return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf', headers={'Content-Disposition':'attachment;filename=asistencia_report.pdf'})
    except Exception as e:
        print(e)
    finally:
        cur.close()


if __name__ == '__main__': #Si el codigo se esta ejecutando directamente abre el puerto y corre el programa directamente
    app.run(port = 5000, debug=True) 