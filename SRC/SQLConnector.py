#-*- coding: utf8 -*-
#===============================================================================================
# Fichier : SQLConnector.py
# Projet  : B52_TP3
# Auteurs : Kevin Mwanangwa, Laurier Lavoie-Giasson, Chris David
#===============================================================================================

#Imports =======================================================================================
import sys
import cx_Oracle
import time

#Class SQLConnector ============================================================================
class SQLConnector():
    def __init__ (self):
        #CONNECTION A LA BD --------------------------------------------------------------------
        print("   /PROGRAM/  Debut connection")
        startConn = time.time()
        PATH_ORACLE = 'C:\Oracle\Client\product\12.2.0\client_1\bin'
        sys.path.append(PATH_ORACLE)    
        dsn_tns = cx_Oracle.makedsn('delta', 1521, 'decinfo')
        chaineConnexion = 'e1484242' + '/' + "ZZZzzz111"+ '@' + dsn_tns
        self.connexion = cx_Oracle.connect(chaineConnexion)
        self.cur = self.connexion.cursor()
        endConn = time.time() - startConn
        print("     /TIMER/  Connection avec la BD : ",endConn, "secondes")        
               
        #DICTIONNAIRE ---------------------------------------------------------------------------
        self.dictionnaire = {}
        #Init le dictionnaire
        print("   /PROGRAM/  Remplir dictionnaire interne")
        startDict = time.time()
        self.get_dict()  
        endDict = time.time() - startDict
        print("     /TIMER/  Recuperer ",len(self.dictionnaire)," lignes dans la table DICTIONNAIRE : ",endDict, "secondes")   
        
        #COOCCURRENCES --------------------------------------------------------------------------
        self.coocs = {}  
        print("   /PROGRAM/  Remplir cooccurrences internes")
        startCoocs = time.time()
        self.get_coocs()  
        endCoocs = time.time() - startCoocs
        print("     /TIMER/  Recuperer ",len(self.coocs)," lignes dans la table COOCCURRENCES : ",endCoocs, "secondes")  
        
    #Cherche la table DICTIONNAIRE de la BD   
    def get_dict(self):
        enonce = "SELECT * FROM dictionnaire"        
        self.cur.execute(enonce)
        for rangee in self.cur.fetchall():    
            #Inserer (mot,id)         
            self.dictionnaire[rangee[1]]=int(rangee[0])   
     
    #Cherche la table COOCCURRENCES de la BD       
    def get_coocs(self):
        enonce = "SELECT * FROM cooccurrences WHERE fenetre_cooc = "+str(self.fenetre)+" ORDER BY id"        
        self.cur.execute(enonce)
        for ligne in self.cur.fetchall():           
            #Inserer mot1, mot2 et nbCooccurrences
            idmot1 = int(ligne[1])
            idmot2 = int(ligne[2])
            idx = int(ligne[0])
            nbc = int(ligne[4])
            self.coocs[(idmot1,idmot2)] = idx
            self.nbcoocs[idx] = nbc        