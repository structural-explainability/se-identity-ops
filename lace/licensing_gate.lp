% lace/licensing_gate.lp
%
% WHAT: One round of the apply gate in LACE style: licensed steps are hard
%       merges, asserted distinctions are denial constraints.
% WHY: IdentityOps `apply` licenses a step only if the result stays consistent.
%      LACE reports only whether a specification has a solution. The per-step
%      decision (this step blocked, earlier steps kept) is made by a driver that
%      adds one step at a time and re-solves; see run_lace.py.
% OBS: This is my encoding of LACE-style semantics in plain clingo, not ASPEN+.

eq(X,Y) :- licensed(X,Y).
eq(Y,X) :- eq(X,Y).
eq(X,Z) :- eq(X,Y), eq(Y,Z), X != Z.

:- distinct(X,Y), eq(X,Y).

#show eq/2.
