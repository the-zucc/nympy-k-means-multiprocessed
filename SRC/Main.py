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
def user_Input(DB):
    print("   /PROGRAM/  Vérification des paramètres ")
    #Init
    taille = nbCen = mots = nbMots = strangerDanger = False    
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
        elif "-" in argument:
            strangerDanger = True
            idxStranger = sys.argv.index(argument)
            
    #Verifier argument etranger
    if not strangerDanger:
        #Par nombre --------------------------------------------------------------------------------
        if (taille and nbCen) and not (nbMots or mots):        
            #Taille
            try:
                ValeurTaille = int(sys.argv[idxTaille+1])   
                #Verifier si il a des coocs avec cette fenetre
                if not DB.verifFenetre(ValeurTaille):
                    print("\n     /ERROR/  Aucune cooccurrence avec une fenetre de taille ('"+sys.argv[idxTaille+1]+"') présente dans la base de donnée.") 
                    return (False,)         
            #En cas de valeur non-numerique
            except ValueError:
                print("\n     /ERROR/  Paramètre invalide, ('"+sys.argv[idxTaille+1]+"') n'est pas une valeur numerique.") 
                return (False,)            
            #NbCen
            try:
                ValeurCen = int(sys.argv[idxNbCen+1])            
            #En cas de valeur non-numerique
            except ValueError:
                print("\n     /ERROR/  Paramètre invalide, ('"+sys.argv[idxNbCen+1]+"') n'est pas une valeur numerique.") 
                return (False,)
            
            #Si tout est bon
            return (True,"nombres",ValeurTaille,ValeurCen)  
        elif (taille and nbCen) and (nbMots or mots):
            if nbMots:
                print("\n     /ERROR/  Paramètre invalide, ('"+sys.argv[idxNbMots]+"') n'est pas un argument valide pour cette opération (-t,-nc)") 
            if mots:
                print("\n     /ERROR/  Paramètre invalide, ('"+sys.argv[idxMots]+"') n'est pas un argument valide pour cette opération (-t,-nc)") 
            return (False,) 
       
        #Par mots --------------------------------------------------------------------------------
        elif not (taille or nbCen) and (nbMots and mots):             
            #Nombremots
            try:
                NombreDeMots = int(sys.argv[idxNbMots+1])            
            #En cas de valeur non-numerique
            except ValueError:
                print("\n     /ERROR/  Paramètre invalide, ('"+sys.argv[idxTaille+1]+"') n'est pas une valeur numerique.") 
                return (False,) 
            #Liste des mots
            i = idxMots+1
            ListeMots = []
            #Tant qu'on a pas atteint le prochain parametre ou la fin des arguments
            while (i != idxNbMots) and (i != len(sys.argv)):
                motTmp = sys.argv[i]
                #Si mot dans dictionnaire
                if motTmp in DB.dictionnaire:
                    #Ajouter mot
                    ListeMots.append(sys.argv[i])
                else:
                    print("\n     /ERROR/  Paramètre invalide, le mot ('"+sys.argv[i]+"') n'est pas dans le dictionnaire.") 
                    return (False,) 
                i+=1
                
            #Si tout est bon
            return (True,"mots",ListeMots,NombreDeMots)
        
        elif (taille or nbCen) and (nbMots and mots): 
            if taille:
                print("\n     /ERROR/  Paramètre invalide, ('"+sys.argv[idxTaille]+"') n'est pas un argument valide pour cette opération (-m,-n)") 
            if nbCen:
                print("\n     /ERROR/  Paramètre invalide, ('"+sys.argv[idxNbCen]+"') n'est pas un argument valide pour cette opération (-m,-n)") 
            return (False,) 
            
    else:  
        print("\n     /ERROR/  Paramètre invalide, ('"+sys.argv[idxStranger]+"') n'est pas un argument valide.") 
        return (False,)  
    
#Methode Main =================================================================================
def main():
    
    #Connection à la bd
    Database = SQLConnector()    
    
    #Verifier l'input/Ligne de commande
    rep = user_Input(Database)     
    #Si input valide
    if rep[0]:
        #Si entree par mots
        if rep[1] == "mots":
            ListeDesMots = rep[2]
            NombreDeMots = rep[3]
            print("   /PROGRAM/  [Clustering] Liste de mots :",ListeDesMots,"  Nombre de mots a afficher par cluster :",NombreDeMots)
        #Si entree par nombre
        else:
            TailleFenetre = rep[2]
            NombreCentroides = rep[3]
            print("   /PROGRAM/  [Clustering] Taille de la fenetre :",TailleFenetre,"  Nb de centroides :",NombreCentroides)
    

#Appel Fonction Main ==========================================================================
if __name__ == '__main__':
    sys.exit(main());