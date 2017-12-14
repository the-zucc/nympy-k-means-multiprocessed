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
import time
from multiprocessing import Process, sharedctypes, Manager, Lock
import gc

#CONSTANTES ==============================================================================================================
nbThreads=4
largeurtest=3000
hauteurtest=200
nombrepointstest=45500
nombrecentroidestest=10

# REMOVE THIS .. MAYBE #
nbPointsParClusters = []

class Calculator1():
    def __init__(self,Params,Database):
        #Variables -------------------------------------------------------------------------------------
        self.Database = Database       
        self.nombreDeMotsAGarder = Params[3]        
        self.centroides=[]
        self.clusters=[]       
        #Initialiser la matrice -------------------------------------------------------------------------
        self.nbMots = 14836 #HARDCODED # REMOVE THIS #
        self.matrice = np.zeros( (self.nbMots,self.nbMots) )   
        self.Database.csvLecture(self.matrice,Params[1]) #Remplir matrice avec taille de fenetre  
        print(self.matrice)  
        print()
        self.nbPoints = len(self.matrice)
        print("NB de points : ", self.nbPoints)
                
        #Loader la stop-list ----------------------------------------------------------------------------
        #self.chargerStopList() # REMOVE THIS #
        
        #Initialiser les centroides par mots -------------------------------------------------------------
        if Params[0] == "mots":
            self.mode = 1            
            self.nbCentroides = len(Params[2])
            self.genererCentroidesParMots(Params[2])            
        #Initialiser les centroides aléatoirement --------------------------------------------------------
        else: 
            self.mode = 2
            self.nbCentroides = Params[2]
            self.genererCentroidesAleatoires(Params[2])   
        
        self.initClusters()
        
        startSeq = time.time()    
        #self.test()
        print(" ====== Sequence du Calculator faite en : ",time.time()-startSeq,"secondes.")
        
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
    
    def initClusters(self):        
        self.clusters = []
        for i in range(self.nbCentroides):
            self.clusters.append([])   
                 
    #GENERER DES CENTROIDES ALÉATOIRES =======================================================================================
    def genererCentroidesAleatoires(self,NombreCentroides):
        #Init les clusters
        self.initClusters()
        print("INIT CENTROIDES ALÉATOIRES")
        #Par Centroide a generer        
        for i in range(NombreCentroides):
            #Nombre aléatoire de points a inserer dans notre "faux" cluster
            nbIdx = (int)(random.randrange(5,(int)(self.nbPoints/NombreCentroides)))
            for c in range(nbIdx):
                #Ajouter point à idx aléatoire dans cluster i
                idx = (int)(random.randrange(0,self.nbPoints))
                self.clusters[i].append(idx)
            print("Cluster",i+1," a",len(self.clusters[i]),"points.")
           
        #Calculer barycentres pour initialiser les centroides aléatoires, puis debuter calculs avec ces centroides
        self.calculerBarycentres(True)    

    #GENERER DES CENTROIDES AUX MOTS VOULUS ==================================================================================
    def genererCentroidesParMots(self,ListeMots):
        for Mot in ListeMots:            
            #Recupere mot dans le dictionnaire ---------------------------------------------------------------
            index = self.Database.dictionnaire[Mot] 
            
            #Creer le centroide avec le mot dans la matrice --------------------------------------------------          
            self.centroides.append(self.matrice[index])            
    
    def leastSquare(self,a,b):
        return np.sum(np.square(a-b))    
    
    # REMOVE THIS #
    def calculerDistancesTMP(self):
        
        self.initClusters()
        i=0
        distances = []
        while i < self.nbCentroides:
            startTMP = time.time()
            distPoints =[]
            for p in self.matrice:
                distPoints.append(self.leastSquare(self.centroides[i], p))
            distances.append(distPoints)
            i += 1
        print("DISTANCES : ",len(distances))
        for d in range(len(distances[0])):
            print("POINT :",d)
            actual = []
            actual.append(distances[0][0:self.nbCentroides][0:self.nbCentroides])
            print("ACTUAL :",actual)
            closest = np.min(actual)
            print("CLOSEST :",closest)
            indexClosest = actual[0].index(closest) 
            print("INDEX :",indexClosest,"\n\n") 
            self.clusters[indexClosest].append(d) 
        
            #print("Calculer la distance entre centroide",i,"et ",self.nbPoints,"points took",time.time()-startTMP,"secondes.")
            
    def calculerDistances(self):
        startDist = time.time()
        nbPointsParClusters = []
        for c in self.clusters:
            nbPointsParClusters.append(len(c))
        print("Nombre de points des clusters precedents:",nbPointsParClusters)
            
        #Passer dans chaque points  
        self.initClusters()           
        i=0
        while i < self.nbPoints:
            distances = []
            p = self.matrice[i]
            for c in self.centroides:
                #Calcul distance et ajoute a la liste
                distances.append(self.leastSquare(p, c))    
           
            #Trouver le plus pret et son index
            closest = np.min(distances)
            indexClosest = distances.index(closest)            
          
            #L'assigner au bon cluster (index du centroide, liste des index des points dans la matrice)
            self.clusters[indexClosest].append(i)         
            i+=1 
        
        for i in range(len(self.clusters)):
            if nbPointsParClusters[i] != len(self.clusters[i]):
                return True
        return False
        # REMOVE THIS #print("Calculer les distances de",len(self.centroides),"centroides sur",self.nbPoints,"points prend",time.time()-startDist,"secondes.")
    
    def transfereCentroides(self,barycentres):
        self.centroides = []
        for c in barycentres:
            self.centroides.append(c)
        
    def calculerBarycentres(self,firstTime = False):#REMOVE THIS AFTER PLZ#
        #Passer dans chaque cluster
        barycentres = []
        for c in self.clusters:  
            CoordsActuelles = np.array([Vecteur for Vecteur in self.matrice[[idx for idx in c]]])   
            #Faire la moyenne des points             
            barycentres.append(np.mean(CoordsActuelles,axis=0))           
       
        #Si les nouveaux barycentres sont differents des ancients centroides (changements)
        if ( not np.array_equal(barycentres,self.centroides)) or firstTime:  
            if firstTime:
                print("Calcul barycentres pour centroides aleatoires\n\n")                 
            self.transfereCentroides(barycentres)           
            return True
        #Sinon, remplacer centroides par nouveaux barycentres
        else:       
            #self.centroides = barycentres
            return True

    def sequenceCalcul(self):
        #Calcul les distances
        if(self.calculerDistances()):
            print("----------- Changements")
            self.calculerBarycentres()
            return True
        else:
            print("----------- Stable")
            return False
            
#         # REMOVE THIS # self.calculerDistancesTMP()
#         #Calculer le barycentres, si nouveaux barycentres, poursuivre calcul
#         if(self.calculerBarycentres()):
#             print("----------- Changements")
#             return True
#         #Sinon, arreter sequence pcq calculs finis
#         else:
#             print("----------- Stable")
#             return False
            
    def test(self):
        debutCalculs = time.time()
        calculating = True   
        i = 0    
        while calculating: 
            i += 1
            debutIteration = time.time()      
            calculating = self.sequenceCalcul()
            print("Itération #"+str(i)+" effectuée en",time.time()-debutIteration,"secondes." )
            pos = 0
            while(pos < len(self.clusters)):
                print("Cluster #"+str(pos+1)+" a "+str(len(self.clusters[pos]))+" points.")
                pos += 1        
            print("\n\n")  
            
        print("======== DONE ! Le tout a ete fait en",time.time()-debutCalculs,"secondes.")
          
     
     


def initClusters(nombreCentroides):
    return [[] for i in range(0, nombreCentroides)]
    
def calculerDistances(sharedArrayPoints, nombrePoints, sharedArrayCentroides, nombreCentroides, dictClusters, indexDebut, indexFin, indexThread):
    matrPoints=np.frombuffer(sharedArrayPoints.get_obj()).reshape((nombrePoints, nombrePoints))
    matrCentr=np.frombuffer(sharedArrayCentroides.get_obj()).reshape((nombreCentroides, nombrePoints))
    #Passer dans chaque points
    clusters=initClusters(nombreCentroides)
    for i in range(nombreCentroides):
        clusters[i].append(i)
    i=0
    
    for i in range(indexDebut, indexFin):
        distances = []
        p = matrPoints[i]
        for c in matrCentr:
            #Calcul distance et ajoute a la liste
            dist=leastSquare(p, c)
            distances.append(dist)
            #print(dist)    
        #Trouver le plus pres et son index
        closest = np.min(distances)
        indexClosest = distances.index(closest)
        #L'assigner au bon cluster (index du centroide, liste des index des points dans la matrice)
        clusters[indexClosest].append(i)
        #print(i)
    for i in range(nombreCentroides):
        dictClusters[i]+=clusters[i]
        print("thread",indexThread,"cluster",i,":",len(clusters[i]),"points")
    print()
    print()
    #queuePointsClusters.put(clusters)
def leastSquare(a,b):
    #c=a-b
    #return np.sum(c)
    return np.sum(np.square(a-b))
class EnsembleThreads1():
    def __init__(self, calculator, nombreThreads):
        self.calculator = calculator
        self.nombreThreads=nombreThreads
        self.nombrePoints=self.calculator.nbMots
        self.nombreCentroides=len(self.calculator.centroides)
        #définition des objets partagés entre les threads
        self.sharedArrayPoints=sharedctypes.Array('d', self.nombrePoints*self.nombrePoints)#la matrice, convertie en une ligne
        #création du dictionnaire contenant les clusters
        self.manager=Manager()
        self.dictClusters=self.manager.dict()
        #initialisation des clusters 
        for i in range(self.nombreCentroides):
            self.dictClusters[i]=[]
        
        self.sharedArrayCentroides=sharedctypes.Array('d',self.nombreCentroides*self.nombrePoints)#la matrice de centroides, ceonvertie en une ligne
        
        #définition de la matrice de centroides
        self.matrCentroides=np.frombuffer(self.sharedArrayCentroides.get_obj()).reshape((self.nombreCentroides, self.nombrePoints))
        for i in range(self.nombreCentroides):
            self.matrCentroides[i]=self.calculator.centroides[i]
        
        #définition de la matrice des Points
        self.matrPoints=np.frombuffer(self.sharedArrayPoints.get_obj()).reshape((self.nombrePoints, self.nombrePoints))
        for i in range(self.nombrePoints):
            self.matrPoints[i]=self.calculator.matrice[i]
        self.nombreEntreesParThread=self.nombrePoints//self.nombreThreads
        self.indexes=[]
        #définition des indexes pour les threads
        for i in range(self.nombreThreads):
            idxD=i*self.nombreEntreesParThread
            if i == self.nombreThreads-1:
                idxF=self.nombrePoints-1
            else:
                idxF=((i+1)*self.nombreEntreesParThread)-1
            self.indexes.append((idxD, idxF))
    def calculer(self):
        threads=[]
        #ici, on initie chaque thread
        for i in range(self.nombreThreads):
            mythread=Process(target=calculerDistances, args=(self.sharedArrayPoints, self.nombrePoints, self.sharedArrayCentroides, self.nombreCentroides, self.dictClusters, self.indexes[i][0], self.indexes[i][1], i))
            mythread.start()
            threads.append(mythread)
        for mythread in threads:
            mythread.join()
            del mythread
        self.calculerBarycentres()
        
        #self.fetchDesQueuesEtCalculerCentroides()
    def calculerBarycentres(self):
        barycentres=[]
        for i in range(self.nombreCentroides):
            barycentre=np.mean(np.array([Vecteur for Vecteur in self.matrPoints[[idx for idx in self.dictClusters[i]]]]),axis=0)
            #Faire la moyenne des points             
            barycentres.append(barycentre)
        for i in range(self.nombreCentroides):
            self.matrCentroides[i]=barycentres[i]
        del self.dictClusters
        self.dictClusters=self.manager.dict()
        for i in range(self.nombreCentroides):
            self.dictClusters[i]=[]
            

if __name__ == '__main__':
    test1 = {}
    test1[1] = (420,23,23,23)
    test1[2] = (80,20)
    test1[3] = (166,)
    
    for i in test1.values():
        print(len(i))