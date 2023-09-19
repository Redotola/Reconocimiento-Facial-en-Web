import cv2
import os

def facial(name):#Obtiene el nombre como parametro de busqueda
    dataPath='C:/Users/AXL/Downloads/ESTANCIA V 1.7.10/reconocimiento/Data'#Carpeta de proyecto que contiene los datos
    imagePath=(os.listdir(dataPath))
    print("imagePath=", imagePath)

    face_recognizer=cv2.face.EigenFaceRecognizer_create()#Funcion para deteccion de rostros y comparador


    face_recognizer.read('modelo'+name+'.xml')#Funcion que lee el modelo creado mediante el formato para el 
    #reconocimiento de rostros

    cap=cv2.VideoCapture(0,cv2.CAP_DSHOW)#Captura de video en tiempo real
    faceclas=cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
    #Utilizamos el mismo formato de deteccion con haarcascade para deteccion de rostros frontales
    count=0#Inicializamos nuestro contador
    while True:
        red, frame=cap.read()
        if red==False: break
        gray=cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)#Convertirmos los frames en escala de grises
        auxFrame=gray.copy()

        faces=faceclas.detectMultiScale(gray, 1.3,5)

        for (x,y,w,h) in faces:
            rostro=auxFrame[y:y+h, x:x+w]
            rostro=cv2.resize(rostro,(150,150), interpolation=cv2.INTER_CUBIC)
            result=face_recognizer.predict(rostro)#Predicciona el rostro conforme el modelos y comparando
            #con las imagenes tomadas en tiempo real
            cv2.putText(frame, '{}'.format(result),(x,y-5), 1, 1.3, (255,255,0), 1, cv2.LINE_AA)
            '''Crea un frame con un figura de seguimiento de rostro con los datos de reconocimiento y nombre del resultado'''
            if result[1]<4000:#Cantidad de discrepancia con el modelo esto ayuda a predecir la similitud
                cv2.putText(frame, '{}'.format(imagePath[result[0]]),(x,y-25), 2, 1.1, (0,255,0), 1, cv2.LINE_AA)
                #en caso de cumplir con la coincidencia se muestra en pantalla el resultado y nombre de la persona
                cv2.rectangle(frame, (x,y),(x+w, y+h), (0,255,0),2)
                count+=1
            else:# en caso de no cumplir se enviara como resultado 'Desconocido'
                cv2.putText(frame,'Desconocido',(x,y-20), 2, 0.8, (0,0,255), 1, cv2.LINE_AA)
                cv2.rectangle(frame, (x,y),(x+w, y+h), (0,255,0),2)
        cv2.imshow('frame', frame)#Se muestra en pantalla los resultados y figura de seguimiento
        k=cv2.waitKey(1)#Espera en tiempo segundos
        if k==27 or count==40:#Si contador arroja 40 similitudes rompe el ciclo
            break
    cap.release()#Libera la memoria de la variable
    cv2.destroyAllWindows()#Destruye todas las ventanas
    