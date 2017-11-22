#-*- coding: utf8 -*-
#===============================================================================================
# Fichier : Points.py
# Projet  : B52_TP3
# Auteurs : Kevin Mwanangwa, Laurier Lavoie-Giasson, Chris David
#===============================================================================================

#Imports =======================================================================================
import numpy as np

#CLASSE CENTROIDE ==============================================================================
class IdMaker():
    currval=0
    def nextval():
        IdMaker.currval+=1
        return IdMaker.currval
class Centroide():
    def __init__(self,vectPosition):
        self.vectPosition=vectPosition
        self.id=IdMaker.nextval()
    
#CLASSE POINT ===================================================================================
class Point():
    def __init__(self,vectPosition,poids):
        self.vectPosition = vectPosition
        self.poids = poids
        self.cluster = None
            
#CLASSE CLUSTER =================================================================================
class Cluster():
    def __init__(self, centroide=None):
        self.centroide=centroide
        self.points=[];
        #self.idCluster=centroide.id

if __name__ == '__main__':
    for i in range(100):
        print(IdMaker.nextval())