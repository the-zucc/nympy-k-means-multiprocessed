#-*- coding: utf8 -*-
#===============================================================================================
# Fichier : Calculator.py
# Projet  : B52_TP3
# Auteurs : Kevin Mwanangwa, Laurier Lavoie-Giasson, Chris David
#===============================================================================================

#Imports =======================================================================================
import numpy as np

#CLASSE CENTROIDE ==============================================================================
class Centroide():
    def __init__(self,x,y):
        self.x = x
        self.y = y
    
#CLASSE POINT ===================================================================================
class Point():
    def __init__(self,x,y,motx,moty,poids):
        self.x = x
        self.y = y 
        self.motx = motx
        self.moty = moty
        self.poids = poids
            
#CLASSE CLUSTER =================================================================================
class Cluster():
    def __init__(self):
        self.points = {} #Objets points
        self.centroide = None #Objet centroide
