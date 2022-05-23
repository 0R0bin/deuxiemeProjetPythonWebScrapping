#   ======================================
#   Importation des bibliothès nécessaires
#   ======================================
import requests
from bs4 import BeautifulSoup
import csv
import string
import os


#   ===============================
#   Défintion des variables de base
#   ===============================
urlBaseLivre = 'http://books.toscrape.com/catalogue/'                           # URL à compléter avec celle du livre
urlBaseCategory = 'https://books.toscrape.com/'                                 # URL à compléter avec celle de la catégorie
url = 'https://books.toscrape.com/index.html'                                   # URL de la page d'acceuil avec la liste des catégories
valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)              # On impose les caractères valables pour les noms de fichiers


#   ====================================================================
#   Petit script permettant de choisir si l'on traite ou non les données
#   ====================================================================
print("Veuillez indiquer si vous souhaitez ou non traiter les données CSV en indiquant oui ou non")
print("\nEntrez oui ou non (choix par défaut : Oui) \n")
choixUser = input()                                                              # Bool pour indiquer au programme s'il doit traiter les données envoyées aux fichiers CSV

if choixUser == "Oui" or choixUser == "oui":
    bTraitement = True
    print('\nLes données seront traitées (suppression des virugles et pas de texte dans la colonne "Elements restants" \n')
elif choixUser == "Non" or choixUser == "non":
    bTraitement = False
    print("\nLes données ne seront pas traitées et resteront comme demandées à la base \n")
else:
    bTraitement = True
    print("\nChoix par défaut séléctionné car la valeure entrée était innatendue \n")
    print("Les données seront donc traitées \n")


print("Lancement du Scrapping du site : " + url + "\n")


#   =======================================================
#   Fonction enlevant les caractères non ASCII d'une string
#   =======================================================
def removeNonASCII(s):
    return "".join(c for c in s if ord(c)<128)


#   ==============================================================================================================================================
#   Fonction renvoyant les éléments à scrapper sur la page d'un livre // VERIFICATION A CHAQUE CARACTERISTIQUE SI ELLE EXISTE, SINON ON LE PRECISE
#   ==============================================================================================================================================
def recuperationDonneesMono(urlLivre):

    r = requests.get(urlLivre)

    if r.ok:
        print('Requête sur : ' + urlLivre + ' réussie !')

        cBook = {}                                                                                      # On crée le dictionnaire qui contiendra toutes les informations de notre livre

        texteParser = BeautifulSoup(r.text, features="html.parser")                                     # Enregistrement de la réponse HTML dans une variable via la fonction BeautifulSoup parser avec la méthode HTML.parser

        cBook["URLBook"] = urlLivre                     

        elementsARecuperer = texteParser.findAll('td')                                                  # On place dans un tableau tous les éléments des caractéristiques en bas de page et l'on récupère ceux qui nous intéressent
        if elementsARecuperer[0] == None:
            cBook["upc"] = "Pas d'UPC"
        else:
            cBook["upc"] = elementsARecuperer[0].text

        if elementsARecuperer[3] == None:
            cBook["PrixTTC"] = 'Pas de prix TTC'
        else:
            if bTraitement == True :
                prixTTC = removeNonASCII(elementsARecuperer[3].text)                                    # On crée la clé "PrixTTC" en enlevant "£"
            else:
                prixTTC = elementsARecuperer[3].text
            cBook["PrixTTC"] = prixTTC

        if elementsARecuperer[2] == None:    
            cBook["PrixHT"] = 'Pas de prix HT' 
        else:
            if bTraitement == True:
                prixHT = removeNonASCII(elementsARecuperer[2].text)                                     # On crée la clé "PrixHT" en enlevant "£"
            else:
                prixHT = elementsARecuperer[2].text                                                     # On crée la clé "PrixHT" en enlevant "£"
            cBook["PrixHT"] = prixHT

        if elementsARecuperer[5] == None:
            cBook["nbRestants"] = 'Pas de nombre restants'
        else:
            if bTraitement == True:
                SnbRestants = elementsARecuperer[5].text                                                # On rentre la string "In Stock (x Available)"
                nbRestants = ""                                                                         # On crée la variable qui contiendra le nombre d'éléments restants           
                for character in SnbRestants:                                                   
                    if character.isdigit():                                                             # Si le caractère est un nombre            
                        nbRestants += character                                                         # On l'ajoute à la variable nbRestants
            else:
                nbRestants = elementsARecuperer[5].text 

            cBook["nbRestants"] = nbRestants
            

        if (texteParser.find('li', {'class': 'active'})) == None:                                       # Ecriture de la clé titre
            cBook["titre"] = "Pas de titre"
        else:
            cBook["titre"] = (texteParser.find('li', {'class': 'active'})).text


        if (texteParser.find('p', {'class': ''})) == None:                                              # Ecriture de la clé descriptionProduit
            cBook["descriptionProduit"] = "Pas de description du livre"
        else:
            cBook["descriptionProduit"] = removeNonASCII((texteParser.find('p', {'class': ''})).text)
            if bTraitement == True:                                                                     # Vérification si le fichier CSV doit supprimer les virgules pour lui permettre d'être lu par Excel
                cBook["descriptionProduit"] = cBook["descriptionProduit"].replace(',', ';')


        if (texteParser.find('img').get('src')) == None:                                                # Ecriture de la clé imageURL + Téléchargement de l'image associée
            cBook["imageURL"] = "Pas d'image"
        else:
            imageURLNonCorrigee = texteParser.find('img').get('src')
            imageURLCorrigee = imageURLNonCorrigee[5:]
            cBook["imageURL"] = 'http://books.toscrape.com/' + imageURLCorrigee

            imageDL = requests.get(cBook["imageURL"]).content                                           # On fait une nouvelle requête sur l'URL de l'image pour la télécharger

            nomFichierJPG = ''.join(c for c in cBook["titre"] if c in valid_chars)                      # On autorise que les caractères autorisés dans notre nomFichierJPG
            nomFichierJPG = nomFichierJPG[:100]                                                         # On impose une limite de 100 caractères pour le nom du fichier
            nomFichierJPG = nomFichierJPG + '.jpg'                                      
            emplacementFichierPython = os.getcwd()                                                      # On récupère l'emplacement du fichier Python
            filepath = emplacementFichierPython + '\Images'                                             # On récupère l'emplacement du fichier Python et on rajoute /Images dans le chemin d'accès

            cheminEtNomJPG = os.path.join(filepath, nomFichierJPG)                                      # On crée le chemin d'accès avec le nom de notre fichier
            if not os.path.exists(filepath):                                                            # On vérifie que le dossier Images soit créé
                os.makedirs(filepath)                                                                   # Si il n'existe pas, on le créer

            with open(cheminEtNomJPG, 'wb') as imgObj:                                                  # On crée le fichier qui contiendra l'image
                imgObj.write(imageDL)                                                                   # On télécharge l'image dans notre fichier


        categoryList = texteParser.findAll('li')                                                        # Ecriture de la clé categoryProduct
        if categoryList[2] == None:
            cBook["category"] = 'Pas de catégorie'
        else:
            cBook["category"] = (categoryList[2].text).replace("\n", "")                                # Ecriture de la clé category + suppression des \n présents
 

        if (texteParser.findAll('p')) == None:                                                          # Ecriture de la clé numberOfStars
            cBook["Note"] = "Pas de note"
        else:
            reviewRatingList = texteParser.findAll('p')
            reviewRating = reviewRatingList[2].get('class')
            cBook["Note"] = reviewRating[1]

        return cBook
        
    else:
        print('Echec de la requête sur : ' + urlLivre)


#   =================================================================================
#   Fonction créant le fichier CSV avec le nom de la catégorie en cours de traitement
#   =================================================================================
def creationFichierCSV(nomDeLaCategorie):
    donneesCSV = [('product_page_URL', 'universal_ product_code', 'title', 'price_including_tax', 'price_excluding_tax', 'number_available', 'product_description', 'category', 'review_rating', 'image_url')]
    nomFichierCSV = 'fichierCSV' + nomDeLaCategorie.replace(" ", "") + '.csv'                                           # On crée un nom de fichier avec la catégorie traitée
    emplacementFichierPython = os.getcwd()                                                                              # On sauvegarde l'emplacement du fichier Python
    filepath = emplacementFichierPython + '\FichiersCSV'                                                                # On crée le cheminement pour enregistrer les fichiers CSV
    cheminEtNomCSV = os.path.join(filepath, nomFichierCSV)                                                              # On crée le chemin d'accès pour notre fichier CSV

    if not os.path.exists(filepath):                                                                                    # On vérifie que le dossier CSV soit créé
        os.makedirs(filepath)                                                                                           # Si il n'existe pas, on le créer

    fichier = open(cheminEtNomCSV, 'w', encoding="utf-8")                                                               # On crée le fichier
    obj = csv.writer(fichier)                                                                                           # On crée l'objet permettant l'écriture dans le fichier

    for n in donneesCSV:                                            
        obj.writerow(n)                                                                                                 # On écrit chacun des éléments sur la même ligne
    fichier.close()

    return cheminEtNomCSV                                                                                               # On renvoie le nom du fichier CSV crée afin de le rentrer pour l'écriture des données                   


#   =====================================================================================
#   Fonction écrivant les données souhaitées dans un fichier CSV nommé "fichierCSVLivres"
#   =====================================================================================
def ecritureFichierCSV(nomDuFichierCSV, cBook):
    dataCSV = [(cBook['URLBook'], cBook['upc'], cBook['titre'], cBook['PrixTTC'], cBook['PrixHT'], cBook['nbRestants'], cBook['descriptionProduit'], cBook['category'], cBook['Note'], cBook['imageURL'])]
        
    fichierCSVOuvert = open(nomDuFichierCSV, 'a', newline='', encoding='utf-8')                                         # On ouvre le fichier
    objFichierOuvert = csv.writer(fichierCSVOuvert)                                                                     # On crée l'objet permettant l'écriture dans le fichier

    for i in dataCSV:
        objFichierOuvert.writerow(i)                                                                                    # On écrit chacun des éléments sur la même ligne
    fichierCSVOuvert.close()


#   ======================================================================================
#   Fonction Scrappant toutes les données dans une catégorie qu'importe son nombre de page
#   ======================================================================================
def scrappingAllInCategory(urlDeLaCategorie, nomDeLaCategorie):

    boolAutrePage = True                                                                                                # Condition pour rentrer dans la boucle while
    urlMultPage = 'index.html'                                                                                          # Fin de l'URL qui sera remplacée par celle de la catégorie                                                            
                       
    while boolAutrePage == True:

        urlCategoryPage = urlDeLaCategorie + urlMultPage                                                                # URL de la page de la catégorie que nous sommes entrain de traiter   
        rCategoryPage = requests.get(urlCategoryPage)                                                                   # Requête pour scrapper les données de la catégorie choisie  

        #   ===================================================================================
        #   Récupération des URL de chacun des livres + Check-UP si une autre page est présente
        #   ===================================================================================
        if rCategoryPage.ok:   
            print('Requête sur : ' + urlCategoryPage + ' réussie !')

            soup = BeautifulSoup(rCategoryPage.text, features="html.parser")                                            # Contient les informations de la page de la catégorie

            basDePage = soup.find('ul', {'class': 'pager'})                                                             # On recherche un bas de page
                                                                            
            if basDePage == None:                                                                                       # Si cet élément n'existe pas alors on sort de la boucle                                                      
                print("\nPas de bas de page trouvé, une seule page à scrapper \n")
                boolAutrePage = False                                                                                   # CONDITION DE SORTIE DE LA BOUCLE
            else:                                                                                                       # Si le bas de page existe on vérifie que le bouton "next" existe
                print("\nUn bas de page est présent, on vérifie si il y a une page suivante \n")
                autrePage = basDePage.find('li', {'class': 'next'})                                                     

                if autrePage == None:
                    print("Pas de pages suivantes \n")
                    boolAutrePage = False

                else:
                    print("Page suivante trouvée \n")
                    lienPageSuivante = autrePage.find('a').get('href')                                                  # Si il existe, on récupère le lien du présent dans le bouton
                    urlMultPage = lienPageSuivante                                                            
                                                            

            listURLNonParsees = soup.find('ol', {'class': 'row'}).findAll('h3')                                         # On récupère tous les titres H3 présents dans le <ol class=row>
            listURLMiParsees = []                                                                                       # On crée une liste qui contiendra tous les bouts d'URL de chacun des livres

            for i in range(len(listURLNonParsees)):
                listURLMiParsees.append(listURLNonParsees[i].find('a').get('href'))                                     # On ajoute les bouts d'URL dans notre liste

        else:
            print('Echec de la requête sur : ' + urlCategoryPage)

        #   ==========================================================================
        #   Execution du script python sur x livres présents dans la catégorie choisie
        #   ==========================================================================
        for i in range(len(listURLMiParsees)):
            urlTemp = listURLMiParsees[i]
            urlPage = urlBaseLivre + urlTemp[9:]                                                                         # On crée chacun des URL correspondant à chacun des livres de la page

            ecritureFichierCSV(nomDeLaCategorie, recuperationDonneesMono(urlPage))                                       # Appel de la fonction ecritureFichierCSV


#   =====================================================================
#   Execution du script python scrappant chaque livre de chaque catégorie
#   =====================================================================
rTotal = requests.get(url)                      
pagePrincipal = BeautifulSoup(rTotal.text, features="html.parser")    

toutesLesCategories = pagePrincipal.find('ul', {'class': 'nav nav-list'}).find('li').findAll('li')

for i in range(len(toutesLesCategories)):

    finLienCategorie = toutesLesCategories[i].find('a').get('href')
    nomCategorie = toutesLesCategories[i].find('a').text.replace("\n", "")
    lienCategorie = urlBaseCategory + finLienCategorie

    nomFichierCree = creationFichierCSV(nomCategorie)
    scrappingAllInCategory(lienCategorie[:-10], nomFichierCree)


print("Scrapping du site réussi !")