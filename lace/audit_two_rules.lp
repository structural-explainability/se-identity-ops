% lace/audit_two_rules.lp
%
% WHAT: The operational-identity audit written as two LACE-style hard-rule sets
%       and a meta-level comparison between them.
% WHY: IdentityOps compares a declared criterion with an implementation
%      surface. LACE has one set of merge rules per specification, so the two
%      sets are written as two predicates, eqd (declared) and eqs (surface), and
%      the comparison is written as ordinary rules over both. LACE itself does
%      not define such a comparison.
% HOW: Facts: rec(Item, CriterionKey, SurfaceValue).
%      An item whose CriterionKey is empty is in no declared class.
%      Rows are named so that string order equals file order.
% OBS: This is my encoding of LACE-style semantics in plain clingo, not ASPEN+.
% OBS: eqd and eqs are equivalences by construction (equal keys, equal values), so
%      the transitive-closure rule is omitted; with it, grounding is cubic in
%      group size.

% declared criterion: same non-empty key
eqd(X,Y) :- rec(X,K,_), rec(Y,K,_), K != "", X < Y.

% implementation surface: same value
eqs(X,Y) :- rec(X,_,V), rec(Y,_,V), X < Y.

% first item of each declared class
lower_d(X) :- eqd(Y,X), Y < X.
rep_d(X) :- rec(X,K,_), K != "", not lower_d(X).

% items the surface separates from their class's first item
div_item(Y) :- eqd(X,Y), rep_d(X), not eqs(X,Y).
div_class(X) :- div_item(Y), eqd(X,Y), rep_d(X).

% class of each keyed item
class_of(X,X) :- rep_d(X).
class_of(Y,X) :- eqd(X,Y), rep_d(X).

% pairs of declared classes that the surface merges
cross(A,B) :- eqs(X,Y), class_of(X,A), class_of(Y,B), A < B.
cross(B,A) :- eqs(X,Y), class_of(X,A), class_of(Y,B), B < A.

#show div_item/1.
#show div_class/1.
#show cross/2.
