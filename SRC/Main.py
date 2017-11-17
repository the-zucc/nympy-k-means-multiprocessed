#-*- coding: utf8 -*-
#===============================================================================================
# Fichier : Main.py
# Projet  : B52_TP3
# Auteurs : Kevin Mwanangwa, Laurier Lavoie-Giasson, Chris David
#===============================================================================================

#Imports =======================================================================================
import sys
from pip._vendor.distlib.compat import raw_input
from SQLConnector import SQLConnector
import time

#Methode user_Input ===========================================================================
def user_Input(Dictionnaire):
    #Init
    taille = nbCen = mots = nbMots = False
    #Verifier la presence des arguments -------------------------------------------------------
    for argument in sys.argv:
        if argument == "-t":
            taille = True
            idxTaille = sys.argv.index(argument)
        elif argument == "-nc":
            nbCen = True
            idxNbCen = sys.argv.index(argument)
        elif argument == "-m":
            mots = True
            idxMots = sys.argv.index(argument)
        elif argument == "-n":
            nbMots = True
            idxNbMots = sys.argv.index(argument)
            
    #Par nombre --------------------------------------------------------------------------------
    if (taille and nbCen) and (nbMots and mots)==False:
        #Taille
        try:
            ValeurTaille = int(sys.argv[idxTaille+1])            
        #En cas de valeur non-numerique
        except ValueError:
            print("/!\: Paramatre invalide, ('"+sys.argv[idxTaille+1]+"') n'est pas une valeur numerique.") 
            return (False,)            
        #NbCen
        try:
            ValeurCen = int(sys.argv[idxNbCen+1])            
        #En cas de valeur non-numerique
        except ValueError:
            print("/!\: Paramatre invalide, ('"+sys.argv[idxTaille+1]+"') n'est pas une valeur numerique.") 
            return (False,)
        
        #Si tout est bon
        return (True,"nombres",ValeurTaille,ValeurCen)            
   
    #Par mots --------------------------------------------------------------------------------
    if (taille and nbCen)==False and (nbMots and mots):        
        #Nombremots
        try:
            NombreDeMots = int(sys.argv[idxNbMots+1])            
        #En cas de valeur non-numerique
        except ValueError:
            print("/!\: Paramatre invalide, ('"+sys.argv[idxTaille+1]+"') n'est pas une valeur numerique.") 
            return (False,) 
        #Liste des mots
        i = idxMots+1
        ListeMots = {}
        #Tant qu'on a pas atteint le prochain parametre ou la fin des arguments
        while (i != idxNbMots) and (i != len(sys.argv)):
            motTmp = sys.argv[i]
            #Si mot dans dictionnaire
            if motTmp in Dictionnaire:
                #Ajouter mot
                ListeMots.append(sys.argv[i])
            else:
                print("/!\: Paramatre invalide, le mot ('"+sys.argv[i]+"') n'est pas dans le dictionnaire.") 
                return (False,) 
            
        #Si tout est bon
        return (True,"mots",ListeMots,NombreDeMots)
        
        
    
#Methode Main =================================================================================
def main():
    #Connection à la bd
    #Database = SQLConnector()
    
    #Input du User 
    dicc = {}
    dicc["wesh"]=1
    dicc["ta"]=2
    dicc["mere"]=3
    dicc["en"]=4
    dicc["shorts"]=5    
    
    user_Input(dicc)#Database.dictionnaire)
    

#Appel Fonction Main ==========================================================================
if __name__ == '__main__':
    sys.exit(main());