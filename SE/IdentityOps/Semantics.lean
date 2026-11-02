/-
Copyright (c) 2026 Denise M. Case. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Denise M. Case
-/
module

public import SE.IdentityOps.Syntax

set_option autoImplicit false

/-!
# IdentityOps Semantics

SE.IdentityOps.Semantics

The meaning of each command as a function on the model state, and the status of
a pair read off the state.

`apply` of a preserving step is licensed only when the commitments are
consistent and Persistence's `Forbidden` does not hold for the pair. Steps of an
identity-ignoring or identity-breaking operator are recorded in the log and join
no pair. Steps of an inapplicable operator are not executed.

`status` follows Persistence: `Required`, `Forbidden`, `Undetermined`, with an
explicit `inconsistent` case because those statuses are defined for consistent
commitments. A pair that is neither required nor forbidden is undetermined, not
distinct.

`Faithful` is adapted from `SE.OperationalIdentity.Faithful`
(`OI.DEF.FAITHFUL`). Operational Identity is not imported because it has no
release tag to pin; the definition is one line.
-/

namespace SE.IdentityOps

open SE.Persistence

@[expose] public section

variable {C T : Type}

-- RR.DEFINES: IDOPS.DEF.LICENSABLE
/--
A preserving step from `x` to `y` may be applied: the commitments are consistent
and joining `x` and `y` would not identify a pair asserted distinct.
-/
def Licensable (s : State C T) (x y : C) : Prop :=
  Consistent s.same s.distinct ∧ ¬ Forbidden s.same s.distinct x y

-- RR.DEFINES: IDOPS.DEF.STEP
/--
One command applied to a state.

The operator classification is a parameter `cls`, as in Persistence:
`cls t = none` is inapplicable.
-/
noncomputable def step (cls : T → Option ClassificationValue) (s : State C T) :
    Cmd C T → State C T
  | .judge .same x y => { s with same := Extend s.same x y }
  | .judge .distinct x y => { s with distinct := Extend s.distinct x y }
  | .propose _ _ _ => s
  | .check => s
  | .explain => s
  | .apply t x y =>
    match cls t with
    | none => s
    | some ClassificationValue.ign => { s with steps := ⟨t, x, y⟩ :: s.steps }
    | some ClassificationValue.brk => { s with steps := ⟨t, x, y⟩ :: s.steps }
    | some ClassificationValue.prs =>
      haveI := Classical.propDecidable (Licensable s x y)
      if Licensable s x y then
        { s with same := Extend s.same x y, steps := ⟨t, x, y⟩ :: s.steps }
      else s

-- RR.DEFINES: IDOPS.DEF.RUN
/-- A program is a list of commands run left to right. -/
noncomputable def run (cls : T → Option ClassificationValue) (s : State C T)
    (p : List (Cmd C T)) : State C T :=
  p.foldl (step cls) s

-- RR.DEFINES: IDOPS.TYPE.STATUS
/-- The status of a pair. -/
inductive Status where
  | required
  | forbidden
  | undetermined
  | inconsistent
  deriving DecidableEq, Repr

-- RR.DEFINES: IDOPS.DEF.STATUS
/--
The status of `(x, y)` under commitments `P` and `D`.

`inconsistent` when some distinct-commitment lies inside the generated identity.
Otherwise `required`, then `forbidden`, else `undetermined`.
-/
noncomputable def status (P D : C → C → Prop) (x y : C) : Status :=
  haveI := Classical.propDecidable (Consistent P D)
  haveI := Classical.propDecidable (Required P x y)
  haveI := Classical.propDecidable (Forbidden P D x y)
  if ¬ Consistent P D then Status.inconsistent
  else if Required P x y then Status.required
  else if Forbidden P D x y then Status.forbidden
  else Status.undetermined

-- RR.DEFINES: IDOPS.DEF.FAITHFUL
/--
A treatment relation `O` never separates a pair that the declared relation `D`
relates. Adapted from `OI.DEF.FAITHFUL`.
-/
def Faithful (D O : C → C → Prop) : Prop :=
  ∀ r s, D r s → O r s

end

end SE.IdentityOps
