#   ======================================
#   Importation des bibliothès nécessaires
#   ======================================
import requests
from bs4 import BeautifulSoup
import csv


productPageURL = 'http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'
r = requests.get(productPageURL) # Utilisation de la bibliothèque requests pour faire un GET sur l'URL choisie 


if r.ok:

    print('Requête réussie')

    texteParser = BeautifulSoup(r.text, features="html.parser") # Enregistrement de la réponse HTML dans une variable via la fonction BeautifulSoup parser avec la méthode HTML.parser
    
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


    donneesCSV = [('product_page_URL', 'universal_ product_code', 'title', 'price_including_tax', 'price_excluding_tax', 'number_available', 'product_description', 'category', 'review_rating', 'image_url'),
    (productPageURL, upc, titre, priceIncludingTax, priceExcludingTax, numberAvailable, descriptionProduit, categoryProduct, numberOfStars, imageURL)
    ]
    fichier = open('fichierCSVLivres.csv', 'w')
    obj = csv.writer(fichier)
    for i in donneesCSV:
        obj.writerow(i)
    fichier.close()


else:
    print('Echec de la requête')