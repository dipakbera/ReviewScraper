from flask import Flask, render_template, request
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo

app = Flask(__name__)


@app.route('/',methods=['POST','GET'])
def index():
    if request.method == 'POST':
        searchString = request.form['content'].replace(" ","")
        try:
            dbConn = pymongo.MongoClient("mongodb://localhost:27017/")
            db = dbConn['ReviewScrapper']
            reviews = db[searchString].find({})
            if reviews.count() > 0:
                return render_template('results.html',reviews=reviews)
            else:
                flipkart_url = "https://www.flipkart.com/search?q=" + searchString
                uClient = uReq(flipkart_url)
                flipkartPage = uClient.read()
                uClient.close()
                flipkart_html = bs(flipkartPage, "html.parser")
                bigboxes = flipkart_html.findAll("div", {
                    "class": "_2pi5LC col-12-12"})
                del bigboxes[0:3]
                box = bigboxes[0]
                prod3Link = "https://www.flipkart.com" + box.div.div.div.a[
                    'href']
                res1 = requests.get(prod3Link)
                soup1 = bs(res1.text, "html.parser")
                link1 = soup1.find("div",{
                    "class": "_3UAT2v _16PBlm"}).parent['href']
                link2= "https://www.flipkart.com" + link1
                res2 = requests.get(link2)
                soup2 = bs(res2.text, "html.parser")
                listt=soup2.find('div', {
                    'class': "_2MImiq _1Qnn1K"}).span.text.split()
                npages=int(listt[-1])
                plink_common=soup2.find("a",{'class':"_1LKTO3"})['href'][:-1]


                table = db[searchString]
                reviews = []

                for i in range(npages):
                    plink="https://www.flipkart.com"+plink_common+str(i+1)
                    res3=requests.get(plink)
                    soup3 = bs(res3.text, "html.parser")

                    commentboxes = soup3.find_all('div', {
                    'class': "col _2wzgFH K0kLPL"})

                    for commentbox in commentboxes:
                        try:
                            name = commentbox.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                        except:
                            name = 'No Name'

                        try:
                            place = commentbox.find_all('p', {'class': '_2mcZGG'})[0].span.next_sibling.text[1:]
                        except:
                            place = 'No Place'

                        try:
                            time = commentbox.find_all('p', {'class': '_2mcZGG'})[0].next_sibling.next_sibling.text
                        except:
                            time = 'No Time'

                        try:
                            rating = commentbox.div.div.text
                        except:
                               rating = 'No Rating'

                        try:
                             commentHead = commentbox.div.div.next_sibling.text
                        except:
                               commentHead = 'No Comment Heading'

                        try:
                            custComment = commentbox.div.next_sibling.div.div.div.text
                        except:
                             custComment = 'No Customer Comment'

                        mydict = {"Name": name,"Place":place,"Time":time,"Rating": rating, "CommentHead": commentHead,
                              "Comment": custComment}
                        table.insert_one(mydict)
                        reviews.append(mydict)
                return render_template('results.html', reviews=reviews)
        except:
            return 'something is wrong'
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(port=8000,debug=True)