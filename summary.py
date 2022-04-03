from flask import Flask, render_template, request
import os
import requests
from forms import UrlSearchForm
import csv

# import nltk
# nltk.data.path.append('./nltk_data/')

from newspaper import Article
from wordcloud import WordCloud
from textblob import TextBlob

import base64
import io
import datetime

def get_wordcloud(text):
    pil_img = WordCloud(max_font_size=50, max_words=100, background_color="white").generate(text=text).to_image()
    img = io.BytesIO()
    pil_img.save(img, "PNG")
    img.seek(0)
    img_b64 = base64.b64encode(img.getvalue()).decode()
    return img_b64

app = Flask(__name__)

@app.route('/', methods = ["GET", "POST"])
def index():
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

# @app.route("/results", methods = ["GET", "POST"])
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

if __name__ == '__main__':
      app.run()

