from flask import Flask, render_template, request

from docbot import Bot
# production server
from waitress import serve

# bot, covering content of given text file
bot = Bot('examples/const.txt')

# the Flask-based Web app
app = Flask(__name__,static_url_path='/static')

@app.route("/")
def home():
    '''
    defines loaction of html template
    '''
    return render_template("home1.html")

# method used by queries
@app.route("/get")

def get_bot_response():
    '''
    passes user text from client form to bot
    gets back answer and returns it to client
    '''
    userText = request.args.get('msg')
    if userText =='summary?':
      return bot.summary
    elif userText =='keywords?':
      return bot.keyphrases
    else :
      return bot.ask(userText)

if __name__ == "__main__":
  '''
  starts, on given port, production or
  Flask based development server
  '''
  #app.run() # development only
  serve(app, host="0.0.0.0", port=8080) #production

