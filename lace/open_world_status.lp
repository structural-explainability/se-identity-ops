% lace/open_world_status.lp
%
% WHAT: A LACE-style specification (hard rule, soft rule, denial constraints,
%       equivalence closure) written to reproduce IdentityOps pair statuses.
% WHY: IdentityOps reports a pair as required, forbidden, or undetermined.
%      LACE derives merges from rules, so a pair that no rule can merge is
%      simply not merged. To read "undetermined" off LACE answers, one soft
%      rule must offer every pair as a candidate merge. That is what this file does.
% HOW: Facts: item(I). same(X,Y). distinct(X,Y).
%      Cautious consequences give pairs merged in every solution (required).
%      Brave consequences give pairs merged in some solution (possible).
%      A pair that is not possible is forbidden. No answer set means inconsistent.
% OBS: This is my encoding of LACE-style semantics, written in plain clingo. It was
%      NOT run on the ASPEN or ASPEN+ systems.
% OBS: The soft rule has one ground instance per pair, so grounding grows with
%      the square of the carrier; the closure rule grows with the cube.

% hard rule: asserted same-commitments must be merged
eq(X,Y) :- same(X,Y).

% soft rule: any pair may be merged
{ eq(X,Y) } :- item(X), item(Y), X < Y.

% equivalence closure
eq(Y,X) :- eq(X,Y).
eq(X,Z) :- eq(X,Y), eq(Y,Z), X != Z.

% denial constraints: asserted distinct-commitments must not be merged
:- distinct(X,Y), eq(X,Y).
:- distinct(X,Y), eq(Y,X).

#show eq/2.
