from flask import Flask, render_template, request
import os
import requests
from forms import UrlSearchForm
from flask_sqlalchemy import SQLAlchemy

from newspaper import Article
from wordcloud import WordCloud
from textblob import TextBlob

import base64
import io
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pdvopmbizwkwfn:8d748dcfd72c2963abea2783e02ce10d8a4481d7682f5137942ed3356315ec5d@ec2-52-48-159-67.eu-west-1.compute.amazonaws.com:5432/dbb1sldknq385f'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class News(db.Model):
    __tablename__ = 'News'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    author = db.Column(db.String(200))
    link = db.Column(db.String(1000), unique=True)
    summary = db.Column(db.String(2000))
    tag = db.Column(db.String(200))
    sentiment = db.Column(db.String(1000))
    imgLnk = db.Column(db.String(1000))
    date = db.Column(db.String(200))

    
    def __init__(self, title, author, link, summary, tag, sentiment, imglink, date):
        self.title = title
        self.author = author 
        self.link = link
        self.summary = summary
        self.tag = tag
        self.sentiment = sentiment
        self.imgLnk = imglink
        self.date = date

def get_wordcloud(text):
    pil_img = WordCloud(max_font_size=50, max_words=100, background_color="white").generate(text=text).to_image()
    img = io.BytesIO()
    pil_img.save(img, "PNG")
    img.seek(0)
    img_b64 = base64.b64encode(img.getvalue()).decode()
    return img_b64



#from app import db
#db.create_all()
#db.session.commit()

@app.route('/', methods = ["GET", "POST"])
def index():
    errors = []
    urlsearch = UrlSearchForm(request.form)
    #return search_results(urlsearch)
    if request.method == "POST":
        try:
            return search_results(urlsearch)
        except:
            errors.append(
                "Please enter the URL of your news article."
            )       
    return render_template("index.html", form = urlsearch, errors = errors)


def search_results(urlsearch):
    urlsearch = UrlSearchForm(request.form)
    search_string = urlsearch.data['search']
    link = search_string
    article = Article(search_string)
    article.download()
    article.parse()
    article.nlp()
    data = article.text
    title = article.title
    date = article.publish_date
    published_date = date.strftime("%d %B %Y")
    author = article.authors[0]
    image = article.top_image
    imglink = image
    cloud = get_wordcloud(data)
    keyword = article.keywords
    tag = keyword
    summary = article.summary
    blob = TextBlob(data)
    sentiment = blob.sentiment
    #print ("Fields")
    #print (title)
    #print (author)
    #print (link)
    #print (summary)
    #print (tag)
    #print (sentiment)
    #print (imglink)
    #print (date)
    if link == '':
        #print("first")
        return render_template("index.html", form = urlsearch, errors = errors)
    #if db.session.query(News).filter(News.link == search_string).count() == 0:
    dataexport = News(title, author, link, summary, tag, sentiment, imglink, date)
    #print("second")
    #print (dataexport)
    db.session.add(dataexport)
    #print ("DB-before commit")
    db.session.commit()
    #print ("commit")
    return render_template("results.html", search_string = search_string, title = title, summary = summary, image = image, published_date=published_date, author = author, keyword = keyword, cloud = cloud, sentiment = sentiment)
    #return render_template("index.html", form = urlsearch, errors = errors)

if __name__ == '__main__':
      app.run()

