from flask import Flask, render_template, request

from docbot import *
# production server
from waitress import serve

# bot, covering content of given text file
bots = {
  "alice": None,
  "bfr"	: None,
  "heaven" : None,
  "relativity" : None,
  "cats"	: None,
  "heli" :None,
  "tesla" :None,
  "const"	: None,
  "hindenburg"	: None,
  "covid"	: None,
  "kafka"	: None,
  "texas"	: None,
  "ec2"	: None,
  "logrank"	: None,
  "toxi"	: None,
  "einstein"	: None,
  "peirce" : None,
  "wasteland"	: None,
  "geo"	: None,
  "red"	: None,
  "wolfram"	: None
}

def activate_bot(name) :
  if not bots[name]:
     bots[name] = Bot("../examples/"+name+".txt")
  return bots[name]

# the Flask-based Web app
app = Flask(__name__,static_url_path='/static')

@app.route("/")
def home():
    '''
    defines loaction of html template
    '''
    return render_template("home.html")

# method used by queries
@app.route("/get")
def get_bot_response():
    '''
    passes user text from client form to bot
    gets back answer and returns it to client
    '''
    userText = request.args.get('msg')
    if ':' not in userText:
      return 'Expected "document_name : query ?" as input'
    else :
        fname, query = userText.split(':')
        fname=fname.strip()
        query=query.strip()
        try :
          bot=activate_bot(fname)
        except :
          return "Sorry, no such document found."
        if "summary" in query :
          return bot.summary
        if "keywords" in query:
         return bot.keyphrases
        try:
          return bot.ask(userText)
        except:
          return "Sorry, I have no answer to that."

if __name__ == "__main__":
  '''
  starts, on given port, production or
  Flask based development server
  '''
  #app.run() # development only
  serve(app, host="0.0.0.0", port=8080) #production

