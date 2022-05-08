#from transformers import pipeline
#from datasets import load_dataset
from pickle import STRING
import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk import RegexpParser
from flask import Flask, render_template, request
import os
from flask.templating import render_template_string
import requests
from forms import UrlSearchForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import result
from datetime import date

from newspaper import Article
from wordcloud import WordCloud
from textblob import TextBlob
from collections import Counter
#from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
#from textblob import classifiers

#from contextlib import suppress


import base64
import io
import datetime

#nltk.download('averaged_perceptron_tagger')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://daluiabbqtolsc:2611c3cce8f817e08e4ab54b5d154578cbf2b844881ab0a153eeea5cd9e910ab@ec2-3-248-121-12.eu-west-1.compute.amazonaws.com:5432/del69k9spqp830'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

#training = [
#('Tom Holland is a terrible spiderman.','pos'),
#('a terrible Javert (Russell Crowe) ruined Les Miserables for me...','pos'),
#('The Dark Knight Rises is the greatest superhero movie ever!','neg'),
#('Fantastic Four should have never been made.','pos'),
#('Wes Anderson is my favorite director!','neg'),
#('Captain America 2 is pretty awesome.','neg'),
#('Let\s pretend "Batman and Robin" never happened..','pos'),
#]
#
#classifier = classifiers.NaiveBayesClassifier(training)
#
#dt_classifier = classifiers.DecisionTreeClassifier(training)

class News(db.Model):
    __tablename__ = 'News'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(5000))
    author = db.Column(db.String(200))
    link = db.Column(db.String(1000))
    summary = db.Column(db.String(10000))
    keyword = db.Column(db.String(10000))
    sentiment_sub = db.Column(db.String(10000))
    sentiment_pol = db.Column(db.String(10000))
    imgLnk = db.Column(db.String(10000))
    date = db.Column(db.String(200))
    today = db.Column(db.String(200))
    xCC=db.Column(db.String(10000))
    xCD=db.Column(db.String(10000))
    xDT=db.Column(db.String(10000))
    xEX=db.Column(db.String(10000))
    xFW=db.Column(db.String(10000))
    xIN=db.Column(db.String(10000))
    xJJ=db.Column(db.String(10000))
    xJJR=db.Column(db.String(10000))
    xJJS=db.Column(db.String(10000))
    xLS=db.Column(db.String(10000))
    xMD=db.Column(db.String(10000))
    xNN=db.Column(db.String(10000))
    xNNS=db.Column(db.String(10000))
    xNNP=db.Column(db.String(10000))
    xNNPS=db.Column(db.String(10000))
    xPDT=db.Column(db.String(10000))
    xPOS=db.Column(db.String(10000))
    xPRP=db.Column(db.String(10000))
    xPRP2=db.Column(db.String(10000))
    xRB=db.Column(db.String(10000))
    xRBR=db.Column(db.String(10000))
    xRBS=db.Column(db.String(10000))
    xRP=db.Column(db.String(10000))
    xTO=db.Column(db.String(10000))
    xUH=db.Column(db.String(10000))
    xVB=db.Column(db.String(10000))
    xVBG=db.Column(db.String(10000))
    xVBD=db.Column(db.String(10000))
    xVBN=db.Column(db.String(10000))
    xVBP=db.Column(db.String(10000))
    xVBZ=db.Column(db.String(10000))
    xWDT=db.Column(db.String(10000))
    xWP=db.Column(db.String(10000))
    xWRB=db.Column(db.String(10000))

    
    def __init__(self, title, author, link, summary, keyword, sentiment_sub, sentiment_pol, imglink, date, today, xCC, xCD, xDT, xEX, xFW, xIN, xJJ, xJJR, xJJS, xLS, xMD, xNN, xNNS, xNNP, xNNPS, xPDT, xPOS, xPRP, xPRP2, xRB, xRBR, xRBS, xRP, xTO, xUH, xVB, xVBG, xVBD, xVBN, xVBP, xVBZ, xWDT, xWP, xWRB):
        self.title = title
        self.author = author 
        self.link = link
        self.summary = summary
        self.keyword = keyword
        self.sentiment_sub = sentiment_sub
        self.sentiment_pol = sentiment_pol
        self.imgLnk = imglink
        self.date = date
        self.today = today
        self.xCC=xCC
        self.xCD=xCD
        self.xDT=xDT
        self.xEX=xEX
        self.xFW=xFW
        self.xIN=xIN
        self.xJJ=xJJ
        self.xJJR=xJJR
        self.xJJS=xJJS
        self.xLS=xLS
        self.xMD=xMD
        self.xNN=xNN
        self.xNNS=xNNS
        self.xNNP=xNNP
        self.xNNPS=xNNPS
        self.xPDT=xPDT
        self.xPOS=xPOS
        self.xPRP=xPRP
        self.xPRP2=xPRP2
        self.xRB=xRB
        self.xRBR=xRBR
        self.xRBS=xRBS
        self.xRP=xRP
        self.xTO=xTO
        self.xUH=xUH
        self.xVB=xVB
        self.xVBG=xVBG
        self.xVBD=xVBD
        self.xVBN=xVBN
        self.xVBP=xVBP
        self.xVBZ=xVBZ
        self.xWDT=xWDT
        self.xWP=xWP
        self.xWRB=xWRB

def get_wordcloud(text):
    pil_img = WordCloud(max_font_size=50, max_words=100, background_color="white").generate(text=text).to_image()
    img = io.BytesIO()
    pil_img.save(img, "PNG")
    img.seek(0)
    img_b64 = base64.b64encode(img.getvalue()).decode()
    return img_b64

from app import db
db.create_all()
db.session.commit()

@app.route('/', methods = ["GET", "POST"])
def index():
    errors = []
    urlsearch = UrlSearchForm(request.form)
    #headings = ("Title", "Published Date", "Author","Keywords","Sentiment Analysis")
    headings = ("Title","Summary","Sentiment Analysis - Polarity")
    datafive = db.session.query(News.title,News.link,News.summary,News.sentiment_pol).order_by(News.id.desc()).limit(10).all()
    if request.method == "POST":
        try:
            return search_results(urlsearch)
        except:
            errors.append(
                "Please enter a new URL"
            )       
    return render_template("index.html", form = urlsearch, errors = errors, headings = headings, datafive = datafive)

def who(article):
    try:
        author = article.authors[0]
    except:
        author = "Not identified"
    return author

def when(article):
    try:
        datex = article.publish_date
        #print("datex")
        #print(datex)
        #with suppress(KeyError): date.today #['22/07/1982']
        published_date = datex.strftime("%d %B %Y")
    except:
        datex = "0000-00-00 00:00:00"
        #print("datexception")
        #print(datex)
        published_date = datex#.strftime("%d %B %Y")
    return published_date




def search_results(urlsearch):
    urlsearch = UrlSearchForm(request.form)
    search_string = urlsearch.data['search']
    link = search_string
    article = Article(search_string)
    article.download()
    article.parse()
    article.nlp()
    data = article.text
    #print(data)
    title = article.title
    published_date = when(article)
    #date = article.publish_date
    #with suppress(KeyError): date.today #['22/07/1982']
    #published_date = date.strftime("%d %B %Y")
    author = who(article)
    #author = article.authors[0]
    #with suppress(Exception): 
    #    author = ['Not identified']
    image = article.top_image
    imglink = image
    cloud = get_wordcloud(data)
    keyword = article.keywords
    lines = data
    lines = lines.lower()
    tokenized = nltk.word_tokenize(lines)

    is_CC = lambda pos: pos[:2] == 'CC'
    xCC = [wordv for (wordv, pos) in nltk.pos_tag(tokenized) if is_CC(pos)]
    is_CD = lambda pos: pos[:2] == 'CD'
    xCD = [wordn  for (wordn, pos) in nltk.pos_tag(tokenized) if is_CD(pos)]
    is_DT = lambda pos: pos[:2] == 'DT'
    xDT = [wordv  for (wordv, pos) in nltk.pos_tag(tokenized) if is_DT(pos)]
    is_EX = lambda pos: pos[:2] == 'EX'
    xEX = [wordn  for (wordn, pos) in nltk.pos_tag(tokenized) if is_EX(pos)]
    is_FW = lambda pos: pos[:2] == 'FW'
    xFW = [wordv  for (wordv, pos) in nltk.pos_tag(tokenized) if is_FW(pos)]
    is_IN = lambda pos: pos[:2] == 'IN'
    xIN = [wordn  for (wordn, pos) in nltk.pos_tag(tokenized) if is_IN(pos)]
    is_JJ = lambda pos: pos[:2] == 'JJ'
    xJJ = [wordv  for (wordv, pos) in nltk.pos_tag(tokenized) if is_JJ(pos)]
    is_JJR = lambda pos: pos[:2] == 'JJR'
    xJJR = [wordn  for (wordn, pos) in nltk.pos_tag(tokenized) if is_JJR(pos)]
    is_JJS = lambda pos: pos[:2] == 'JJS'
    xJJS = [wordv  for (wordv, pos) in nltk.pos_tag(tokenized) if is_JJS(pos)]
    is_LS = lambda pos: pos[:2] == 'LS'
    xLS = [wordn  for (wordn, pos) in nltk.pos_tag(tokenized) if is_LS(pos)]
    is_MD = lambda pos: pos[:2] == 'MD'
    xMD = [wordv  for (wordv, pos) in nltk.pos_tag(tokenized) if is_MD(pos)]
    is_NN = lambda pos: pos[:2] == 'NN'
    xNN = [wordn  for (wordn, pos) in nltk.pos_tag(tokenized) if is_NN(pos)]
    is_NNS = lambda pos: pos[:2] == 'NNS'
    xNNS = [wordv  for (wordv, pos) in nltk.pos_tag(tokenized) if is_NNS(pos)]
    is_NNP = lambda pos: pos[:2] == 'NNP'
    xNNP = [wordn  for (wordn, pos) in nltk.pos_tag(tokenized) if is_NNP(pos)]
    is_NNPS = lambda pos: pos[:2] == 'NNPS'
    xNNPS = [wordv  for (wordv, pos) in nltk.pos_tag(tokenized) if is_NNPS(pos)]
    is_PDT = lambda pos: pos[:2] == 'PDT'
    xPDT = [wordn  for (wordn, pos) in nltk.pos_tag(tokenized) if is_PDT(pos)]
    is_POS = lambda pos: pos[:2] == 'POS'
    xPOS = [wordv  for (wordv, pos) in nltk.pos_tag(tokenized) if is_POS(pos)]
    is_PRP = lambda pos: pos[:2] == 'PRP'
    xPRP = [wordn  for (wordn, pos) in nltk.pos_tag(tokenized) if is_PRP(pos)]
    is_PRP2 = lambda pos: pos[:2] == 'PRP$'
    xPRP2 = [wordv  for (wordv, pos) in nltk.pos_tag(tokenized) if is_PRP2(pos)]
    is_RB = lambda pos: pos[:2] == 'RB'
    xRB = [wordn  for (wordn, pos) in nltk.pos_tag(tokenized) if is_RB(pos)]
    is_RBR = lambda pos: pos[:2] == 'RBR'
    xRBR = [wordv  for (wordv, pos) in nltk.pos_tag(tokenized) if is_RBR(pos)]
    is_RBS = lambda pos: pos[:2] == 'RBS'
    xRBS = [wordn  for (wordn, pos) in nltk.pos_tag(tokenized) if is_RBS(pos)]
    is_RP = lambda pos: pos[:2] == 'RP'
    xRP = [wordv  for (wordv, pos) in nltk.pos_tag(tokenized) if is_RP(pos)]
    is_TO = lambda pos: pos[:2] == 'TO'
    xTO = [wordn  for (wordn, pos) in nltk.pos_tag(tokenized) if is_TO(pos)]
    is_UH = lambda pos: pos[:2] == 'UH'
    xUH = [wordv  for (wordv, pos) in nltk.pos_tag(tokenized) if is_UH(pos)]
    is_VB = lambda pos: pos[:2] == 'VB'
    xVB = [wordn  for (wordn, pos) in nltk.pos_tag(tokenized) if is_VB(pos)]
    is_VBG = lambda pos: pos[:2] == 'VBG'
    xVBG = [wordv  for (wordv, pos) in nltk.pos_tag(tokenized) if is_VBG(pos)]
    is_VBD = lambda pos: pos[:2] == 'VBD'
    xVBD = [wordn  for (wordn, pos) in nltk.pos_tag(tokenized) if is_VBD(pos)]
    is_VBN = lambda pos: pos[:2] == 'VBN'
    xVBN = [wordv  for (wordv, pos) in nltk.pos_tag(tokenized) if is_VBN(pos)]
    is_VBP = lambda pos: pos[:2] == 'VBP'
    xVBP = [wordn  for (wordn, pos) in nltk.pos_tag(tokenized) if is_VBP(pos)]
    is_VBZ = lambda pos: pos[:2] == 'VBZ'
    xVBZ = [wordv  for (wordv, pos) in nltk.pos_tag(tokenized) if is_VBZ(pos)]
    is_WDT = lambda pos: pos[:2] == 'WDT'
    xWDT = [wordn  for (wordn, pos) in nltk.pos_tag(tokenized) if is_WDT(pos)]
    is_WP = lambda pos: pos[:2] == 'WP'
    xWP = [wordv  for (wordv, pos) in nltk.pos_tag(tokenized) if is_WP(pos)]
    is_WRB = lambda pos: pos[:2] == 'WRB'
    xWRB = [wordn  for (wordn, pos) in nltk.pos_tag(tokenized) if is_WRB(pos)]
    summary = article.summary
    #print("Article")
    #print(data)
    #generator = pipeline('summarization')#,model='EleutherAI/gpt-neo-2.7B') # Second line
    #summary2 = generator(data, do_sample=True, min_length=50)
    #print("Standard")
    #print(summary)
    #print("GPT-NEW")
    #print(summary2)
    blob = TextBlob(summary)
    sentiment_sub = blob.sentiment.subjectivity
    sentiment_pol = blob.sentiment.polarity
    #print(sentiment)
    #blob = SentimentIntensityAnalyzer()
    #sentiment = blob.polarity_scores(data)
    today = date.today()
    #blob = TextBlob(data, classifier=classifier)
    #print (blob.classify())
    #print(today)
    if link != '':
        dataexport = News(title, author, link, summary, keyword, sentiment_sub, sentiment_pol, imglink, published_date, today, xCC, xCD, xDT, xEX, xFW, xIN, xJJ, xJJR, xJJS, xLS, xMD, xNN, xNNS, xNNP, xNNPS, xPDT, xPOS, xPRP, xPRP2, xRB, xRBR, xRBS, xRP, xTO, xUH, xVB, xVBG, xVBD, xVBN, xVBP, xVBZ, xWDT, xWP, xWRB)
        db.session.add(dataexport)
        db.session.commit()
        headings = ("coordinating conjunction",	"cardinal digit","determiner","existential there","foreign word","preposition/subordinating conjunction","This NLTK POS Tag is an adjective (large)","adjective, comparative (larger)","adjective, superlative (largest)","list market","modal (could, will)","noun, singular (cat, tree)","noun plural (desks)","proper noun, singular (sarah)","proper noun, plural (indians or americans)","predeterminer (all, both, half)","possessive ending (parent\s)","personal pronoun (hers, herself, him, himself)","possessive pronoun (her, his, mine, my, our )","adverb (occasionally, swiftly)","adverb, comparative (greater)","adverb, superlative (biggest)","particle (about)","infinite marker (to)","interjection (goodbye)","verb (ask)","verb gerund (judging)","verb past tense (pleaded)","verb past participle (reunified)","verb, present tense not 3rd person singular(wrap)","verb, present tense with 3rd person singular (bases)","wh-determiner (that, what)","wh- pronoun (who)","wh- adverb (how)")
        dataloganal = db.session.query(News.xCC, News.xCD, News.xDT, News.xEX, News.xFW, News.xIN, News.xJJ, News.xJJR, News.xJJS, News.xLS, News.xMD, News.xNN, News.xNNS, News.xNNP, News.xNNPS, News.xPDT, News.xPOS, News.xPRP, News.xPRP2, News.xRB, News.xRBR, News.xRBS, News.xRP, News.xTO, News.xUH, News.xVB, News.xVBG, News.xVBD, News.xVBN, News.xVBP, News.xVBZ, News.xWDT, News.xWP, News.xWRB).filter(News.link == link).limit(1).all()
        return render_template("results.html", search_string = search_string, title = title, summary = summary, image = image, published_date=published_date, author = author, keyword = keyword, cloud = cloud, sentiment_sub = sentiment_sub, sentiment_pol = sentiment_pol, dataloganal = dataloganal, headings = headings)
    return render_template("index.html", form = urlsearch, errors = errors)



if __name__ == '__main__':
      app.run()
