#-*- coding: utf8 -*-
#========================================================================================================================
# Fichier : Main.py
# Projet  : B52_TP3
# Auteurs : Kevin Mwanangwa, Laurier Lavoie-Giasson, Chris David
#=========================================================================================================================

#IMPORTS =================================================================================================================

import random
import numpy as np
import time
from multiprocessing import Process, sharedctypes, Queue

#VARIABLES GLOBALES ET METHODES STATIQUES =================================================================
maxLength = 80   #Don't judge me, I have OCD - Kevin 
def OCD(char,phrase): #Don't judge me, I have OCD - Kevin 
    current = " "+phrase+" "
    maxMargin = (maxLength-len(current))
    leftMargin = (int) (maxMargin/2)    
    rightMargin = maxMargin - leftMargin    
    return (char*leftMargin)+current+(char*rightMargin) 

def secondsToString(secondes): #Don't judge me, I have OCD - Kevin 
    #Calculer minutes avec secondes
    m, s = divmod(secondes, 60)
    #Calculer heures avec minutes
    h, m = divmod(m, 60)
    duration = ""
    if h != 0:
        duration += str(int(h))+" HEURES: "
    if m != 0:
        duration += str(int(m))+" MINUTES: "
    duration += str(round(s,2))+" SECONDES"
    return duration
 
def leastSquare(a,b):        
    return np.sum(np.square(a-b))    

class Calculator1():
    def __init__(self,Params,Database):
        random.seed(time.time())
        #Variables -------------------------------------------------------------------------------------
        self.Database = Database       
        self.nombreDeMotsAGarder = Params[3]        
        self.centroides=[]
        self.clusters=[]       
        #Initialiser la matrice -------------------------------------------------------------------------
        self.nbPoints = 14836 #HARDCODED # REMOVE THIS #
        self.matrice = np.zeros( (self.nbPoints,self.nbPoints) )   
        self.Database.csvLecture(self.matrice,Params[1]) #Remplir matrice avec taille de fenetre     
        print(self.matrice[2])     
        print("\n\n"+OCD("*","CLUSTERING SUR "+str(self.nbPoints)+" MOTS")+"\n") #Don't judge me, I have OCD - Kevin  
      
        #Loader la stop-list ----------------------------------------------------------------------------
        self.stoplist = []
        #self.chargerStopList() # REMOVE THIS #
        
        #Initialiser les centroides par mots -------------------------------------------------------------
        if Params[0] == "mots":
            self.mode = 1            
            self.nbCentroides = len(Params[2])
            self.creerFichier()
            self.genererCentroidesParMots(Params[2])            
        #Initialiser les centroides aléatoirement --------------------------------------------------------
        else: 
            self.mode = 2
            self.nbCentroides = Params[2]
            self.creerFichier()
            self.genererCentroidesAleatoires(Params[2]) 
            
        #Debuter clustering -----------------------------------------------------------------------------
        self.clustering()
            
    def creerFichier(self): 
        #Ouvrir Document et ecrire la date ---------------------------------------------------------------
        startDate = time.ctime(time.time())
        startDate = startDate.replace(':','.')          
        self.filename = "Resultats/["+startDate+"]_["+str(5)+"-Fenetre]_["+str(self.nbCentroides)+"-Centroides]_["+str(self.nombreDeMotsAGarder)+"-Mots].txt"
       
        self.fichier = open(self.filename,"w",encoding="utf-8")
        self.fichier.write(OCD("*","DEBUT : "+startDate)+"\n\n")
       
    def chargerStopList(self):
        #Ouvrir liste ------------------------------------------------------------------------------------
        fichier = "TP3_KevLauChr_StopList.txt"
        stream = open(fichier,"r", encoding="utf-8")
       
        #Split les mots et fermer stream -----------------------------------------------------------------
        liste = stream.read().replace('\ufeff','').split() 
        stream.close()
         
        #Verifier chaque mots du dictionnaire ------------------------------------------------------------
        for (mot,idx) in self.Database.dictionnaire.items():
            #Si mot actuel est dans la stop-liste
            if mot in liste:
                #Ajouter index du mot a la liste d'indexes (idx -1 puisque les indexes dans la BD commencent a 1)
                self.stoplist.append(idx)                                  
    
    def resetClusters(self):   
        #Vider les clusters     
        self.clusters = []
        #Ajouter une liste par centroides voulus
        for i in range(self.nbCentroides):
            self.clusters.append([])   
                 
    #GENERER DES CENTROIDES ALÉATOIRES =======================================================================================
    def genererCentroidesAleatoires(self,NombreCentroides):  
        tmp = OCD("*","INITIATION DE "+str(self.nbCentroides)+" CENTROÏDES ALÉATOIRES")
        self.fichier.write(tmp+"\n")
        print(tmp) #Don't judge me, I have OCD - Kevin  
        
        #Reset les Clusters
        self.resetClusters()      
        
        #Assigner un cluster aleatoire pour chaque point, 1 chance sur 5, devraient donc etre repartis assez equitablement  
        for point in range(self.nbPoints):
            index = random.randrange(0,NombreCentroides)
            self.clusters[index].append(point)
                    
        #Calculer barycentres pour initialiser les centroides aléatoires, puis debuter calculs avec ces centroides
        self.calculerBarycentres()  
        #Vider nos faux clusters
        self.resetClusters()  

    #GENERER DES CENTROIDES AUX MOTS VOULUS ==================================================================================
    def genererCentroidesParMots(self,ListeMots):
        for Mot in ListeMots:            
            #Recupere mot dans le dictionnaire ---------------------------------------------------------------
            index = self.Database.dictionnaire[Mot]             
            #Creer le centroide avec le mot dans la matrice --------------------------------------------------          
            self.centroides.append(self.matrice[index])            
     
    def findClosest(self,index):
        #Distances du points i avec tous les centroîdes
            distances = []           
            for centroide in self.centroides:
                #Calcul distance et ajoute a la liste
                distances.append(leastSquare(self.matrice[index],centroide)) 
            #Trouver le plus pret et son index
            closest = np.min(distances)            
            indexClosest = distances.index(closest)   
       
            return indexClosest      
               
    #CALCULER LA DISTANCE ENTRE LES POINTS ET LES CENTROIDES ===================================================================
    def calculerDistances(self):    
        #Garder le nombre de points des clusters précédents   
        nbPointsParClusters = []
        for c in self.clusters:
            nbPointsParClusters.append(len(c))      
            
        #Reset les clusters  
        self.resetClusters()           
        db = time.time()
        #Passer dans chacun des points
        for index in range(self.nbPoints):
            #Trouve le centroide le plus pret de i et assigner i au bon cluster 
            plusProche = self.findClosest(index)
            self.clusters[plusProche].append(index)
     
        #Compter nombre de changements
        nbChangements = 0      
        for i in range(len(self.clusters)):
            nbChangements += np.absolute(nbPointsParClusters[i] - len(self.clusters[i])) 
        
        #Inscrire informations dans le fichier txt    
        tmp = "\n"+OCD("=",str(nbChangements)+" CHANGEMENTS")+"\n"
        self.fichier.write(tmp+"\n")
        print(tmp) #Don't judge me, I have OCD - Kevin 
        
        #Continuer le calcul ou stop le clustering
        if nbChangements != 0:        
            return True
        else:            
            return False
      
    def calculerBarycentres(self):
        #Reset les centroides
        self.centroides = []
        #Passer par tout les clusters
        for c in self.clusters:  
            #Regrouper tous les points du cluster actuel
            CoordsActuelles = np.array([Vecteur for Vecteur in self.matrice[[idx for idx in c]]])   
            #Faire la moyenne des points et assigner nouveaux centroides            
            self.centroides.append(np.mean(CoordsActuelles,axis=0))           
     
    def sequenceCalcul(self):
        #Si il y a des changements, calculer barycentres
        if(self.calculerDistances()):       
            self.calculerBarycentres()
            return True
        #Sinon, arreter le calcul
        else:          
            return False
       
    def getTopResults(self,cluster,index): 
        distances = []      
        for mot in cluster:
            if mot not in self.stoplist:
                distances.append(leastSquare(self.centroides[index], self.matrice[mot]))
                
        topIndexes = np.argsort(distances)[::1][:self.nombreDeMotsAGarder] #Retourne lesindexes des N distances les plus petites
        topMots = []
        topScores = []
        for index in topIndexes:
            topMots.append(cluster[index])
            topScores.append(distances[index])
        return(topMots,topScores) #Retourne les N top indexes et les N top distances
    
    #MAY BE COMPLETELY USELESS
    def autosave(self):
        #Ferme/save le fichier
        self.fichier.close()
        #Re-ouvre le fichier en mode append
        self.fichier = open(self.filename,"a",encoding="utf-8")
                 
    def clustering(self):
        #filename = "TP3_Results_"+str(self.Database.fenetre)+"-Fenetre_"+str(self.nbCentroides)+"-Centroides_"+str(self.nombreDeMotsAGarder)+"-Mots_"+time.ctime(time.time())
        debutCalculs = time.time()
        i = 0 
        calculating = True  
        #TANT QUE LE PROGRAMME CALCULE ====================================================================================        
        while calculating:          
            i += 1
            debutIteration = time.time()      
            calculating = self.sequenceCalcul()  
            pos = 0
              
            if calculating:                
                while(pos < len(self.clusters)):
                    tmp = '{:18}'.format(" Le cluster "+str(pos+1))+": contient "+str(len(self.clusters[pos]))+" mots."
                    self.fichier.write(tmp+"\n")
                    print(tmp) #Don't judge me, I have OCD - Kevin 
                    pos += 1
                tmp = "\n"+OCD("=","ITÉRATION #"+str(i)+" : ["+secondsToString(time.time()-debutIteration)+"]")+"\n"
                self.fichier.write(tmp+"\n")
                print(tmp)    #Don't judge me, I have OCD - Kevin 
            
            #Autosave apres chaque 10 iterations    
            if i%10 == 0 and i != 0:
                self.autosave()     
              
        tmp =  OCD("*","CLUSTERING : ["+secondsToString(time.time()-debutCalculs)+"]")+"\n\n\n\n\n"
        self.fichier.write(tmp+"\n")     
        print(tmp)
   
        #AFFICHER LES RESULTATS DU GROUPING ==============================================================================
        tmp = OCD("*","GROUPING DE "+str(self.nombreDeMotsAGarder)+" MOTS SUR "+str(self.nbCentroides)+" CLUSTERS")
        self.fichier.write(tmp+"\n")
        print(tmp)
        
        debutGrouping = time.time()
        maxLength = 40
        for c in range(self.nbCentroides):   
            tmp =  "\n"+OCD("=","GROUPE #"+str(c+1))+"\n"                                                       #Don't judge me, I have OCD - Kevin
            self.fichier.write(tmp+"\n")
            print(tmp)   
            results = self.getTopResults(self.clusters[c], c)
            for r in range(len(results[0])):
                tmp = '{:25}'.format('{:5}'.format(str(r+1)+") ")+str(results[0][r]))+" : "+str(results[1][r])  #Don't judge me, I have OCD - Kevin
                self.fichier.write(tmp+"\n")
                print(tmp) #Don't judge me, I have OCD - Kevin                 
#                 for (mot,idx) in self.Database.dictionnaire:
#                     if idx == results[0][r]:
#                         print('{:24}'.format(" "+mot+str(pos+1))+str(results[1][r]))                          #Don't judge me, I have OCD - Kevin  
        tmp = "\n\n"+OCD("*","GROUPING : ["+secondsToString(time.time()-debutGrouping)+"]")+"\n\n"              #Don't judge me, I have OCD - Kevin  
        self.fichier.write(tmp+"\n")
        self.fichier.close()
        print(tmp) 
        
"""
    MULTITHREADING ==============================================================================================================================
"""                       
def initClusters(nombreCentroides):
    return [[] for i in range(0, nombreCentroides)]

def calculerDistances(sharedArrayPoints, nombrePoints, sharedArrayCentroides, nombreCentroides, queuePointsClusters, indexDebut, indexFin, indexThread):
    matrice=np.frombuffer(sharedArrayPoints.get_obj()).reshape((nombrePoints, nombrePoints))
    centroides=np.frombuffer(sharedArrayCentroides.get_obj()).reshape((nombreCentroides, nombrePoints))
    #Passer dans chaque points
    clusters=initClusters(nombreCentroides)
    for i in range(len(clusters)):
        clusters[i].append(i)
    i=0
    
    for i in range(indexDebut, indexFin):
        distances = []
        p = matrice[i]
        for c in centroides:
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
    for i in range(len(clusters)):
        print("thread",indexThread,"cluster",i,":",len(clusters[i]),"points")
    print()
    print()

class EnsembleThreads1():
    def __init__(self, calculator, nombreThreads):
        self.calculator = calculator
        self.nombreThreads=nombreThreads
        self.nombrePoints=self.calculator.nbMots
        self.nombreCentroides=len(self.calculator.centroides)
        #définition des objets partagés entre les threads
        self.sharedArrayPoints=sharedctypes.Array('d', self.nombrePoints*self.nombrePoints)#la matrice, convertie en une ligne
        self.queuePointsClusters=Queue()#la queue qui devrait servir à passer des objets entre les threads 
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
            mythread=Process(target=calculerDistances, args=(self.sharedArrayPoints, self.nombrePoints, self.sharedArrayCentroides, self.nombreCentroides, self.queuePointsClusters, self.indexes[i][0], self.indexes[i][1], i))
            mythread.start()
            threads.append(mythread)
        for mythread in threads:
            mythread.join()
            mythread.terminate()
        #self.fetchDesQueuesEtCalculerCentroides()
    def fetchDesQueuesEtCalculerCentroides(self):
        while not self.queuePointsClusters.empty():
            tab=self.queuePointsClusters.get()
            print(tab)
            idxCluster=tab[0]
            for i in range(1,len(tab)):
                #self.calculator.clusters[idxCluster].append(tab[i])
                print(tab[i])

if __name__ == '__main__':
    iter = 5
    boucles = 5
    data = np.random.uniform(low=0, high=40, size=(14836,14836))
    centroids = np.random.uniform(low=0, high=40, size=(5,14836))
    
    #print("Data:",data)
    #print("centroids:",centroids)


    list1 = []
    for x in range (boucles):
        distances = []
        debut = time.time()
        for point in data:
            for c in centroids:
                distances.append(leastSquare(point, c))
        closest = np.min(distances)
        indexClosest = distances.index(closest) 
          
        fin = time.time()-debut  
        print("Iter",x,"took",fin)
        list1.append(fin)  
    print("Resultat obtenu: Closest =",closest)
    print("========== Moyenne least Square numpy  :",np.mean(list1),"\n\n")  
    
        
             
    