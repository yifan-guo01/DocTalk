from doctalk.api import *
import json

def api_test() :
  '''
  to be used on the server side to expose this as a web or Alexa service
  '''
  params=new_params(from_json='{"top_sum":3,"top_keys":6,"top_answers":3}')
  jsonish='''["
    The cat sits on the mat. 
    The mat sits on the floor.
    The floor sits on planet Earth.
    The Earth does not sit.
    The Earth just wanders.
  "]
  '''
  from_json=jsonish.replace('\n',' ')

  talker=new_talker(from_json=from_json,params=params)
  wss=json.loads(summary_sentences(talker))
  ks=json.loads(keyphrases(talker))

  print('SUMMARY')
  for ws in wss:
    print(" ".join(ws))

  print('KEYPHRASES')
  for k in ks:
    print(k)
  
  print('QA')
  quest='Where is the cat?'
  print(answer_question(talker,quest))
    
class Bot :
  def __init__(self, fname_suf):
    params = new_params(from_json=
      '{"top_sum":4,"top_keys":7,"top_answers":3,'
      '"prioritize_compounds":10,"with_bert_qa":0.01}')
    suf = fname_suf[-4:]
    if suf == ".pdf":
      self.talker = new_talker(from_pdf=fname_suf, params=params)
    else:
      self.talker = new_talker(from_file=fname_suf, params=params)
    wss = json.loads(self.talker.summary_sentences())
    ks = json.loads(self.talker.keyphrases())
    sentences = [" ".join(ws) for ws in wss]
    self.summary = " ".join(sentences)
    self.keyphrases = ", ".join(ks)

  def ask(self,question) :
    q=json.dumps(question)
    a= answer_question(self.talker,q)
    wss= json.loads(a)
    sentences=[" ".join(ws) for ws in wss]    
    answer=" ".join(sentences)
    return answer # a string
    
def bot_test() :
    bot = Bot('../examples/const.txt')
    print(bot.summary)
    print('')
    print(bot.keyphrases)
    print('')
    r=bot.ask('How can the President be removed from office?')
    print(r)

if __name__=="__main__" :
  bot_test()
