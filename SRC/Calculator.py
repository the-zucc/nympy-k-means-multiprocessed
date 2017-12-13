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
from test.regrtest import multiprocessing

#CONSTANTES ==============================================================================================================
nbThreads=4
largeurtest=3000
hauteurtest=200
nombrepointstest=45500
nombrecentroidestest=10

class Calculator1():
    def __init__(self,Params,Database):
        #Variables -------------------------------------------------------------------------------------
        self.Database = Database       
        self.nombreDeMotsAGarder = Params[3]        
        self.centroides=[]
        self.clusters=[]
        
        #Initialiser la matrice -------------------------------------------------------------------------
        self.nbMots = len(Database.dictionnaire)
        self.matrice = np.zeros( (self.nbMots,self.nbMots) )   
        self.Database.csvLecture(self.matrice,Params[1]) #Remplir matrice avec taille de fenetre  
        print(self.matrice)  
        print()
        self.nbPoints = len(self.matrice)
        print("NB de points : ", self.nbPoints)
                
        #Loader la stop-list ----------------------------------------------------------------------------
        self.chargerStopList()
        
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
        self.test()
        print(" ====== Sequence du Calculator -copie (1) faite en : ",time.time()-startSeq,"secondes.")
        
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
        self.calculerBarycentres()    

    #GENERER DES CENTROIDES AUX MOTS VOULUS ==================================================================================
    def genererCentroidesParMots(self,ListeMots):
        for Mot in ListeMots:            
            #Recupere mot dans le dictionnaire ---------------------------------------------------------------
            index = self.Database.dictionnaire[Mot] 
            
            #Creer le centroide avec le mot dans la matrice --------------------------------------------------          
            self.centroides.append(self.matrice[index])            
    
    def leastSquare(self,a,b):
        return np.sum(np.square(a-b))    
            
    def calculerDistances(self):
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
    
    def calculerBarycentres(self):
        #Passer dans chaque cluster
        barycentres = []
        for c in self.clusters:  
            CoordsActuelles = np.array([Vecteur for Vecteur in self.matrice[[idx for idx in c]]])       
            
            #Faire la moyenne des points             
            barycentres.append(np.mean(CoordsActuelles,axis=0))           
       
        #Si les nouveaux barycentres sont egaux aux ancients centroide (Donc rien ne bouge)
        if [centroide.all() for centroide in self.centroides] == [barycentre.all() for barycentre in barycentres]:
            print("Change")
            print(barycentres[0][0:3], self.centroides[0][0:3])
            self.centroides = barycentres
            print(barycentres[0][0:3], self.centroides[0][0:3])
            return False
        #Sinon, remplacer centroides par nouveaux barycentres
        else:
            print("Pouet")
            #self.centroides = barycentres
            return True

    def sequenceCalcul(self):
        #Calcul les distances
        self.calculerDistances()
        #Calculer le barycentres, si nouveaux barycentres, poursuivre calcul
        if(self.calculerBarycentres()):
            return True
        #Sinon, arreter sequence pcq calculs finis
        else:
            return False
            
    def test(self):
        i=0        
        while i<20: 
            debutIteration = time.time()           
            i+=1
            self.sequenceCalcul()
            print("Itération #"+str(i)+" effectuée en",time.time()-debutIteration,"secondes." )
            pos = 0
            while(pos < len(self.clusters)):
                print("Cluster #"+str(pos+1)+" a "+str(len(self.clusters[pos]))+" points.")
                pos += 1        
            print("\n\n")    
     
     
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
            
        startSeq = time.time()    
        self.test()
        print(" ====== Sequence du Calculator faite en : ",time.time()-startSeq,"secondes.")
    
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
                     
    def hasntStopped(self):
        for c in self.centroides:
            x = 0
            if c.hasChanged:
                return True
        
        return False
            
    def test(self):
        i=0        
        while i<20: 
            debutIteration = time.time()           
            i+=1
            self.sequenceCalcul(self.points, self.clusters.values())
            print("Itération #"+str(i)+" effectuée en",time.time()-debutIteration,"secondes." )
            pos = 0
            for cluster in self.clusters.values():            
                print("Cluster #"+str(pos+1)+" a "+str(len(cluster.points))+" points.")
                pos+= 1        
            print("\n\n")
                
     
    
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
        x = 0
        for cluster in clusters:
            self.calculerPositionCentroide(cluster)           
            x += len(cluster.points)
                 
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
   test1 = {}
   test1[1] = (420,23,23,23)
   test1[2] = (80,20)
   test1[3] = (166,)
   
   for i in test1.values():
       print(len(i))