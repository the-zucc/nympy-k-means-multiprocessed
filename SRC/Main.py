#-*- coding: utf8 -*-
#========================================================================================================================
# Fichier : Main.py
# Projet  : B52_TP3
# Auteurs : Kevin Mwanangwa, Laurier Lavoie-Giasson, Chris David
#========================================================================================================================

#IMPORTS ================================================================================================================
import sys
from pip._vendor.distlib.compat import raw_input
from SQLConnector import SQLConnector
from Calculator import *
import time
from numpy import single
from test.regrtest import multiprocessing

#ANALYSER LA LIGNE DE COMMANDE/INPUT DU L'USAGER ========================================================================
def user_Input(DB):
    #Verifier la presence des arguments ------------------------------------------------------------------
    print("   /PROGRAM/  Vérification des paramètres ")        
    taille = nbCen = mots = nbMots = strangerDanger = multiThread = singleThread = False
    NombreThreads=0    
       
    for argument in sys.argv[1:]:
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
        elif argument == "-mt":
            multiThread = True
            idxNbThreads = sys.argv.index(argument)
        elif argument == "-st":
            singleThread = True
            idxSingle = sys.argv.index(argument)
            NombreThreads=0
        elif "-" in argument:
            strangerDanger = True
            idxStranger = sys.argv.index(argument)
            
    #Si il n'y a pas d'argument étranger, verifier la syntaxe --------------------------------------------
    if not strangerDanger:
        #Verifier Taille de fenetre ----------------------------------------------------------
        if taille:
            try:
                pass
                ValeurTaille = int(sys.argv[idxTaille+1])   
                #Verifier si il a des coocs avec cette fenetre
                if not DB.verifFenetre(ValeurTaille):
                    print("\n     /ERROR/  Aucune cooccurrence avec une fenetre de taille ('"+sys.argv[idxTaille+1]+"') présente dans la base de donnée.") 
                    return (False,)         
            #En cas de valeur non-numerique
            except ValueError:
                print("\n     /ERROR/  Paramètre invalide, ('"+sys.argv[idxTaille+1]+"') n'est pas une valeur numerique.") 
                return (False,)   
        else:         
            print("\n     /ERROR/  Paramètre manquant, ('-t')") 
            return (False,)
        
        #Initialisation par nombre de centroides ---------------------------------------------
        if nbCen and not mots: 
            #NbCen
            try:
                ValeurCen = int(sys.argv[idxNbCen+1])            
            #En cas de valeur non-numerique
            except ValueError:
                print("\n     /ERROR/  Paramètre invalide, ('"+sys.argv[idxNbCen+1]+"') n'est pas une valeur numerique.") 
                return (False,)
        #Initialisation par mots -------------------------------------------------------------       
        elif mots and not nbCen:
            #Liste des mots
            i = idxMots+1
            ListeMots = []
            #Tant qu'on a pas atteint le prochain parametre ou la fin des arguments
            while (i != idxMots) and (i != len(sys.argv)) and "-" not in sys.argv[i]:
                motTmp = sys.argv[i]
                #Si mot dans dictionnaire
                if motTmp in DB.dictionnaire.values():
                    #Ajouter mot
                    ListeMots.append(sys.argv[i])
                else:
                    print("\n     /ERROR/  Paramètre invalide, le mot ('"+motTmp+"') n'est pas dans le dictionnaire.") 
                    return (False,) 
                i+=1                
            
        #Si parametre en trop ou incompatible ------------------------------------------------
        else:
            print("\n     /ERROR/  Paramètres incompatibles, choisir UN des deux (-nc OU -m).") 
            return (False,) 
            
        #Verifier le nombre de mots -----------------------------------------------------------
        if nbMots:
            try:
                NombreDeMots = int(sys.argv[idxNbMots+1])            
            #En cas de valeur non-numerique
            except ValueError:
                print("\n     /ERROR/  Paramètre invalide, ('"+sys.argv[idxNbMots+1]+"') n'est pas une valeur numerique.") 
                return (False,)
        else:
            print("\n     /ERROR/  Svp, entrer un nombre de mots à afficher avec -n [nombre]")
            return (False,)
        if not multiThread and not singleThread:
            print("\n     /ERROR/  Paramètre manquant, -mt ou -st")
            return(False,)
        if multiThread and singleThread:
            print("\n     /ERROR/  Paramètres incompatibles, choisir UN des deux (-mt OU -st).")
            return(False,)
        if singleThread and not multiThread:
            multiThread=False
            NombreThreads=0
        if multiThread and not singleThread:
            try:
                nbProcesseurs = multiprocessing.cpu_count()
                NombreThreads = int(sys.argv[idxNbThreads+1])
                if(NombreThreads >= nbProcesseurs):
                    print("\n   /WARNING/  la configuration désirée serait inefficace, reconfiguration automatique.\n")
                    NombreThreads = nbProcesseurs//2
                    print("   /PROGRAM/  Configuration automatique -- nombre de processeurs:",nbProcesseurs,"nombre de processus à utiliser:",NombreThreads)
            #En cas de valeur non-numerique
            except ValueError:
                if sys.argv[idxNbThreads+1] == "auto":
                    NombreThreads = nbProcesseurs//2
                    print("   /PROGRAM/  Configuration automatique -- nombre de processeurs:",nbProcesseurs,"nombre de processus à utiliser:",NombreThreads)
                else:
                    print("\n     /ERROR/  Paramètre invalide, ('"+sys.argv[idxNbThreads+1]+"') n'est pas une valeur numerique.") 
                    return (False,)
            except IndexError:
                print("\n     /ERROR/  Paramètre manquant, -mt doit être suivi d'une valeur numérique (combien de processus exécuter? par défaut 1)")
                NombreThreads = 1
        #Si on arrive ici, params valides
        if mots:
            return(True,"mots",ValeurTaille,ListeMots,NombreDeMots,multiThread,NombreThreads)
        else:
            return(True,"nb",ValeurTaille,ValeurCen,NombreDeMots, multiThread,NombreThreads)

    #Si parametre invalide    
    else:
        print("\n     /ERROR/  Paramètre invalide, ('"+sys.argv[idxStranger]+"') n'est pas un argument valide.") 
        return (False,)

#MAIN ===================================================================================================================
def main():    
    #Connection à la bd
    Database = SQLConnector()        
    #Verifier l'input/Ligne de commande
    rep = user_Input(Database)     
    #Si input valide
    if rep[0]:
        TailleFenetre = rep[2]
        NombreDeMots = rep[4]
        multiThread = rep[5]
        NombreThreads = rep[6]
        if NombreThreads == 0:
            NombreThreads = 1
        #Si entree par mots
        if rep[1] == "mots":
            ListeDesMots = rep[3]
            print("   /PROGRAM/  [Clustering] "+" Taille de la fenetre :",TailleFenetre,"  Liste de mots :",ListeDesMots," Nb de mots à garder :",NombreDeMots,)
            print("   /PROGRAM/  [Clustering]  Mode d'exécution: Multiprocessing ->",multiThread,"  Nombre de processus:",NombreThreads)
            Params = (rep[1],TailleFenetre,ListeDesMots,NombreDeMots)
        #Si entree par nombre
        else:
            NombreCentroides = rep[3]
            print("   /PROGRAM/  [Clustering] "+" Taille de la fenetre :",TailleFenetre,"  Nb de centroides :",NombreCentroides," Nb de mots à garder :",NombreDeMots)
            print("   /PROGRAM/  [Clustering] Mode d'exécution: Multiprocessing ->",multiThread,"  Nombre de processus:",NombreThreads)
            Params = (rep[1],TailleFenetre,NombreCentroides,NombreDeMots)

        #initialisation de la calculatrice
        Calc = Calculator1(Params,Database)
        #multithread
        if multiThread:
            operationsMultiThread(Calc, NombreThreads)
        #singlethread
        else:
            #Debuter clustering -----------------------------------------------------------------------------
            Calc.clustering()

"""

==== MULTITHREAD ========================================================================================================================================================

"""            
def operationsMultiThread(Calc, NombreThreads):
    threads=EnsembleThreads1(Calc, NombreThreads)
    i=0
    startTime=time.time()
    startiter = time.time()
    timeiter=startiter
    Calc.fichier = open(Calc.filename,"a",encoding="utf-8") #Fix pour un bug
    tmp = OCD("*","MULTITHREADING : "+str(NombreThreads)+" PROCESSUS")+"\n"    
    Calc.fichier.write(tmp+"\n")
    print(tmp)
    
    while threads.calculer(): 
        tmp = "\n"+OCD("=","ITÉRATION #"+str(i+1)+" : ["+secondsToString(time.time()-timeiter)+"]")+"\n"        
        Calc.fichier.write(tmp+"\n")   
        print(tmp)    #D
        i+=1
        timeiter=time.time()
        
    #Une fois fini, grouping
    tmp =  OCD("*","CLUSTERING : ["+secondsToString(time.time()-startTime)+"]")+"\n\n\n\n\n"
    Calc.fichier.write(tmp+"\n")     
    print(tmp)
    
    #AFFICHER LES RESULTATS DU GROUPING ==============================================================================
    tmp = OCD("*","GROUPING DE "+str(Calc.nombreDeMotsAGarder)+" MOTS SUR "+str(Calc.nbCentroides)+" CLUSTERS")
    Calc.fichier.write(tmp+"\n")
    print(tmp)
            
    debutGrouping = time.time()     
    for c in range(Calc.nbCentroides):      
        tmp =  "\n"+OCD("=","GROUPE #"+str(c+1))+"\n"                                                        #Don't judge me, I have OCD - Kevin
        Calc.fichier.write(tmp+"\n") 
        print(tmp) 
        results = Calc.getTopResults(threads.dictClusters[c], c)            
        for index in range(len(results[0])):                        
            mot = Calc.Database.dictionnaire[results[0][index]]
            tmp ='{:5}'.format(str(index+1)+")")  +  '{:24}'.format(" "+mot)+str(results[1][index])            #Don't judge me, I have OCD - Kevin  
            Calc.fichier.write(tmp+"\n")
            print(tmp)                                                                                       #Don't judge me, I have OCD - Kevin  
                                                                                                   
    tmp = "\n\n"+OCD("*","GROUPING : ["+secondsToString(time.time()-debutGrouping)+"]")+"\n\n"               #Don't judge me, I have OCD - Kevin  
    Calc.fichier.write(tmp+"\n")
    Calc.fichier.close()
    print(tmp) 

#             
#EXECUTION DU PROGRAMME =================================================================================================
if __name__ == '__main__':
    print("NBCORES",multiprocessing.cpu_count())
    sys.exit(main());