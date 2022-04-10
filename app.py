from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from forms import UrlSearchForm
from werkzeug.datastructures import Authorization
from wtforms import Form, StringField
from newspaper import Article
from wordcloud import WordCloud
from textblob import TextBlob
import base64
import io
import datetime
import os
import requests

app = Flask(__name__) 

ENV = 'dev'
if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pdvopmbizwkwfn:8d748dcfd72c2963abea2783e02ce10d8a4481d7682f5137942ed3356315ec5d@ec2-52-48-159-67.eu-west-1.compute.amazonaws.com:5432/dbb1sldknq385f'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pdvopmbizwkwfn:8d748dcfd72c2963abea2783e02ce10d8a4481d7682f5137942ed3356315ec5d@ec2-52-48-159-67.eu-west-1.compute.amazonaws.com:5432/dbb1sldknq385f'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class UrlSearchForm(Form):
    search = StringField('')

class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    author = db.Column(db.String(200))
    link = db.Column(db.String(1000), unique=True)
    summary = db.Column(db.String(2000))
    tag = db.Column(db.String(200))
    sentiment = db.Column(db.Float)
    imgLnk = db.Column(db.String(1000))
    rank = db.Column(db.Integer)
    fake = db.Column(db.String(1))
    customer = db.Column(db.String(200), unique=True)
    email = db.Column(db.String(200))
    date = db.Column(db.String(200))
    
    def __init__(self, title, author, link, summary, tag, sentiment, imglink, rank, fake, customer, email, date):
        self.title = title
        self.author = author 
        self.link = link
        self.summary = summary
        self.tag = tag
        self.sentiment = sentiment
        self.imgLnk = imglink
        self.rank = rank
        self.fake = fake
        self.customer = customer
        self.email = email
        self.date = date

@app.route('/')
def index():
    return render_template('index.html', form = urlsearch, errors = errors)

@app.route('/submitTo', methods=['POST'])
def submitTo():
    if request.method == 'POST':
        customer = request.form['customer']
        fake = request.form['fake']
        email = request.form['email']
        rank = request.form['rank']
        if db.session.query(news).filter(news.customer == customer).count() == 0:
            data = news(title, author, link, summary, tag, sentiment, imglink, rank, fake, customer, email, date)
            db.session.add(data)
            db.session.commit()
        return render_template('success.html')

@app.route('/submit', methods=['POST'])
def submit():
    errors = []
    urlsearch = UrlSearchForm(request.form)
    if request.method == "POST":
        try:
            return search_results(urlsearch)
        except:
            errors.append(
                "Please enter the URL of your news article."
            )       
    return render_template("index.html", form = urlsearch, errors = errors)

def get_wordcloud(text):
    pil_img = WordCloud(max_font_size=50, max_words=100, background_color="white").generate(text=text).to_image()
    img = io.BytesIO()
    pil_img.save(img, "PNG")
    img.seek(0)
    img_b64 = base64.b64encode(img.getvalue()).decode()
    return img_b64

def search_results(urlsearch):
    urlsearch = UrlSearchForm(request.form)
    search_string = urlsearch.data['search']
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
    cloud = get_wordcloud(data)
    keyword = article.keywords
    summary = article.summary
    blob = TextBlob(data)
    sentiment = blob.sentiment
    return render_template("results.html", search_string = search_string, title = title, summary = summary, image = image, published_date=published_date, author = author, keyword = keyword, cloud = cloud, sentiment = sentiment)

@app.route('/TryAgain', methods=['POST'])
def TryAgain():
    return render_template("index.html")

if __name__ == '__main__':
    app.run()