#-*- coding: utf8 -*-
#========================================================================================================================
# Fichier : Main.py
# Projet  : B52_TP3
# Auteurs : Kevin Mwanangwa, Laurier Lavoie-Giasson, Chris David
#=========================================================================================================================

#IMPORTS =================================================================================================================
from multiprocessing import Process
from Points import *
import random
import numpy as np
import threading
from test.regrtest import multiprocessing

#CONSTANTES ==============================================================================================================
nbThreads=4
largeurtest=3000
hauteurtest=200
nombrepointstest=25000
nombrecentroidestest=10

#CLASSE Calculator =======================================================================================================
class Calculator():
    def __init__(self,Params,Database):
        #Variables -------------------------------------------------------------------------------------
        self.Database = Database       
        self.nombreDeMotsAGarder = Params[3]
        self.points=[]
        self.centroides=[]
        self.clusters={}
        
        #Initialiser la matrice -------------------------------------------------------------------------
        self.nbMots = len(Database.dictionnaire)
        self.matrice = np.zeros( (self.nbMots,self.nbMots) )   
        self.Database.csvLecture(self.matrice,Params[1]) #Remplir matrice avec taille de fenetre  
        print(self.matrice)   
        
        #Loader la stop-list ----------------------------------------------------------------------------
        self.chargerStopList()
        
        #Initialiser les centroides par mots -------------------------------------------------------------
        if Params[0] == "mots":
            self.mode = 1            
            self.genererCentroidesParMots(Params[2])
        #Initialiser les centroides aléatoirement --------------------------------------------------------
        else: 
            self.mode = 2
            self.genererCentroidesAleatoires(Params[2])   
    
    #REMPLIR LA STOP-LIST ====================================================================================================
    def chargerStopList(self):
        #Ouvrir liste ------------------------------------------------------------------------------------
        fichier = "TP3_KevLauChr_StopList.txt"
        stream = open(fichier,"r", encoding="utf-8")
       
        #Split les mots et fermer stream -----------------------------------------------------------------
        liste = stream.read().replace('\ufeff','').split() 
        stream.close()
                
        self.stoplist = []       
        #Verifier chaque mots du dictionnaire ------------------------------------------------------------
        for (mot,idx) in self.Database.dictionnaire.items():
            #Si mot actuel est dans la stop-liste
            if mot in liste:
                #Ajouter index du mot a la liste d'indexes (idx -1 puisque les indexes dans la BD commencent a 1)
                self.stoplist.append(idx)                                  
     
    #GENERER DES CENTROIDES ALÉATOIRES =======================================================================================
    def genererCentroidesAleatoires(self,NombreCentroides):
        pass

    #GENERER DES CENTROIDES AUX MOTS VOULUS ==================================================================================
    def genererCentroidesParMots(self,ListeMots):
        for Mot in ListeMots:            
            #Recupere mot dans le dictionnaire ---------------------------------------------------------------
            index = self.Database.dictionnaire[Mot] 
            
            #Creer le centroide avec le mot dans la matrice --------------------------------------------------
            CentroTmp = Centroide(self.matrice[index])
            self.centroides.append(CentroTmp)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    def genererPosition(self):
        position=np.zeros(8)
        for i in range(len(position)):
            position[i]=random.randrange(largeurtest)
        return position
    
    def attribuerLesClusters(self,points, indexEntreeDepart, indexEntreeFin):
        for i in range(indexEntreeDepart, indexEntreeFin):
            distance=self.attribuerCluster(points[i])
            #print ("cluster choisi:",point.cluster.centroide.id," distance:",distance)
    
    def attribuerCluster(self, point):#la fonction attribue à chaque point le cluster/centroide qui lui convient.
        centroideProche=None
        distanceCentroideProche=None
        for centroide in self.centroides:
            if(centroideProche is None):
                centroideProche=centroide
                distanceCentroideProche=self.calculerDistance(point.vectPosition, centroide.vectPosition)
                #print("distance centroide 1:",distanceCentroideProche)
            else:
                distanceCentroide=self.calculerDistance(point.vectPosition, centroide.vectPosition)
                if(distanceCentroide < distanceCentroideProche):
                    centroideProche=centroide
                    distanceCentroideProche=distanceCentroide
                #print("distance centroide",centroide.id,":",distanceCentroide)
        nouveauCluster = self.clusters[centroideProche.id]
        if point.cluster is None:
            point.cluster=nouveauCluster
            nouveauCluster.points.append(point)
        else:
            ancienCluster=point.cluster
            if ancienCluster != nouveauCluster:
                #enlever le point de son ancien cluster
                ancienCluster.points.remove(point)
                #ajouter le point dans son nouveau cluster
                nouveauCluster.points.append(point)
                point.cluster=nouveauCluster
        return distanceCentroideProche
    
    def calculerDistance(self, vect1, vect2):
        return np.sum(np.square(vect1-vect2))
    
    def calculerPositionCentroide(self, cluster):
        vecteurs=np.array([point.vectPosition for point in cluster.points])
        cluster.centroide.changerPosition(np.mean(vecteurs,axis=0))
        
    def calculerPositionsCentroides(self, clusters):
        for cluster in clusters:
            self.calculerPositionCentroide(cluster)
            print(cluster.centroide.vectPosition)
    
    def sequenceCalcul(self, points, clusters):
        self.attribuerLesClusters(points, 0, len(self.points)-1)
        self.calculerPositionsCentroides(clusters.values())
        

class CalculatorThread(multiprocessing.Process):
    def __init__(self, calculator,indexThread, nombreTotalThreads):
        multiprocessing.Process.__init__(self,name=("threadCalculatrice-"+str(indexThread)))
        print(self.name)
        self.indexThread=indexThread
        self.calculator=calculator
        nombreEntrees=len(calculator.points)
        nombreEntreesParThread=nombreEntrees//nombreTotalThreads
        self.indexDebut=self.indexThread*nombreEntreesParThread
        self.indexFin=((self.indexThread+1)*nombreEntreesParThread)-1
    def run(self):
        print("indexDebut:",self.indexDebut,"indexFin:",self.indexFin)
        #for i in range(self.indexDebut, self.indexFin):
            #print(self.name,":",self.calculator.points[i].vectPosition)
        self.calculator.attribuerLesClusters(self.calculator.points, self.indexDebut, self.indexFin)

#la classe wrapper pour les différents threads
class EnsembleThreads():
    def __init__(self, calculator, nombreThreads):
        self.calculator=calculator
        self.threads=[]
        for j in range(nombreThreads):
            self.threads.append(CalculatorThread(calculator, j, nbThreads))
    def initierThreadsEtCalculerUneFois(self):
        for mythread in self.threads:
            mythread.start()
        for mythread in self.threads:
            mythread.join()
    def calculer(self):
        for mythread in self.threads:
            mythread.run()
        for mythread in self.threads:
            mythread.join()
            
if __name__ == '__main__':
    calculator=Calculator()
    i=0
    #threads=EnsembleThreads(calculator, nbThreads)
    #threads.initierThreadsEtCalculerUneFois()
    #calculator.calculerPositionsCentroides(calculator.clusters.values())
    while True:
        #threads.calculer()
        i+=1
        calculator.sequenceCalcul(calculator.points, calculator.clusters)
        print("calculé",i)