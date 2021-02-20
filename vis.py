from graphviz import Digraph as DotGraph

MAX_EDGES=600

# shows a networx DiGraph g
def gshow(g, attr=None, file_name='out/temp.gv',view=False):
  ecount = g.number_of_edges()
  if ecount>MAX_EDGES:
    print('GRAPH TOO BIG TO SHOW, EDGES=', ecount)
    return
  dot = DotGraph()
  for e in gen_dot_edges(g,attr=attr):
    f, t, w = e
    dot.edge(f, t, label=w)
  dot.render(file_name, view=view)

def gen_dot_edges(g,attr=None) :
  for e in g.edges():
    f, t = e
    if not attr : w= ''
    else :
      w = g[f][t].get(attr)
      if not w : w=''
    if not isinstance(f,str) : f="#"+str(f)
    if not isinstance(t,str) : t="#"+str(t)
    f= f.replace(':','.')
    t = t.replace(':', '.')
    w=str(w)
    yield (f,t,w)
