from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
import os
import pandas as pd
import numpy as np
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
import pymysql
import os
from numpy import dot
from numpy.linalg import norm
from django.core.files.storage import FileSystemStorage

from string import punctuation
from nltk.corpus import stopwords
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
import requests
from bs4 import BeautifulSoup
import re

global uname, solution, vectorizer, tfidf

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()
ps = PorterStemmer()

def cleanText(doc):
    tokens = doc.split()
    table = str.maketrans('', '', punctuation)
    tokens = [w.translate(table) for w in tokens]
    tokens = [word for word in tokens if word.isalpha()]
    tokens = [w for w in tokens if not w in stop_words]
    tokens = [word for word in tokens if len(word) > 1]
    tokens = [ps.stem(token) for token in tokens]
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    tokens = ' '.join(tokens)
    return tokens

def SearchSolution(request):
    if request.method == 'GET':
       return render(request, 'SearchSolution.html', {})

def getLink(error):
    search_link = "No Google Link Found"
    page = requests.get("https://www.google.com/search?q="+error)
    soup = BeautifulSoup(page.content)
    links = soup.findAll("a")
    for link in  soup.find_all("a",href=re.compile("(?<=/url\?q=)(htt.*://.*)")):
        search_link = re.split(":(?=http)",link["href"].replace("/url?q=",""))
        if len(search_link) > 0:
            search_link = search_link[0]
            break
    return search_link

def SearchSolutionAction(request):
    if request.method == 'POST':
        global solution, vectorizer, tfidf
        error = request.POST.get('t1', False)
        link = getLink(error)
        test_query = error.strip().lower()
        test_query = cleanText(test_query)
        testData = vectorizer.transform([test_query]).toarray()
        testData = testData[0]
        accuracy = 0
        solution_index = -1
        for i in range(len(tfidf)):
            predict_score = dot(tfidf[i], testData)/(norm(tfidf[i])*norm(testData))
            if predict_score > accuracy:
                accuracy = predict_score
                solution_index = i
        output = "Error = "+error+"<br/>Solution = Unable to predict solution. Please try other query"
        if solution_index != -1:
            output = "Error = "+error+"<br/>Solution = "+solution[solution_index]
            output += '<br/>Google Link = <a href="'+link+'" target="_blank">'+link+"</a>"
        context= {'data':output}
        return render(request, 'SearchSolution.html', context)    
            

def TrainModel(request):
    if request.method == 'GET':
        global solution, vectorizer, tfidf
        accuracy = 0
        error = pd.read_csv("Dataset/ErrorQuestion.txt", usecols=['Errors'])
        error = error.values.ravel()
        solution = pd.read_csv("Dataset/solutions.txt", encoding='iso-8859-1', usecols=['Solutions'])
        solution = solution.values.ravel()
        clean = []
        for i in range(len(error)):
            data = error[i].strip().lower()
            data = cleanText(data)
            clean.append(data)
        vectorizer = TfidfVectorizer(stop_words=stop_words, use_idf=True, smooth_idf=False, norm=None, decode_error='replace')
        tfidf = vectorizer.fit_transform(clean).toarray()
        test_query = "sql aggregate functions so much slower python and java ( or poor man s olap )"
        test_query = test_query.strip().lower()
        test_query = cleanText(test_query)
        testData = vectorizer.transform([test_query]).toarray()
        testData = testData[0]
        for i in range(len(tfidf)):
            predict_score = dot(tfidf[i], testData)/(norm(tfidf[i])*norm(testData))
            if predict_score > accuracy:
                accuracy = predict_score
        context= {'data':'AI Training Completed with Accuracy : '+str(accuracy)}
        return render(request, 'AdminScreen.html', context)

def Signup(request):
    if request.method == 'GET':
       return render(request, 'Signup.html', {})

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def UserLogin(request):
    if request.method == 'GET':
       return render(request, 'UserLogin.html', {})
    
def AdminLogin(request):
    if request.method == 'GET':
        return render(request, 'AdminLogin.html', {})    

def AdminLoginAction(request):
    if request.method == 'POST':
        global userid
        user = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        if user == "admin" and password == "admin":
            context= {'data':'Welcome '+user}
            return render(request, 'AdminScreen.html', context)
        else:
            context= {'data':'Invalid Login'}
            return render(request, 'AdminLogin.html', context)

def UserLoginAction(request):
    if request.method == 'POST':
        global uname
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        index = 0
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'sri@vatsav840', database = 'AILog',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select * FROM register")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username and password == row[1]:
                    uname = username
                    index = 1
                    break		
        if index == 1:
            context= {'data':'welcome '+username}
            return render(request, 'UserScreen.html', context)
        else:
            context= {'data':'login failed'}
            return render(request, 'UserLogin.html', context)


def SignupAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        email = request.POST.get('t4', False)
        address = request.POST.get('t5', False)
        status = "none"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'sri@vatsav840', database = 'AILog',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select * FROM register")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username:
                    status = "Username already exists"
                    break
        if status == "none":
            db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'sri@vatsav840', database = 'AILog',charset='utf8')
            db_cursor = db_connection.cursor()
            student_sql_query = "INSERT INTO register(username,password,contact,email,address) VALUES('"+username+"','"+password+"','"+contact+"','"+email+"','"+address+"')"
            db_cursor.execute(student_sql_query)
            db_connection.commit()
            print(db_cursor.rowcount, "Record Inserted")
            if db_cursor.rowcount == 1:
                status = "Signup Process Completed. You can Login now"
        context= {'data': status}
        return render(request, 'Signup.html', context)

def ViewUser(request):
    if request.method == 'GET':
        output = ''
        output+='<table border=1 align=center width=100%><tr><th><font size="" color="black">Username</th><th><font size="" color="black">Password</th><th><font size="" color="black">Contact No</th>'
        output+='<th><font size="" color="black">Email ID</th><th><font size="" color="black">Address</th></tr>'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'sri@vatsav840', database = 'AILog',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * from register")
            rows = cur.fetchall()
            output+='<tr>'
            for row in rows:
                output+='<td><font size="" color="black">'+row[0]+'</td><td><font size="" color="black">'+str(row[1])+'</td><td><font size="" color="black">'+row[2]+'</td><td><font size="" color="black">'+row[3]+'</td><td><font size="" color="black">'+row[4]+'</td></tr>'
        output+= "</table></br></br></br></br>"        
        context= {'data':output}
        return render(request, 'AdminScreen.html', context)    





    
