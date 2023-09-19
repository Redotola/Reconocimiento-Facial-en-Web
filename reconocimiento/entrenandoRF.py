#mandamos a importar las siguientes librerias
import cv2
import os
import numpy as np

#creación de la función entrenar, recibiendo el nombre como parametro
def entrenar(name):
    #ruta que almacenara la lista de las personas
    dataPath='C:/Users/AXL/Downloads/ESTANCIA V 1.7.10/reconocimiento/Data'
    peopleList=os.listdir(dataPath)#creamos una variable para poder almacenar toda la lista de las personas que se encontraran en la ruta
    print ("Lista de personas: ", peopleList)
#realiza las siguientes listas
    labels=[]
    faceData=[]
    label=0
#se realiza la busqueda de todas las personas, leyendo directorio por directorio hasta encontrar la imagen para realizar el entrenamiento
#leyendolo desde la ruta Data
    for nameDir in peopleList:
        personPath=dataPath+'/'+nameDir
        print("Leyendo imagenes")
#recorrido en los directorios para encontrar la lista en la ruta de Data   
        for fileName in os.listdir(personPath):
            print("Rostros: ", nameDir+'/'+fileName)
            labels.append(label)
            faceData.append(cv2.imread(personPath+'/'+fileName,0))
            image=cv2.imread(personPath+'/'+fileName,0)
            cv2.imshow('image', image)
            cv2.waitKey(10)
        label+=1
#se manda la variable face recongnizer para poder reconocer las fotos
    face_recognizer=cv2.face.EigenFaceRecognizer_create()
#mensaje de entrenamiento
    print("Entrenando")
    face_recognizer.train(faceData,np.array(labels))
    path='modelo'+name+'.xml'
    face_recognizer.write(path)