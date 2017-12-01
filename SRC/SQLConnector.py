#-*- coding: utf8 -*-
#=========================================================================================================================
# Fichier : SQLConnector.py
# Projet  : B52_TP3
# Auteurs : Kevin Mwanangwa, Laurier Lavoie-Giasson, Chris David
#=========================================================================================================================

#Imports =================================================================================================================
import sys
import cx_Oracle
import time
import csv
import os

#CLASSE SQLConnector =====================================================================================================
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
        print("   /PROGRAM/  Remplir dictionnaire interne")
        startDict = time.time()
        self.get_dict()  
        endDict = time.time() - startDict
        print("     /TIMER/  Recuperer ",len(self.dictionnaire)," lignes dans la table DICTIONNAIRE : ",endDict, "secondes")   
        #COOCCURRENCES --------------------------------------------------------------------------
        #Si fichier cvm n'existe pas, loader Coocs dans la bd est generer CSV
        if not os.path.isfile('TP3_KevLauChr.csv'):           
            self.coocs = {}  
            self.nbcoocs = {}
            self.tailleFenetre = {}
            print("   /PROGRAM/  Remplir cooccurrences internes")
            startCoocs = time.time()
            self.get_coocs()  
            endCoocs = time.time() - startCoocs
            print("     /TIMER/  Recuperer ",len(self.coocs)," lignes dans la table COOCCURRENCES : ",endCoocs, "secondes")  
            startCSV = time.time()
            print("   /PROGRAM/  Remplir fichier CSV")
            self.csvEcriture()
            endCSV = time.time()-startCSV
            print("     /TIMER/  Écrire ",len(self.coocs)," lignes dans le fichier TP3_KevLauChr.csv : ",endCSV, "secondes")              
        
    #RECUPERER LA TABLE DICTIONNAIRE DANS LA BD =================================================== 
    def get_dict(self):
        enonce = "SELECT * FROM dictionnaire"        
        self.cur.execute(enonce)
        for rangee in self.cur.fetchall():    
            #Inserer (mot,id)         
            self.dictionnaire[rangee[1]]=int(rangee[0])-1   
   
    #VERIFIER LA TAILLE DE LA FENETRE DANS LA BD ==================================================
    def verifFenetre(self,fenetre):
        enonce = "SELECT count(*) FROM cooccurrences WHERE fenetre_cooc = "+str(fenetre)+" ORDER BY id"        
        self.cur.execute(enonce)
        for rangee in self.cur.fetchall():            
            nbCoocs = int(rangee[0])          
        if nbCoocs != 0:
            return True
        else:
            return False 
     
    #RECUPERER LA TABLE COOCCURRENCES DANS LA BD ==================================================
    def get_coocs(self):
        enonce = "SELECT * FROM cooccurrences ORDER BY id"        
        self.cur.execute(enonce)
        for ligne in self.cur.fetchall():           
            #Inserer mot1, mot2 et nbCooccurrences
            idmot1 = int(ligne[1])
            idmot2 = int(ligne[2])
            idx = int(ligne[0])
            taille = int(ligne[3])
            nbc = int(ligne[4])
            self.coocs[(idmot1,idmot2)] = idx
            self.nbcoocs[idx] = nbc
            self.tailleFenetre[idx] = taille
            
    #REMPLIR LE FICHIER CSV ======================================================================
    def csvEcriture(self):
        f = open('TP3_KevLauChr.csv','w')
        w = csv.writer(f)
        for ((id_mot1,id_mot2),idx) in self.coocs.items():
            score = self.nbcoocs[idx]    
            fenetre = self.tailleFenetre[idx]        
            w.writerow([id_mot1, id_mot2, fenetre, score])   
        f.close()        
        
    #LIRE LES DONNÉES DU FICHIER CSV =============================================================
    def csvLecture(self, matrice, fenetre):
        lectureFichier = csv.reader(open("TP3_KevLauChr.csv","r"))        
        for row in lectureFichier:
            if(len(row) > 0):           
                if int(row[2]) == fenetre:
                    idmot1 = int(row[0])-1
                    idmot2 = int(row[1])-1
                    nbcoocs = int(row[3])
                    matrice[idmot1][idmot2] = nbcoocs
            
        