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
urlBase = 'http://books.toscrape.com/catalogue/'                                                            # URL à compléter avec celle du livre
urlCategoryPage = 'http://books.toscrape.com/catalogue/category/books/sports-and-games_17/index.html'       # URL de la catégorie que nous sommes entrain de traiter
rCategoryPage = requests.get(urlCategoryPage)                                                               # Requête pour scrapper les données de la catégorie choisie


#   =========================================
#   Récupération des URL de chacun des livres
#   =========================================
if rCategoryPage.ok:   
    print('Requête sur : ' + urlCategoryPage + ' réussie !')

    soup = BeautifulSoup(rCategoryPage.text, features="html.parser")
    listURLNonParsees = soup.find('ol', {'class': 'row'}).findAll('h3')
    listURLMiParsees = []

    for i in range(len(listURLNonParsees)):
        listURLMiParsees.append(listURLNonParsees[i].find('a').get('href'))

else:
    print('Echec de la requête sur : ' + urlCategoryPage)


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


#   ==========================================================================
#   Execution du script python sur x livres présents dans la catégorie choisie
#   ==========================================================================
for i in range(len(listURLMiParsees)):
    urlTemp = listURLMiParsees[i]
    urlPage = urlBase + urlTemp[9:]

    ecritureFichierCSV(*recuperationDonneesMono(urlPage)) # Appel de la fonction ecritureFichierCSV avec '*' permettant à la fonction de séparer en plusieurs valeurs le tuple

    



