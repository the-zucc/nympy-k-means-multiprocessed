#-*- coding: utf8 -*-
#===============================================================================================
# Fichier : Calculator.py
# Projet  : B52_TP3
# Auteurs : Kevin Mwanangwa, Laurier Lavoie-Giasson, Chris David
#===============================================================================================
from Points import *
import random
import numpy as np

largeurtest=3000
hauteurtest=200
nombrepointstest=20000
nombrecentroidestest=50

class Calculator():
    def __init__(self):
        self.points=[]
        self.centroides=[]
        self.clusters={}
        #génération des données pour le test                                                       o
        for i in range(nombrepointstest):
            position=self.genererPosition()
            self.points.append(Point(position, 1))
            
        for i in range(nombrecentroidestest):
            position=self.genererPosition()
            centroide=Centroide(position)
            self.centroides.append(centroide)
            print(centroide.id)
            self.clusters[centroide.id]=Cluster(centroide)
    
    def genererPosition(self):
        position=np.zeros(10)
        for i in range(len(position)):
            position[i]=random.randrange(largeurtest)
        return position
    
    def attribuerLesClusters(self,points):
        for point in points:
            distance=self.attribuerCluster(point)
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
        return distanceCentroideProche
    
    def calculerDistance(self, vect1, vect2):
        return np.sum(np.square(vect1-vect2))
    
    def calculerPositionCentroide(self, cluster):
        vecteurs=np.array([point.vectPosition for point in cluster.points])
        cluster.centroide.changerPosition(np.mean(vecteurs,axis=0))
        
    def calculerPositionsCentroides(self, clusters):
        for cluster in clusters:
            self.calculerPositionCentroide(cluster)
            print("ancienne position centroide: ", cluster.centroide.anciennePosition)
            print("nouvelle position centroide: ", cluster.centroide.vectPosition)
    
    def sequenceCalcul(self, points, clusters):
        self.attribuerLesClusters(points)
        self.calculerPositionsCentroides(clusters.values())
if __name__ == '__main__':
    calculator=Calculator()
    calculator.sequenceCalcul(calculator.points, calculator.clusters)