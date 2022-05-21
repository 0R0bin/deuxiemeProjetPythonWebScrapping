#   ======================================
#   Importation des bibliothès nécessaires
#   ======================================
import requests
from bs4 import BeautifulSoup
import csv


#   ========================================
#   On crée le fichier CSV avec ses colonnes
#   ========================================
donneesCSV = [('product_page_URL', 'universal_ product_code', 'title', 'price_including_tax', 'price_excluding_tax', 'number_available', 'product_description', 'category', 'review_rating', 'image_url')]
fichier = open('fichierCSVLivres.csv', 'w', encoding="utf-8")
obj = csv.writer(fichier)
for n in donneesCSV:
    obj.writerow(n)
fichier.close()


#   ===============================
#   Défintion des variables de base
#   ===============================
urlMultPage = 'index.html'                                              # URL qui sera modifiée si la page que nous sommes entrain de traiter possède d'autres pages
urlBase = 'http://books.toscrape.com/catalogue/'                        # URL finale à compléter avec celle du livre
boolAutrePage = True                                                    # Booléan qui nous permettra de sortir de la boucle


#   =================================================================
#   Fonction renvoyant les éléments à scrapper sur la page d'un livre
#   =================================================================
def recuperationDonneesMono(urlLivre):

    r = requests.get(urlLivre)

    if r.ok:
        print('Requête sur : ' + urlLivre + ' réussie !')


        texteParser = BeautifulSoup(r.text, features="html.parser") # Enregistrement de la réponse HTML dans une variable via la fonction BeautifulSoup parser avec la méthode HTML.parser
        
        productPageURL = urlLivre

        # On place dans un tableau tous les éléments des caractéristiques en bas de page et l'on récupère ceux qui nous intéressent
        elementsARecuperer = texteParser.findAll('td')
        upc = elementsARecuperer[0].text
        priceIncludingTax = elementsARecuperer[3].text
        priceExcludingTax = elementsARecuperer[2].text
        numberAvailable = elementsARecuperer[5].text

        titre = (texteParser.find('li', {'class': 'active'})).text

        descriptionProduit = (texteParser.find('p', {'class': ''})).text

        imageURLNonCorrigee = texteParser.find('img').get('src')
        imageURLCorrigee = imageURLNonCorrigee[5:]
        imageURL = 'http://books.toscrape.com/' + imageURLCorrigee

        categoryList = texteParser.findAll('li')
        categoryProduct = categoryList[2].text

        reviewRatingList = texteParser.findAll('p')
        reviewRating = reviewRatingList[2].get('class')
        numberOfStars = reviewRating[1]

        return productPageURL, upc, titre, priceIncludingTax, priceExcludingTax, numberAvailable, descriptionProduit, categoryProduct, numberOfStars, imageURL  # Sera return un tuple
        
    else:
        print('Echec de la requête sur : ' + urlLivre)

#   =====================================================================================
#   Fonction écrivant les données souhaitées dans un fichier CSV nommé "fichierCSVLivres"
#   =====================================================================================
def ecritureFichierCSV(urlProduit, universal_product_code, title, price_including_tax, price_excluding_tax, number_available, product_description, category, review_rating, image_url):

    dataCSV = [(urlProduit, universal_product_code, title, price_including_tax, price_excluding_tax, number_available, product_description, category, review_rating, image_url)]
        
    fichierCSVOuvert = open('fichierCSVLivres.csv', 'a', newline='', encoding='utf-8')
    objFichierOuvert = csv.writer(fichierCSVOuvert)

    for i in dataCSV:
        objFichierOuvert.writerow(i)
    fichier.close()



while boolAutrePage == True:

    urlCategoryPage = 'https://books.toscrape.com/catalogue/category/books/mystery_3/' + str(urlMultPage)       # URL de la page de la catégorie que nous sommes entrain de traiter
    rCategoryPage = requests.get(urlCategoryPage)                                                               # Requête pour scrapper les données de la catégorie choisie

    #   ===================================================================================
    #   Récupération des URL de chacun des livres + Check-UP si une autre page est présente
    #   ===================================================================================
    if rCategoryPage.ok:   
        print('Requête sur : ' + urlCategoryPage + ' réussie !')

        soup = BeautifulSoup(rCategoryPage.text, features="html.parser")                                        # Contient les informations de la page de la catégorie

        autrePage = soup.find('ul', {'class': 'pager'}).find('li', {'class': 'next'})                           # On vérifie si un élément li avec la classe next (correspondant au bouton) est présent dans le ul de classe pager
                                                                        
        if autrePage == None:                                                                                   # Si cet élément n'existe pas                                                       
            print("Pas d'autres pages trouvées")
            boolAutrePage = False                                                                               # CONDITION DE SORTIE DE LA BOUCLE
        else:
            autrePage = soup.find('ul', {'class': 'pager'}).find('a').get('href')                               # Si il existe, on récupère le lien du présent dans le bouton
            urlMultPage = autrePage                                                                             # Et on le place dans une varialbe qui est utilisée pour écrire urlCategoryPage présente plus haut
            boolAutrePage = True                                                                                # On reste dans notre boucle pour tester la prochaine page


        listURLNonParsees = soup.find('ol', {'class': 'row'}).findAll('h3')                                     # On récupère tous les titres H3 présents dans le <ol class=row>
        listURLMiParsees = []                                                                                   # On crée une liste qui contiendra tous les bouts d'URL de chacun des livres

        for i in range(len(listURLNonParsees)):
            listURLMiParsees.append(listURLNonParsees[i].find('a').get('href'))                                 # On ajoute les bouts d'URL dans notre liste

    else:
        print('Echec de la requête sur : ' + urlCategoryPage)


    #   ==========================================================================
    #   Execution du script python sur x livres présents dans la catégorie choisie
    #   ==========================================================================
    for i in range(len(listURLMiParsees)):
        urlTemp = listURLMiParsees[i]
        urlPage = urlBase + urlTemp[9:]                                                                         # On crée chacun des URL correspondant à chacun des livres de la page

        ecritureFichierCSV(*recuperationDonneesMono(urlPage))                                                   # Appel de la fonction ecritureFichierCSV avec '*' permettant à la fonction de séparer en plusieurs valeurs le tuple
