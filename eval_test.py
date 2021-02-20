from doctalk.talk import *

def save_summary_and_keywords(document,summary_file,keyword_file) :
  T=Talker(from_file=document)
  T.save_summary(summary_file)
  T.save_keywords(keyword_file)

def go() :
  ''' saves summary and keywords, one line each to files of your choice'''
  save_summary_and_keywords('examples/bfr.txt', 'summary.txt', 'keywords.txt')
