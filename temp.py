#   ======================================
#   Importation des bibliothès nécessaires
#   ======================================
import requests
from bs4 import BeautifulSoup
import csv

urlBase = 'http://books.toscrape.com/catalogue/'
urlCategoryPage = 'http://books.toscrape.com/catalogue/category/books/sports-and-games_17/index.html'
rCategoryPage = requests.get(urlCategoryPage) 



#   ========================================
#   On crée le fichier CSV avec ses colonnes
#   ========================================
donneesCSV = [('product_page_URL', 'universal_ product_code', 'title', 'price_including_tax', 'price_excluding_tax', 'number_available', 'product_description', 'category', 'review_rating', 'image_url')]
fichier = open('fichierCSVLivres.csv', 'w', encoding="utf-8")
obj = csv.writer(fichier)
for n in donneesCSV:
    obj.writerow(n)
fichier.close()




if rCategoryPage.ok:    # Si la requête renvoi bien <Response [200]>
    print('Requête réussie')

    soup = BeautifulSoup(rCategoryPage.text, features="html.parser")
    listURLNonParsees = soup.find('ol', {'class': 'row'}).findAll('h3')
    listURLMiParsees = []
    for i in range(len(listURLNonParsees)):
        listURLMiParsees.append(listURLNonParsees[i].find('a').get('href'))

else:
    print('Echec de la requête')


#   ===================================================
#   Fonction renvoyant les éléments demandés à Scrapper
#   ===================================================
def recuperationDonneesMono(urlLivre):


    r = requests.get(urlLivre)
    texteParser = BeautifulSoup(r.text, features="html.parser") # Enregistrement de la réponse HTML dans une variable via la fonction BeautifulSoup parser avec la méthode HTML.parser
    
    productPageURL = urlLivre

    # On place dans un tableau tous les éléments du "tableau" des caractéristiques en bas de page et l'on récupère ceux qui nous intéressent
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

    return productPageURL, upc, titre, priceIncludingTax, priceExcludingTax, numberAvailable, descriptionProduit, categoryProduct, numberOfStars, imageURL

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




for i in range(len(listURLMiParsees)):
    urlTemp = listURLMiParsees[i]
    urlPage = urlBase + urlTemp[9:]
    print(urlPage)

    ecritureFichierCSV(*recuperationDonneesMono(urlPage))

    



