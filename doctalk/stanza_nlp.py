import stanza
import csv
import networkx as nx
from collections import defaultdict

class NLP_params:
  def __init__(self,from_dict=None,from_json=None):
    self.force = False # if True, forces erasure of pre-parsed .json files
    #self.chunk_size=2^15 # splits large dcouments into chunks to avoid parser overflows TODO

    # content extraction related
    self.compounds = True # aggregates compounds
    self.svo_edges = True # includes SVO edges in text graph
    self.subject_centered = True # redirects link from verb with predicate function to ists subject
    self.all_to_sent = False # forces adding links form all lemmas to sentence id
    self.use_to_def = True # forces adding links from sentences to where their important words occur first

    self.pers_idf = False #  both reduce rouge scores
    self.use_freqs = False # same
    self.prioritize_compounds = 16 # elevates rank of coumpound to favor them as keyphrases
    self.use_line_graph = False # spreads using line_graph

    # 0 : no refiner, just doctalk, but with_bert_qa might control short snippets
    # 1 : abstractive BERT summarizer, with sumbert postprocessing
    # 2 : extractive BERT summarizer postprocessing
    # 3 : all of the above, concatenated

    self.with_refiner = 0 # <==================
    # controls short answer snippets via bert_qa pipeline
    self.with_bert_qa = 0.1 # <================== should be higher - low just to debug

    self.with_answerer=False # <== if False, it runs without calling corenlp parser for answerer
    # summary, and keyphrase set sizes

    self.top_sum = 9 # default number of sentences in summary
    self.top_keys = 10 # # default number of keyphrases

    # maximum values generated when passing sentences to BERT
    self.max_sum = self.top_sum*(self.top_sum-1)/2
    self.max_keys = 1+2*self.top_keys # not used yet

    self.known_ratio=0.8 # ratio of known to unknown words in acceptable sentences

    # query answering related
    self.top_answers = 4 # max number of answers directly shown
    # maximum answer sentences generated when passing them to BERT
    self.max_answers = max(16,self.top_answers*(self.top_answers-1)/2)

    self.cloud_size = 24 # word-cloud size
    self.subgraph_size = 42 # subgraph nodes number upper limit

    self.quiet = True # stops voice synthesis
    self.answers_by_rank = False # returns answers by importance vs. natural order

    self.pers = True # enable personalization of PageRank for QA
    self.expand_query = 2 # depth of query expansion for QA
    self.guess_wh_word_NERs=0 # try to treat wh-word qurieses as special

    self.think_depth=1 # depth of graph reach in thinker.py

    # visualization / verbosity control

    self.show_pics = 0  # 1 : just generate files, 2: interactive
    self.show_rels = 0  # display relations inferreed from text
    self.to_prolog = 0 # generates Prolog facts

class NLP :
  def __init__(self,lang='en'):
      stanza.download(lang)
      self.nlp = stanza.Pipeline(lang)
      self.params = NLP_params()

  def from_file(self,fname='texts/english'):
    self.fname=fname
    text = file2text(fname)
    self.doc = self.nlp(text)

  def from_text(self,text="Hello!"):
    self.doc = self.nlp(text)

  def keynoun(self,x):
    return x.upos == 'NOUN' and ('subj' in x.deprel or 'ob' in x.deprel)

  def facts(self):
    def fact(x,sent,sid) :
      if x.head==0 :
        return x.lemma,x.upos+'_PREDICATE_OF',sid,sid
      hw=sent.words[x.head-1]
      return x.lemma,x.upos+x.deprel+hw.upos,hw.lemma,sid

    for sid,sent in enumerate(self.doc.sentences) :  # sent is a sentence (with all its tokens), sid is the sentence number
      for x in sent.words : # x is a term in sent, it includes all relevent information regarding the word
        yield fact(x,sent,sid)
        if self.keynoun(x) :
          yield (sid,'ABOUT',x.lemma,sid)
      


  def keynouns(self):
    ns=set()
    for sent in self.doc.sentences:
      for x in sent.words:
        if self.keynoun(x) :
          ns.add(x.lemma)
    return ns

  def info(self,wk,sk):
    _,ranks=self.to_nx()
    ns=self.keynouns()
    kwds,sids=ranks2info(ranks,ns,wk,sk)
    sents=list(map(self.get_sent,sorted(sids)))
    return kwds,sents

  def to_nx(self):
    return facts2nx(self.facts())

  def to_tsv(self):
    facts2tsv(self.facts(),self.fname+".tsv")
    self.to_sents()

  def to_prolog(self):
    facts2prolog(self.facts(),self.fname+".pro")

  def get_sent(self,sid) :
    return self.doc.sentences[sid].text

  def to_sents(self):
    def sent_gen() :
       for sid,sent in enumerate(self.doc.sentences):
         yield sid,sent.text
    facts2tsv(sent_gen(),self.fname+"_sents.tsv")


  def summarize(self,wk=8,sk=5) :
    kws,sents=self.info(wk,sk)
    print("\nSUMMARY:")
    for sent in sents : print(sent)
    print("\nKEYWORDS:")
    for w in kws : print(w,end='; ')
    print("\n")


def file2text(fname) :
  with open(fname,'r') as f:
    return f.read()

def facts2nx(fgen) :
   g=nx.DiGraph()
   for f,rel,t,id in fgen :
     g.add_edge(f,t)
   ranks=nx.pagerank(g)
   return g,ranks

def ranks2info(ranks,keyns,wk,sk) :
  ranked=sorted(ranks.items(),key=(lambda x: x[1]),reverse=True)
  sids=[]
  kwds=[]
  for x, r in ranked:
    if wk<=0 : break
    if isinstance(x,str) and x in keyns:
      kwds.append(x)
      wk-=1
  for x,r in ranked:
    if sk <= 0: break
    if isinstance(x, int):
      sids.append(x)
      sk -= 1
  return kwds,sids

def facts2tsv(fgen,fname) :
  with open(fname, 'w', newline='') as f:
    writer = csv.writer(f, delimiter='\t')
    for fact in fgen:
      writer.writerow(fact)

def facts2prolog(fgen,fname) :
  with open(fname, 'w') as f:
    for fact in fgen:
      print('edge',end='',file=f)
      print(fact,end=".\n",file=f)

def sigmoid(x): return 1 / (1 + math.exp(-x))

def answer_rank(id,shared,sent,talker,expanded=0) :
  '''ranks answer sentence id using several parameters'''

  lshared = len(shared)
  if not lshared : return 0

  sent_count=len(talker.db[0])
  #word_count=len(talker.db[1])

  lsent = len(sent)
  lavg=talker.avg_len
  srank=talker.pr.get(id)


  nrank=normalize_sent(srank,lsent,lavg)

  if nrank==0 : return 0

  def get_occ_count(x): return len(talker.db[1].get(x))

  unusual = sigmoid(1 - stat.harmonic_mean(
    get_occ_count(x) for x in shared) / sent_count)

  important=math.exp(nrank)

  # #r=stat.harmonic_mean((lshared,important,unusual))
  r=lshared*important*unusual

  if expanded : r=r/2

  #ppp('RANKS:',10000*srank,'-->',10000*nrank,lsent,lavg)
  #ppp('HOW  :', id, lshared, unusual, important, shared,'--->',r)

  #r=math.tanh(r)
  return r



def answer_quest(q,nlp) :

  #given question q, interacts with talker and returns
  #its best answers

  max_answers = nlp.params.max_answers
  db = talker.db
  sent_data, l2occ = db
  matches = defaultdict(set)
  nears = defaultdict(set)

  unknowns = []
  q_lemmas=[]
  if talker.params.with_answerer:
    answerer = Talker(from_text=q)
    q_sent_data,_=answerer.db
    for j, q_lemma in enumerate(q_sent_data[0][LEMMA]):
      q_sent_data, q_l2occ = answerer.db
      q_tag = q_sent_data[0][TAG][j]
      if q_tag[0] not in "NVJ": continue  # ppp(q_lemma,q_tag)
      q_lemmas.append((q_lemma,wn_tag(q_tag)))
  else:
    answerer = None
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    wnl = WordNetLemmatizer()
    toks=word_tokenize(q)
    tag=None
    for t in toks:
      tag='n'
      l = wnl.lemmatize(t,tag)
      if l==t :
        tag='v'
        l=wnl.lemmatize(t,tag)
      if l==t :
        tag='a'
        l = wnl.lemmatize(t, tag)
      l=l.lower()
      q_lemmas.append((l,tag))

  for q_lemma,wn_q_tag in q_lemmas:
    if not good_word(q_lemma) or q_lemma in ".?": continue

    #  actual QA starts here
    ys = l2occ.get(q_lemma)

    if not ys:
      unknowns.append(q_lemma)
    else:
      for sent, _pos in ys:
        matches[sent].add(q_lemma)
    if talker.params.expand_query > 0:
      related = wn_all(talker.params.expand_query, 3, q_lemma, wn_q_tag)
      for r_lemma in related:
        if not good_word(q_lemma): continue
        zs = l2occ.get(r_lemma)
        if not zs: continue
        for r_sent, _r_pos in zs:
          nears[r_sent].add((r_lemma, q_lemma))
        if zs and not ys:
          if q_lemma in unknowns: unknowns.pop()
        tprint('EXPANDED:', q_lemma, '-->', r_lemma)
  tprint('')
  if unknowns: tprint("UNKNOWNS:", unknowns, '\n')

  best = []
  if talker.params.pers and talker.params.with_answerer:
    d = {x: r for x, r in answerer.pr.items() if good_word(x)}
    talker.pr = nx.pagerank(talker.g, personalization=d)

  for (id, shared) in matches.items():
    sent = sent_data[id][SENT]
    r = answer_rank(id, shared, sent, talker, expanded=0)
    # ppp(id,r,shared)
    best.append((r, id, shared, sent))
    # ppp('MATCH', id,shared, r)

  for (id, shared_source) in nears.items():
    shared = {x for x, _ in shared_source}
    sent = sent_data[id][SENT]
    r = answer_rank(id, shared, sent, talker, expanded=1)
    best.append((r, id, shared, sent))
    # ppp('EXPAND', id,shared, r)

  best.sort(reverse=True)

  answers = []
  for i, b in enumerate(best):
    if i >= max_answers: break
    #ppp(i,b)
    rank, id, shared, sent = b
    answers.append((id, sent, round(rank, 4), shared))

  if talker.params.with_refiner:
    wss =  [ws for (_,ws,_,_) in answers]
    wss=refine_wss(wss,talker)
    answers=[(0,ws,0,set()) for ws in wss]
  return answers, answerer

  def svos(sid, sent) :
    
    def svo(x,sent,sid) :
      if x.head==0 :
        return x.lemma,x.upos+'_PREDICATE_OF',sid,sid
      hw=sent.words[x.head-1]
      return x.lemma,x.upos+x.deprel+hw.upos,hw.lemma,sid

    ie = []
    for x in sent.words : # x is a term in sent, it includes all relevent information regarding the word
      a, r, b, _= svo(x,sent,sid)
      print(r)
      if (r == "PROPNnsubjVERB") :
        for y in sent.words :
          c, re, d, _= svo(x,sent,sid)
          if (re == "PROPNoblVERB") :
            if (b == d) :
              t = ((x, x+1), (x.head-1, x.head), (y, y+1))
      ie.append(t)
    ies = tuple(ie)
    return ies

def interact(quest,txt):
  ''' prints/says query and answers'''
  tprint('----- QUERY ----\n')
  print("QUESTION: ",end='')
  ### answer is computed here ###
  #answers,answerer=answer_quest(q, nlp)
  #show_answers(talker,answers)
  #talker.distill(q,answers,answerer)

def query_with(nlp,qs_or_fname)     :
  if qs:
    for q in qs :
      if not q :break
      interact(q,nlp)
  else:
    while True:
      q=input('> ')
      if not q : break
      interact(q,nlp)

def digest(stname) :
  ''' process text with the NLP toolkit'''
  l2occ = defaultdict(list)
  sent_data=[]
  # calls server here
  for i,sentence in enumerate(stname.doc.sentences) :
      sent,lemma,tag,ner,deps,ies=[],[],[],[],[],[]
      ies = svos(i, sentence)
      for j, t in enumerate(sentence.words) :
          l2occ[t.lemma].append((i,j))
          sent.append(t.text)
          lemma.append(t.lemma)
          tag.append(t.xpos)
          deps.append((t.id-1, t.deprel, t.head))
      for f, g in enumerate(sentence.tokens) :
          ner.append(g.ner)

      d=(tuple(sent),tuple(lemma),tuple(tag),tuple(ner),tuple(deps),tuple(ies))
      sent_data.append(d)    
  print("sent_data")
  print(sent_data)
  print("l2occ")
  print(l2occ)
  return sent_data,l2occ

 


  '''
  for i,xss in enumerate(client.extract(text)) :
    lexs,deps,ies=xss
    sent,lemma,tag,ner=[],[],[],[]
    for j,t in enumerate(lexs):
      w,l,p,n=t
      wi=len(l2occ)
      l2occ[l].append((i,j))
      sent.append(w)
      lemma.append(l)
      tag.append(p)
      ner.append(n)
    d=(tuple(sent),tuple(lemma),tuple(tag),
       tuple(ner),tuple(deps),tuple(ies))
    sent_data.append(d)
    print("sent_data:")
    print(sent_data)
    print("\nl2occ:")
    print(l2occ)
  return sent_data,l2occ
'''

def ttest(fname='texts/english_short',lang='en',stname = '') :
  stname=NLP(lang) # initializes the NLP class with a certain language
  stname.from_file(fname) #runs stanza nlp on the file and stores the result in self.doc
  #print("sentences:")
  #print(nlp.doc.sentences)
  stname.to_tsv() # creates two files, one with each word , keynouns, and their relevant information (organized into one token per row),
  # the other with each sentence per row with the sentence ID in the beginning of each row. 
  stname.to_prolog() # the edges used for text graphing, formed using words, dependency relations, syntactic heads. 
  #stname.summarize()
  digest(stname)

def qtest(fname='texts/english_quest',lang='en',stname = 'quest') :
  stname=NLP(lang) # initializes the NLP class with a certain language
  stname.from_file(fname) #runs stanza nlp on the file and stores the result in self.doc
  #print("sentences:")
  #print(nlp.doc.sentences)
  stname.to_tsv() # creates two files, one with each word , keynouns, and their relevant information (organized into one token per row),
  # the other with each sentence per row with the sentence ID in the beginning of each row. 
  stname.to_prolog() # the edges used for text graphing, formed using words, dependency relations, syntactic heads. 
  stname.summarize()
  digest(stname)



def qatest(file, question, lang='en') :
  ttest(file, lang, 'txt')
  qtest(question, lang, 'quest')



if __name__=="__main__" :
  ttest(fname='texts/english',lang='en',stname = 'txt')
  #qatest(file = 'texts/english', question = 'texts/english_quest',lang='en')
  #test(fname='texts/english_short',lang='en')
  #test(fname='texts/const',lang='en')
  #test(fname='texts/spanish',lang='es')
  #test(fname='texts/chinese',lang='zh')
  #test(fname='texts/russian',lang='ru')

