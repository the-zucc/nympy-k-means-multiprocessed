#-*- coding: utf8 -*-
#===============================================================================================
# Fichier : Main.py
# Projet  : B52_TP3
# Auteurs : Kevin Mwanangwa, Laurier Lavoie-Giasson, Chris David
#===============================================================================================

from multiprocessing import Process
from Points import *
import random
import numpy as np
import threading
from test.regrtest import multiprocessing

nbThreads=4
largeurtest=3000
hauteurtest=200
nombrepointstest=455000
nombrecentroidestest=80

class Calculator():
    def __init__(self):
        self.points=[]
        self.centroides=[]
        self.clusters={}
        #self.pointsAEnlever=[]
        
        for i in range(nombrepointstest):
            position=self.genererPosition()
            self.points.append(Point(position, 1))
            
        for i in range(nombrecentroidestest):
            position=self.genererPosition()
            centroide=Centroide(position)
            self.centroides.append(centroide)
            #print(centroide.id)
            self.clusters[centroide.id]=Cluster(centroide)
    
    def genererPosition(self):
        position=np.zeros(8)
        for i in range(len(position)):
            position[i]=random.randrange(largeurtest)
        return position
    
    def attribuerLesClusters(self,points, indexEntreeDepart, indexEntreeFin):
        for i in range(indexEntreeDepart, indexEntreeFin):
            distance=self.attribuerCluster(points[i])
            #print ("cluster choisi:",point.cluster.centroide.id," distance:",distance)
    
    def attribuerCluster(self, point, multithread=False):#la fonction attribue à chaque point le cluster/centroide qui lui convient.
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
                #ancienCluster.points.remove(point)
                #ajouter le point dans son nouveau cluster
                #nouveauCluster.points.append(point)
                point.cluster=nouveauCluster
        return
    
    def calculerDistance(self, vect1, vect2):
        return np.sum(np.square(vect1-vect2))
    
    def calculerPositionCentroide(self, cluster):
        vecteurs=np.array([point.vectPosition for point in cluster.points])
        cluster.centroide.changerPosition(np.mean(vecteurs,axis=0))
        
    def calculerPositionsCentroides(self, clusters):
        for cluster in clusters:
            self.calculerPositionCentroide(cluster)
            #print(cluster.centroide.vectPosition)
    
    def sequenceCalcul(self, points, clusters):
        self.attribuerLesClusters(points, 0, len(self.points)-1)
        self.creerClustersAPartirDesPoints(self.points, self.clusters)
        self.calculerPositionsCentroides(clusters.values())
    
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
    threads=EnsembleThreads(calculator, nbThreads)
    threads.initierThreadsEtCalculerUneFois()
    calculator.calculerPositionsCentroides(calculator.clusters.values())
    while True:
        threads.calculer()
        i+=1
        #calculator.sequenceCalcul(calculator.points, calculator.clusters)
        print("calculé",i)