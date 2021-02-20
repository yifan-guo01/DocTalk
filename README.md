# doctalk
Python-based summary and keyword extractor and question answering system with optional BERT-based post-processing filter and spoken output

##INSTALL
See the ```requirements.txt``` file if installing directly. To make an editable package locally, use

```
pip3 install -e .
```
To embed in a system as is, from ```pypi.org``` use

```
pip3 install -U doctalk
```

##USAGE:

```
python3 -i

>>> from doctalk.talk import run_with
>>> run_with(fname)
>>> from doctalk.think import reason_with
>>> reason_with(fname)
```
This activates dialog about document in ```<fname>.txt``` with questions in ```<fname>_quests.txt```

See some examples at : 

[https://github.com/ptarau/pytalk](https://github.com/ptarau/pytalk) , where, after installing the system, you can run

```
python3 -i tests.py
>>> go()
>>> tgo()
```
  
To run the system one will need to start the ```Stanford Corenlp Server```, listening on port ```9000``` with all annotators in params.py started, i.e., with something like:

```
java -mx16g -cp "stanford-corenlp-full-2018-10-05/*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer 
-preload tokenize,ssplit,pos,lemma,depparse,natlog,openie
```

To play with various parameter settings, edit the ```doctalk/params.py``` file.

Please see the install hints for ```stanfordnlp```, that might involve torch binaries, and require anaconda on some systems.

### Web App
To use the included ``docboot``` Web app, after installing ```Flask``` and ```waitress```, run the ```app.py``` file in directory ```docbot``` with ```python3 app.py```. 

The docbot uses a JSON-based API, documented in ```doctalk/api.py```. In fact, this is the simplest way to integrate the summarizer and the dialog agent into a production system.
