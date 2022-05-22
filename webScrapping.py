#   ======================================
#   Importation des bibliothès nécessaires
#   ======================================
import requests
from bs4 import BeautifulSoup
import csv


#   ===============================
#   Défintion des variables de base
#   ===============================
urlBaseLivre = 'http://books.toscrape.com/catalogue/'                           # URL à compléter avec celle du livre
urlBaseCategory = 'https://books.toscrape.com/'                                 # URL à compléter avec celle de la catégorie
url = 'https://books.toscrape.com/index.html'                                   # URL de la page d'acceuil avec la liste des catégories


#   ==============================================================================================================================================
#   Fonction renvoyant les éléments à scrapper sur la page d'un livre // VERIFICATION A CHAQUE CARACTERISTIQUE SI ELLE EXISTE, SINON ON LE PRECISE
#   ==============================================================================================================================================
def recuperationDonneesMono(urlLivre):

    r = requests.get(urlLivre)

    if r.ok:
        print('Requête sur : ' + urlLivre + ' réussie !')

        texteParser = BeautifulSoup(r.text, features="html.parser") # Enregistrement de la réponse HTML dans une variable via la fonction BeautifulSoup parser avec la méthode HTML.parser
        productPageURL = urlLivre

        # On place dans un tableau tous les éléments des caractéristiques en bas de page et l'on récupère ceux qui nous intéressent
        elementsARecuperer = texteParser.findAll('td')
        if elementsARecuperer[0] == None:
            upc = "Pas d'UPC"
        else:
            upc = elementsARecuperer[0].text

        if elementsARecuperer[3] == None:
            priceIncludingTax = 'Pas de prix incluant la taxe'
        else:
            priceIncludingTax = elementsARecuperer[3].text

        if elementsARecuperer[2] == None:    
            priceExcludingTax = 'Pas de prix sans taxes' 
        else:
            priceExcludingTax = elementsARecuperer[2].text

        if elementsARecuperer[5] == None:
            numberAvailable = 'Pas de nombre restants'
        else:
            numberAvailable = elementsARecuperer[5].text



        if (texteParser.find('li', {'class': 'active'})) == None:                       # Ecriture de la variable titre
            titre = "Pas de titre"
        else:
            titre = (texteParser.find('li', {'class': 'active'})).text


        if (texteParser.find('p', {'class': ''})) == None:                              # Ecriture de la variable descriptionProduit
            descriptionProduit = "Pas de description du livre"
        else:
            descriptionProduit = (texteParser.find('p', {'class': ''})).text


        if (texteParser.find('img').get('src')) == None:                                # Ecriture de la variable imageURL
            imageURL = "Pas d'image"
        else:
            imageURLNonCorrigee = texteParser.find('img').get('src')
            imageURLCorrigee = imageURLNonCorrigee[5:]
            imageURL = 'http://books.toscrape.com/' + imageURLCorrigee


        categoryList = texteParser.findAll('li')                                        # Ecriture de la variable categoryProduct
        if categoryList[2] == None:
            categoryProduct = 'Pas de catégorie'
        else:
            categoryProduct = categoryList[2].text
 

        if (texteParser.findAll('p')) == None:                                          # Ecriture de la variable numberOfStars
            numberOfStars = "Pas de notations"
        else:
            reviewRatingList = texteParser.findAll('p')
            reviewRating = reviewRatingList[2].get('class')
            numberOfStars = reviewRating[1]

        return productPageURL, upc, titre, priceIncludingTax, priceExcludingTax, numberAvailable, descriptionProduit, categoryProduct, numberOfStars, imageURL  # Sera return un tuple
        
    else:
        print('Echec de la requête sur : ' + urlLivre)


#   =================================================================================
#   Fonction créant le fichier CSV avec le nom de la catégorie en cours de traitement
#   =================================================================================
def creationFichierCSV(nomDeLaCategorie):
    donneesCSV = [('product_page_URL', 'universal_ product_code', 'title', 'price_including_tax', 'price_excluding_tax', 'number_available', 'product_description', 'category', 'review_rating', 'image_url')]
    nomFichierCree = 'fichierCSV' + nomDeLaCategorie.replace(" ", "") + '.csv'
    fichier = open(nomFichierCree, 'w', encoding="utf-8")                           # On crée le fichier
    obj = csv.writer(fichier)                                                       # On crée l'objet permettant l'écriture dans le fichier

    for n in donneesCSV:                                            
        obj.writerow(n)                                                             # On écrit chacun des éléments sur la même ligne
    fichier.close()

    return nomFichierCree                                                           # On renvoie le nom du fichier CSV crée afin de le rentrer pour l'écriture des données                   


#   =====================================================================================
#   Fonction écrivant les données souhaitées dans un fichier CSV nommé "fichierCSVLivres"
#   =====================================================================================
def ecritureFichierCSV(nomDuFichierCSV, urlProduit, universal_product_code, title, price_including_tax, price_excluding_tax, number_available, product_description, category, review_rating, image_url):

    dataCSV = [(urlProduit, universal_product_code, title, price_including_tax, price_excluding_tax, number_available, product_description, category, review_rating, image_url)]
        
    fichierCSVOuvert = open(nomDuFichierCSV, 'a', newline='', encoding='utf-8')         # On ouvre le fichier
    objFichierOuvert = csv.writer(fichierCSVOuvert)                                     # On crée l'objet permettant l'écriture dans le fichier

    for i in dataCSV:
        objFichierOuvert.writerow(i)                                                    # On écrit chacun des éléments sur la même ligne
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
                print("Pas de bas de page trouvé")
                boolAutrePage = False                                                                                   # CONDITION DE SORTIE DE LA BOUCLE
            else:                                                                                                       # Si le bas de page existe on vérifie que le bouton "next" existe
                print("Un bas de page est présent")
                autrePage = basDePage.find('li', {'class': 'next'})                                                     

                if autrePage == None:
                    print("Pas de pages suivantes")
                    boolAutrePage = False

                else:
                    print("Page suivante trouvée")
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

            ecritureFichierCSV(nomDeLaCategorie, *recuperationDonneesMono(urlPage))                                      # Appel de la fonction ecritureFichierCSV avec '*' permettant à la fonction de séparer en plusieurs valeurs le tuple


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
















