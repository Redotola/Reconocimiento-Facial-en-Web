import cv2
import os
import imutils

def captura(name):#Recibe el nombre del que desea que 
    personName=name#Guardamos el nombre dentro de la variable
    dataPath='C:/Users/AXL/Downloads/ESTANCIA V 1.7.10/reconocimiento/Data'
    '''
    Importante: La variable "dataPath" necesita estar dentro del proyecto en la carpeta "Data" por lo cual
    se pide que se copie la ruta de la carpeta "Data" del proyecto para guardar las imagenes y manipular los datos 
    y modelos que se generan dentro de esta carpeta
    Esto se debe aplicar en todas las rutas de los 3 scripts
    '''
    personpath=dataPath+ '/' + personName #Se concatena la ruta de la carpeta y se añade el nombre de la persona
    print(personpath)#Se imprime la ruta de la carpeta para comprobar 

    if not os.path.exists(personpath):#Si no existe la carpeta de la persona la crea de lo contrario devuelve 1
        print("Carpeta creada: ", personpath)
        os.makedirs(personpath)
    else:
        return 1

    #captura de video dinamico de la camara web de la persona
    cap=cv2.VideoCapture(0,cv2.CAP_DSHOW)


    faceClassif=cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
    '''Se utiliza el modelo haarcascade para clasificacion de los rostros y el modelo predefinido de frontal_face
    este modelo permite reconocer rostros por medio de un algoritmo que define los contornos y forma de un rostro por 
    delante
    '''
    count=0 #Variable contador de las capturas tomadas por el programa

    while True:#Mientras verdadero
        ret, frame=cap.read()#captura el frame obtenido por la camara y lo lee
        if ret==False:break#Si ret es False rompe el ciclo
        frame = imutils.resize(frame, width=640)#Guardamos los frames o capturas del rostro redimensionandolos con la funcion
        #resize es una funcion que redimensiona los frames 
        gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        '''
        Convierte los frames obtenidos con escalas de grises
        '''
        auxframe=frame.copy()#Copia el frame en una variable copia que almacenaremos en una nueva variable

        faces=faceClassif.detectMultiScale(gray, 1.3, 5)#Redimensiona las caras en grises
        
        
        for (x,y,w,h) in faces: #Con variables auxiliares nos apoyamos para manipular los contornos que tendra el rostro
            cv2.rectangle(frame,(x,y), (x+w,y+h), (0,255,0),2)#Crea un rectangulo alrededor de la cara
            rostro=auxframe[y:y+h,x:x+w]
            rostro=cv2.resize(rostro,(150,150), interpolation=cv2.INTER_CUBIC)#redimensiona los frames obtenidos
            cv2.imwrite(personpath+'/rostro_{}.jpg'.format(count),rostro)#Escribe los frames en la ruta especificada
            '''nombrandola con el nombre del contador'''
            count+=1#aumenta el contador 1 en 1 para 
        cv2.imshow('frame', frame)#Muetra en pantalla el proceso de deteccion facial al usuario
        if count>=80: #Condicion para monitorear el numero de frames que se caoturan
            break#Si lo cumple rompe el ciclo

    cap.release()#Libera la memoria de la variable
    cv2.destroyAllWindows()#Cierra y borra las ventanas creadas con el programa
    return 0 #Retorna 0
    