#-*- coding: utf8 -*-
#===============================================================================================
# Fichier : Main.py
# Projet  : B52_TP3
# Auteurs : Kevin Mwanangwa, Laurier Lavoie-Giasson, Chris David
#===============================================================================================

from Points import *
import random
import numpy as np

largeurtest=300
hauteurtest=200
nombrepointstest=300

class Calculator():
    def __init__(self):
        self.points=[]
        self.centroides=[]
        self.clusters=[]
        #g�n�ration des donn�es pour le test                                                       o
        for i in range(nombrepointstest):
            vecteur=np.array()
            
            x=random.randrange(largeurtest)
            y=random.randrange(hauteurtest)
            
            self.points.append(Point(x,y, random.randrange(20)))
        for i in range(20):
            x=random.randrange(largeurtest)
            y=random.randrange(hauteurtest)
            self.centroides
    
    def attribuerLesClusters(self,points):
        for point in points:
            self.attribuerCluster(point)
    
    def attribuerCluster(self, point):
        centroideProche=None
        distanceCentroideProche=None
        for centroide in self.centroides:
            if(centroideProche is None):
                centroideProche=centroide
                distanceCentroideProche=self.calculerDistance(point.x, point.y, centroide.x, centroide.y)
            else:
                distanceCentroide=self.calculerDistance(point.x, point.y, centroide.x, centroide.y)
                if(distanceCentroide < distanceCentroideProche):
                    centroideProche=centroide
                    distanceCentroideProche=distanceCentroide
            #attribuer le cluster a partir du centroide
    def calculerDistance(self, vect1, vect2):
        return np.sum(np.square(vect1), np.square(vect2))