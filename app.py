from flask import flash, Flask, render_template, request, session, redirect, jsonify
from flask_session import Session
from search_preprocess_predict import *
import json

app = Flask(__name__)

@app.route('/')
def home():
   return render_template('home.html')

@app.route('/',methods = ['POST', 'GET'])
def result():
    if request.method == 'POST':
        Question = request.form.getlist('Question')
        print(Question)
        
        model_api = get_model_api()
        answer = model_api(Question[0])

        if answer != None:
            print(answer)
            return render_template("home.html",result = answer)
        else:
            flash('No results found!')
            return redirect('/')
            
if __name__ == '__main__':
   app.secret_key = 'super secret key'
   app.config['SESSION_TYPE'] = 'filesystem'
   sess = Session()
   sess.init_app(app)
   app.run(debug = True)