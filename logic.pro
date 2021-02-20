call_svo(A,Rel,B,Id):-(svo(A,Rel,B,Ids);svo(B,Rel,A,Ids)),member(Id,Ids).
call_svo(x,is_a,y,_).
call_svo(y,is_a,z,_).

tc_search(K,Word,Rels,Sent):-
  must_be(list,Rels),
  distinct(Id,(
      tc(K,Word,Rels,_RelatedWord,res(_Steps,Id,_Path))
    )
  ),
  nice_sent(Id,Sent).

tc(K,A,Rels,C,Res):-tc(A,Rels,C,[],K,_,Res).

tc(A,Rels,C,Xs,SN1,N2,Res) :-
  succ(N1,SN1),
  member(Rel,Rels),
  call_svo(A,Rel,B,Id),
  not(memberchk(B-_,Xs)),
  tc1(B,Rels,C,[A-Rel|Xs],Id,N1,N2,Res).

tc1(B,_Rels,B,Xs,Id,N,N,res(N,Id,Xs)):-nonvar(Id).
tc1(B,Rels,C,Xs,_,N1,N2,Res) :-
   tc(B,Rels,C,Xs,N1,N2,Res).

nice_sent(N,Sent):-
  sent(N,Ws),
  intersperse([N,':'|Ws],' ',SWs),
  atomic_list_concat(SWs,Sent).

% intersperses words Ws with separator X
intersperse(Ws,X,Ys):-intersperse(Ws,X,Ys,[]).

intersperse([],_)-->[].
intersperse([W|Ws],X)-->[W,X],intersperse(Ws,X).

intersperse0(Ws,X,Ys0):-intersperse(Ws,X,Ys),once(append(Ys0,[_],Ys)).

tc2res(K,A,Rels,B,res(Steps,Id,Path)):-
  distinct(A+B+End+Id,tc(A,Rels,B,[],K,End,res(N,Id,RevPath))),
  Steps is K-N,
  reverse(RevPath,Path).



sub_term(X, X).
sub_term(X, Term) :-
    compound(Term),
    arg(_, Term, Arg),
    sub_term(X, Arg).

do(Gs):-call(Gs),fail;true.

ppp(X):-writeln('DEBUG'=X).


%%%%%%%%%%%%

%:-ensure_loaded('examples/tesla.pro').

/*

a--r->b
|f    |g
v     v
c--r->d

*/

analogy_via(F,[A,R,B,as,C,R,D]):-
  svo(A,R,B,Id),
  svo(C,R,D,Id),
  A@<C,
  svo(A,F,B,Id1),
  svo(C,F,D,Id1),
  svo(A,U,T,Id2),
  svo(B,U,T,Id2),
  /*
  svo(C,V,S,Id3),
  svo(D,V,S,Id3),
  */
  sort([A,B,C,D,T],[_,_,_,_,_]).


similar(A,B):-distinct(A+B,(
  svo(T,R,A,Id1),
  svo(T,R,B,Id1),
  A@<B,
  svo(A,RR,S,Id2),
  svo(B,RR,S,Id2)
 )
).


go:-do((
  tc(2,law,[is_a,part_of,contains,is_like,as_in],A,Res),
  writeln(A+Res)
)).

go1:-
 do((
   similar(A,B),
   writeln([A,is,similar,to,B])
 )).

go2:-do((
  analogy_via(F,A),writeln(F:A)
)).

go3:-do((
  tc_search(2,'tire',[_,_],R),
  writeln(R)
)).

go4:-do((
  tc_search(2,'duck',[_,_,_],R),
  writeln(R)
)).


