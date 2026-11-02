/-
Copyright (c) 2026 Denise M. Case. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Denise M. Case
-/
module

public import SE.Persistence

set_option autoImplicit false

/-!
# IdentityOps Syntax

SE.IdentityOps.Syntax

The command language of IdentityOps and the model state it acts on.

Items are records. This module has no type of referents and no function from
records to referents, so no command can turn a record match into a referent
claim. A same-commitment between two records is a model-level commitment made
by a judgment or by a licensed step.

Operator classifications are Persistence's: `none` is inapplicable and `some v`
is applicable with class `v`. This module adds no classification of its own.

Declarations (`source`, `carrier`, `regime`, `surface`, `probe`) are not modeled
here. This core covers the five operations over one regime and one carrier.
`check` and `explain` observe the state and never change it; what they report is
given by `status` in `SE.IdentityOps.Semantics`.
-/

namespace SE.IdentityOps

@[expose] public section

-- RR.DEFINES: IDOPS.TYPE.POLARITY
/-- A judgment says two items are the same or are distinct. -/
inductive Polarity where
  | same
  | distinct
  deriving DecidableEq, Repr

-- RR.DEFINES: IDOPS.TYPE.CMD
/--
A command over items `C` and operators `T`.

- `judge`: record a same or distinct judgment.
- `propose`: construct a step without changing the state.
- `apply`: execute a step if its conditions hold.
- `check`, `explain`: observe the state.
-/
inductive Cmd (C T : Type) where
  | judge (polarity : Polarity) (first second : C)
  | propose (operator : T) (first second : C)
  | apply (operator : T) (first second : C)
  | check
  | explain

-- RR.DEFINES: IDOPS.TYPE.APPLIED_STEP
/-- A transformation step recorded in the model state. -/
structure AppliedStep (C T : Type) where
  /-- The operator of the step. -/
  operator : T
  /-- The item before the step. -/
  first : C
  /-- The item after the step. -/
  second : C

-- RR.DEFINES: IDOPS.TYPE.STATE
/--
The model state.

`same` and `distinct` are the asserted same-commitments and distinct-commitments
that Persistence's calculus takes as inputs `P` and `D`. `steps` is the log of
applied steps. The state is a model of declared commitments, not a claim about
referents.
-/
structure State (C T : Type) where
  /-- Asserted same-commitments: judgments and licensed steps. -/
  same : C → C → Prop
  /-- Asserted distinct-commitments. -/
  distinct : C → C → Prop
  /-- Applied steps, most recent first. -/
  steps : List (AppliedStep C T)

-- RR.DEFINES: IDOPS.DEF.STATE_EMPTY
/-- The initial state: no commitments and no steps. -/
def State.empty (C T : Type) : State C T where
  same := fun _ _ => False
  distinct := fun _ _ => False
  steps := []

end

end SE.IdentityOps
