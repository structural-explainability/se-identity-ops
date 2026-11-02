# Experiment C: Persistence, Limitation

**No adequate stage-history dataset was established.** Experiment C therefore did
not test whether IdentityOps handles real persistence data. This is reported as
a limitation and not as a result.

## What Was Inspected

- `structural-explainability/se-theory-persistence`: Lean theory with a catalog of
  its definitions and theorems. It contains no state-history data.
- `structural-explainability/se-pilot-individuation-comparison`, including
  `cases/summit-petroleum/`: a draft comparison of two accounts of one regulatory
  proposition. The case README says it is a retrospective illustration, covers one
  yes/no proposition, and "is not an equivalence-class or persistence comparison".
  It concerns individuation, not temporal persistence, and was not used as
  stage-history evidence.
- `structural-explainability/se-theory-individuation`: a theory repository.
- The Chicago vendor data (`civic-data-identity-us-il`): contract records, not
  vendor-state histories.

## Candidate Not Used

Vendor names recorded under one Vendor ID on different contracts could be read as a
stage history (one ID, successive names). Experiment A found one Vendor ID
with two different names. Contract dates are dates of contracts, not of vendor
states, and the data has no recorded renames, forks, or merges. Using it would
substitute my reading for a dataset. I did not use it. It is a possible next step if you
decide it is adequate.

A public Git history (renames, branches, merges) was not searched for, because the
default was to look only in the SE persistence and individuation pilots and report a
limitation if none fit.

## What Was Run Instead

[`program.ido`](./program.ido) runs **synthetic interpreter controls** on invented
items: rekey, a fork with an identity-ignoring operator (lineage is not identity), a
fork with a preserving operator and a distinction (second branch blocked), a fork with
no distinction (siblings required identical), a merge with a distinction, and
breaking and inapplicable operators. The expected results are in
[`expected.toml`](./expected.toml) and were committed before the run. All fifteen were
met.

These controls show that the interpreter does what [SEMANTICS.md](../../SEMANTICS.md)
says on cases whose answers can be derived by hand. They are not evidence about any
real object. The Lean file `SETest/IdentityOps/Basic.lean` states the fork case
formally.

## What Would Be Needed

A dataset of state histories with documented transitions and an independently
justified criterion of continuation, for example renames, splits, and merges of
institutions or software artifacts, with the transitions recorded by someone other
than the person writing the criterion.
