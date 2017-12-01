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
nombrepointstest=45500
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
        
        #TEMPORAIRE ############################# 
        for vecteur in self.matrice:
            ptTmp = Point(vecteur,0)
            self.points.append(ptTmp)
        #########################################   
            
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
            
        self.test()
    
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
            self.clusters[CentroTmp.id] = Cluster(CentroTmp)
            
            
            
            
            
            
    def test(self):
        i=0
        #threads=EnsembleThreads(calculator, nbThreads)
        #threads.initierThreadsEtCalculerUneFois()
        #calculator.calculerPositionsCentroides(calculator.clusters.values())
        while True:
            #threads.calculer()
            i+=1
            self.sequenceCalcul(self.points, self.clusters.values())
            print("calculé",i)        
                
            
            
            
            
            
            
            
            
            
            
            
            
    
    
    def genererPosition(self):
        position=np.zeros(8)
        for i in range(len(position)):
            position[i]=random.randrange(largeurtest)
        return position
    
    #la fonction attribue les clusters aux points passés en paramètre, de indexDepart à indexFin inclusivement
    def attribuerLesClusters(self,points, indexEntreeDepart, indexEntreeFin):
        for i in range(indexEntreeDepart, indexEntreeFin):
            distance=self.attribuerCluster(points[i])
            #print ("cluster choisi:",point.cluster.centroide.id," distance:",distance)
    
    def attribuerCluster(self, point, multithread=False):#la fonction attribue à chaque point le cluster/centroide qui lui convient.
        #le centroide le plus proche pour l'instant est inconnu ainsi que sa distance
        centroideProche=None
        distanceCentroideProche=None
        
        #pour chaque centroide
        for centroide in self.centroides:
            #si c'est la première itération
            if(centroideProche is None):
                #sauvegarde le centroide et sa distance
                centroideProche=centroide
                distanceCentroideProche=self.calculerDistance(point.vectPosition, centroide.vectPosition)
                #print("distance centroide 1:",distanceCentroideProche)
            #si ce n'est pas la première itération
            else:
                #calcul de la distance relative avec le centroide courant
                distanceCentroide=self.calculerDistance(point.vectPosition, centroide.vectPosition)
                #si la distance est plus petite que celle déjà sauvegardée
                if(distanceCentroide < distanceCentroideProche):
                    #on sauvegarde ce centroide et sa distance en tant que centroide le plus proche
                    centroideProche=centroide
                    distanceCentroideProche=distanceCentroide
                #print("distance centroide",centroide.id,":",distanceCentroide)
        # référence au nouveau cluster à associer au point, avec le id du centroide le plus proche.
        nouveauCluster = self.clusters[centroideProche.id]
        
        #si le cluster actuel du point n'est pas encore défini
        if point.cluster is None:
            #ajouter la référence à son cluster actuel au point
            point.cluster=nouveauCluster
            #ajouter au cluster la référence vers point
            nouveauCluster.points.append(point)
        else:
            #le cluster auquel renvoie la référence dans l'objet point 
            ancienCluster=point.cluster
            
            #si l'ancien cluster du point n'est pas le même que son nouveau
            if ancienCluster != nouveauCluster:
                #enlever le point de son ancien cluster
                #ancienCluster.points.remove(point)
                #ajouter le point dans son nouveau cluster
                #nouveauCluster.points.append(point)
                #ajouter la référence à son cluster au point
                point.cluster=nouveauCluster
        #return
    
    #calcule la distance relative entre deux points dans un espace à n dimensions
    def calculerDistance(self, vect1, vect2):
        return np.sum(np.square(vect1-vect2))
    
    #calcule la le barycentre d'un cluster
    def calculerPositionCentroide(self, cluster):
        vecteurs=np.array([point.vectPosition for point in cluster.points])
        cluster.centroide.changerPosition(np.mean(vecteurs,axis=0))
    
    #calcule les position des centroides de tous les clusters passés en paramètre
    def calculerPositionsCentroides(self, clusters):
        for cluster in clusters:
            self.calculerPositionCentroide(cluster)
            print(cluster.centroide.vectPosition)
    
    #la séquence de calcul attribue les clusters aux points, 
    def sequenceCalcul(self, points, clusters):
        self.attribuerLesClusters(points, 0, len(self.points)-1)
        self.creerClustersAPartirDesPoints(points, clusters)
        self.calculerPositionsCentroides(clusters)
    
    def creerClustersAPartirDesPoints(self, listepoints, listeclusters):
        for cluster in listeclusters:
            cluster.points=[]
        for point in listepoints:
            if point.cluster is not None:
                point.cluster.points.append(point)
        
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
        self.calculator.creerClustersAPartirDesPoints(self.calculator.points, self.calculator.clusters.values())
        self.calculator.calculerPositionsCentroides(self.calculator.clusters.values())

if __name__ == '__main__':
    calculator=Calculator()
    i=0
    #threads=EnsembleThreads(calculator, nbThreads)
    #threads.initierThreadsEtCalculerUneFois()
    #calculator.calculerPositionsCentroides(calculator.clusters.values())
    while True:
        #threads.calculer()
        i+=1
        calculator.sequenceCalcul(calculator.points, calculator.clusters.values())
        print("calculé",i)