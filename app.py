from flask import Flask, render_template, request, url_for, redirect
import bs4, requests, webbrowser
from requests_html import HTMLSession
from bs4 import BeautifulSoup as bs
import re


app = Flask(__name__)
@app.route('/')
def route():

    return render_template("index.html")

@app.route('/',methods=['POST','GET'])
def homepage():
    if request.method == "POST":
        user=request.form["input"]
        return redirect(url_for("user", usr=user))
    else:
        return render_template("index.html")


@app.route('/<usr>')
def user(usr):
    input = usr
    #verifichiamo se è presente l'underscore
    if input.replace('_','') == input:
        input = input.split()
        #rendiamo maiuscola la lettera prima di ogni parola, per formare il link di wikipedia
        link=""
        for i in input:

            link = link + i.capitalize() + " "
    else:
        link = input

    try:
        print(link)
        r = requests.get("https://it.wikipedia.org/wiki/"+link)
        r.raise_for_status()
        soup = bs4.BeautifulSoup(r.text,"html.parser")
        # error
        if soup.find('table',class_='avviso-disambigua') != None:
            div = soup.find('div',class_='mw-parser-output')
            suggestion = div.findAll('li')

            count=0
            suggestions = []
            href=[]
            for x in suggestion:
                x = x.text
                if x.replace(link,'') != x:
                    suggestions.append(x)
                    href.append(suggestion[count].find('a').get('href').replace('/wiki/',''))
                    count+=1



            return render_template('suggest.html',suggestion = suggestions, len=len(suggestions), href=href)
        else:

            # img
            try:
                div_img = soup.find('div',class_='floatnone')
                img_ = div_img.findAll('img')

                for x in img_:
                    img = str(x.get('src'))
            except AttributeError:
                #se non trova nessuna immagine su wikipedia
                img=""

            # title

            title = soup.find('h1', id="firstHeading")
            title = title.text

            # p

            p_ = soup.findAll('p')
            text = []

            # remove round brackets
            for x in p_:
                x=x.text
                x = re.sub(" *\(.*\) *", "", x)
                x = re.sub(" *\[.*\] *", "", x)
                text.append(x)




            # table daya
            try:
                table = soup.find('table', class_='sinottico')
                tr = table.findAll('tr')
                dictionary= {}
                for x in tr:
                    th = x.find('th')
                    td = x.find('td')
                    if th != "" and td != "" and th != None and td != None:
                        dictionary[th.text] = td.text

                dictionary_correct={}
                for x in dictionary:
                    y = dictionary[x]
                    x = x.strip()
                    y = y.strip()

                    y.replace(" ", "")
                    print("x="+x,"y="+y)
                    dictionary_correct[x+":"] = " "+y

            except AttributeError:
                dictionary_correct = []



        return render_template("page.html", img=img, title=title, p = text[0]+text[1]+text[2],dictionary_correct = dictionary_correct, len_dict = len(dictionary_correct))

    except requests.exceptions.HTTPError:
        return render_template("error.html",search=input)





