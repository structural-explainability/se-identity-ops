/-
Copyright (c) 2026 Denise M. Case. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Denise M. Case
-/
module

public import SE.IdentityOps

set_option autoImplicit false

/-!
# IdentityOps Checks

Concrete checks of the semantics on small carriers. Each mirrors a synthetic
control in `examples/persistence/program.ido`, so the Lean statement and the
Python run can be read side by side.
-/

namespace SETest.IdentityOps

open SE.Persistence SE.IdentityOps

@[expose] public section

/-- Every operator is preserving. -/
def allPreserving : Unit → Option ClassificationValue := fun _ => some ClassificationValue.prs

/-- The only operator is identity-ignoring. -/
def allIgnoring : Unit → Option ClassificationValue := fun _ => some ClassificationValue.ign

/-- The only operator is identity-breaking. -/
def allBreaking : Unit → Option ClassificationValue := fun _ => some ClassificationValue.brk

/-- The only operator is inapplicable. -/
def inapplicable : Unit → Option ClassificationValue := fun _ => none

/-- A step of an identity-ignoring operator is logged and joins nothing. -/
theorem ignoring_joins_nothing (x y a b : Fin 3) :
    (step allIgnoring (State.empty (Fin 3) Unit) (.apply () x y)).same a b ↔ False := by
  simp [step, allIgnoring, State.empty]

/-- A step of an identity-breaking operator is logged and joins nothing. -/
theorem breaking_joins_nothing (x y a b : Fin 3) :
    (step allBreaking (State.empty (Fin 3) Unit) (.apply () x y)).same a b ↔ False := by
  simp [step, allBreaking, State.empty]

/-- A step of an inapplicable operator is not executed. -/
theorem inapplicable_is_not_executed (x y : Fin 3) :
    step inapplicable (State.empty (Fin 3) Unit) (.apply () x y) = State.empty (Fin 3) Unit := by
  simp [step, inapplicable]

/-- Fork: with the branches asserted distinct, the second branch is blocked. -/
theorem fork_second_branch_blocked :
    ¬ (run allPreserving (State.empty (Fin 3) Unit)
        [.apply () 0 1, .judge .distinct 1 2, .apply () 0 2]).same 0 2 := by
  have hl : Licensable (State.empty (Fin 3) Unit) 0 1 := by
    refine ⟨fun u v hD => hD.elim, ?_⟩
    rintro ⟨u, v, hD, _⟩
    exact hD.elim
  have hs1 : (step allPreserving (State.empty (Fin 3) Unit) (.apply () 0 1)).same =
      Extend (State.empty (Fin 3) Unit).same 0 1 := by
    simp [step, allPreserving, hl]
  have h2 : (step allPreserving (step allPreserving (State.empty (Fin 3) Unit) (.apply () 0 1))
      (.judge .distinct 1 2)).same 0 1 := by
    show (step allPreserving (State.empty (Fin 3) Unit) (.apply () 0 1)).same 0 1
    rw [hs1]
    exact Or.inr ⟨rfl, rfl⟩
  have h3 : (step allPreserving (step allPreserving (State.empty (Fin 3) Unit) (.apply () 0 1))
      (.judge .distinct 1 2)).distinct 1 2 :=
    Or.inr ⟨rfl, rfl⟩
  have hblocked := apply_fork_branch_blocked allPreserving
    (step allPreserving (step allPreserving (State.empty (Fin 3) Unit) (.apply () 0 1))
      (.judge .distinct 1 2)) (t := ()) (a := 0) (b := 1) (c := 2) rfl h2 h3
  show ¬ (step allPreserving (step allPreserving
      (step allPreserving (State.empty (Fin 3) Unit) (.apply () 0 1))
      (.judge .distinct 1 2)) (.apply () 0 2)).same 0 2
  rw [hblocked]
  intro h
  have h' : (step allPreserving (State.empty (Fin 3) Unit) (.apply () 0 1)).same 0 2 := h
  rw [hs1] at h'
  rcases h' with h' | ⟨_, h'⟩
  · exact h'
  · exact absurd h' (by decide)

/-- With no distinctions, a pair nobody has judged is undetermined, not distinct. -/
theorem unjudged_pair_is_undetermined (x y : Fin 3) (hxy : x ≠ y) :
    status (State.empty (Fin 3) Unit).same (State.empty (Fin 3) Unit).distinct x y =
      Status.undetermined := by
  have hc : Consistent (State.empty (Fin 3) Unit).same (State.empty (Fin 3) Unit).distinct :=
    fun u v hD => hD.elim
  rw [status_undetermined_iff hc]
  refine ⟨?_, ?_⟩
  · intro hr
    have heq : x = y :=
      Generated.le_of_equivalence (s := fun a b : Fin 3 => a = b)
        ⟨fun _ => rfl, fun h => h.symm, fun h1 h2 => h1.trans h2⟩
        (fun _ _ hf => hf.elim) hr
    exact hxy heq
  · rintro ⟨u, v, hD, _⟩
    exact hD.elim

end

end SETest.IdentityOps
