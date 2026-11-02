/-
Copyright (c) 2026 Denise M. Case. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Denise M. Case
-/
module

public import SE.IdentityOps.Semantics

set_option autoImplicit false

/-!
# IdentityOps Properties

SE.IdentityOps.Properties

What the semantics guarantees, and what it does not.

Guaranteed:

- `propose`, `check`, and `explain` leave the state unchanged.
- The same-commitments change only by a same-judgment or by a licensed preserving
  `apply` (`same_step_cases`). No other command can join two items.
- Commitments are only ever added (`run_mono_same`, `run_mono_distinct`), so
  earlier snapshots are never contradicted by a later state's record of them.
- A program with no `judge` keeps consistent commitments consistent
  (`run_preserves_consistency`). Licensing never creates a contradiction.
- A `judge distinct` on a pair that is already required makes the commitments
  inconsistent and is recorded, not discarded (`judge_distinct_required_inconsistent`).
- `status` agrees with Persistence: `required` exactly when every admissible
  identity relation identifies the pair, and so on
  (`status_required_iff_all_admissible`).
- Order matters: licensing a step and then judging its endpoints distinct differs
  from the reverse (`licensing_order_matters`).

Not guaranteed, and not claimed:

- That the Python interpreter implements `step`. That is an obligation checked by
  tests (SEMANTICS.md, "Correspondence"), not by this file.
- That any declared criterion is the right one for any real referents.
-/

namespace SE.IdentityOps

open SE.Persistence

@[expose] public section

variable {C T : Type}

-- ============================================================
-- OBSERVERS
-- ============================================================

-- RR.DEFINES: IDOPS.THM.STEP_PROPOSE
/-- `propose` leaves the state unchanged. -/
theorem step_propose (cls : T → Option ClassificationValue) (s : State C T) (t : T) (x y : C) :
    step cls s (.propose t x y) = s :=
  rfl

-- RR.DEFINES: IDOPS.THM.STEP_CHECK
/-- `check` leaves the state unchanged. -/
theorem step_check (cls : T → Option ClassificationValue) (s : State C T) :
    step cls s .check = s :=
  rfl

-- RR.DEFINES: IDOPS.THM.STEP_EXPLAIN
/-- `explain` leaves the state unchanged. -/
theorem step_explain (cls : T → Option ClassificationValue) (s : State C T) :
    step cls s .explain = s :=
  rfl

-- ============================================================
-- WHAT CAN CHANGE THE SAME-COMMITMENTS
-- ============================================================

-- RR.DEFINES: IDOPS.THM.SAME_STEP_CASES
/--
After one command, the same-commitments are either unchanged, or extended by a
same-judgment, or extended by a licensed step of a preserving operator.
-/
theorem same_step_cases (cls : T → Option ClassificationValue) (s : State C T) (c : Cmd C T) :
    (step cls s c).same = s.same ∨
    (∃ x y, c = .judge .same x y ∧ (step cls s c).same = Extend s.same x y) ∨
    (∃ t x y, c = .apply t x y ∧ cls t = some ClassificationValue.prs ∧ Licensable s x y ∧
      (step cls s c).same = Extend s.same x y) := by
  cases c with
  | judge p x y =>
    cases p with
    | same => exact Or.inr (Or.inl ⟨x, y, rfl, rfl⟩)
    | distinct => exact Or.inl rfl
  | propose t x y => exact Or.inl rfl
  | check => exact Or.inl rfl
  | explain => exact Or.inl rfl
  | apply t x y =>
    cases h : cls t with
    | none => left; simp [step, h]
    | some v =>
      cases v with
      | ign => left; simp [step, h]
      | brk => left; simp [step, h]
      | prs =>
        by_cases hl : Licensable s x y
        · right; right
          refine ⟨t, x, y, rfl, h, hl, ?_⟩
          simp [step, h, hl]
        · left; simp [step, h, hl]

-- RR.DEFINES: IDOPS.THM.SAME_STEP_EQ_OF_NOT_JUDGE_OR_APPLY
/-- A command that is neither a judgment nor an application leaves the same-commitments unchanged. -/
theorem same_step_eq_of_observer (cls : T → Option ClassificationValue) (s : State C T)
    {c : Cmd C T} (h : c = .check ∨ c = .explain ∨ ∃ t x y, c = .propose t x y) :
    (step cls s c).same = s.same := by
  rcases h with rfl | rfl | ⟨t, x, y, rfl⟩ <;> rfl

-- ============================================================
-- MONOTONICITY: COMMITMENTS ARE ONLY ADDED
-- ============================================================

-- RR.DEFINES: IDOPS.THM.STEP_MONO_SAME
/-- A command never removes a same-commitment. -/
theorem step_mono_same (cls : T → Option ClassificationValue) (s : State C T) (c : Cmd C T)
    {x y : C} (h : s.same x y) : (step cls s c).same x y := by
  rcases same_step_cases cls s c with hc | ⟨a, b, _, hc⟩ | ⟨t, a, b, _, _, _, hc⟩
  · rw [hc]; exact h
  · rw [hc]; exact Or.inl h
  · rw [hc]; exact Or.inl h

-- RR.DEFINES: IDOPS.THM.STEP_MONO_DISTINCT
/-- A command never removes a distinct-commitment. -/
theorem step_mono_distinct (cls : T → Option ClassificationValue) (s : State C T) (c : Cmd C T)
    {x y : C} (h : s.distinct x y) : (step cls s c).distinct x y := by
  cases c with
  | judge p a b =>
    cases p with
    | same => exact h
    | distinct => exact Or.inl h
  | propose t a b => exact h
  | check => exact h
  | explain => exact h
  | apply t a b =>
    cases hc : cls t with
    | none => simpa [step, hc] using h
    | some v =>
      cases v with
      | ign => simpa [step, hc] using h
      | brk => simpa [step, hc] using h
      | prs =>
        by_cases hl : Licensable s a b
        · simpa [step, hc, hl] using h
        · simpa [step, hc, hl] using h

-- RR.DEFINES: IDOPS.THM.RUN_CONS
/-- Running a command followed by a program is running the program after the command. -/
theorem run_cons (cls : T → Option ClassificationValue) (s : State C T) (c : Cmd C T)
    (p : List (Cmd C T)) : run cls s (c :: p) = run cls (step cls s c) p :=
  rfl

-- RR.DEFINES: IDOPS.THM.RUN_APPEND
/-- Running two programs in turn is running their concatenation. -/
theorem run_append (cls : T → Option ClassificationValue) (s : State C T)
    (p q : List (Cmd C T)) : run cls s (p ++ q) = run cls (run cls s p) q := by
  unfold run
  exact List.foldl_append

-- RR.DEFINES: IDOPS.THM.RUN_MONO_SAME
/-- No program removes a same-commitment. -/
theorem run_mono_same (cls : T → Option ClassificationValue) (p : List (Cmd C T)) :
    ∀ (s : State C T) {x y : C}, s.same x y → (run cls s p).same x y := by
  induction p with
  | nil => intro s x y h; exact h
  | cons c p ih => intro s x y h; exact ih (step cls s c) (step_mono_same cls s c h)

-- RR.DEFINES: IDOPS.THM.RUN_MONO_DISTINCT
/-- No program removes a distinct-commitment. -/
theorem run_mono_distinct (cls : T → Option ClassificationValue) (p : List (Cmd C T)) :
    ∀ (s : State C T) {x y : C}, s.distinct x y → (run cls s p).distinct x y := by
  induction p with
  | nil => intro s x y h; exact h
  | cons c p ih => intro s x y h; exact ih (step cls s c) (step_mono_distinct cls s c h)

-- ============================================================
-- CONSISTENCY
-- ============================================================

-- RR.DEFINES: IDOPS.THM.CONSISTENT_EXTEND_OF_NOT_FORBIDDEN
/-- If identifying `x` and `y` is not forbidden, extending by that pair keeps commitments consistent. -/
theorem consistent_extend_of_not_forbidden {P D : C → C → Prop} {x y : C}
    (h : ¬ Forbidden P D x y) : Consistent (Extend P x y) D := by
  intro u v hD hg
  exact h ⟨u, v, hD, hg⟩

/-- A command that is not a judgment is one of the observers or an application. -/
def IsJudge (c : Cmd C T) : Prop :=
  ∃ p x y, c = .judge p x y

-- RR.DEFINES: IDOPS.THM.STEP_PRESERVES_CONSISTENCY
/-- A command that is not a judgment keeps consistent commitments consistent. -/
theorem step_preserves_consistency (cls : T → Option ClassificationValue) (s : State C T)
    (c : Cmd C T) (hc : Consistent s.same s.distinct) (hj : ¬ IsJudge c) :
    Consistent (step cls s c).same (step cls s c).distinct := by
  cases c with
  | judge p x y => exact absurd ⟨p, x, y, rfl⟩ hj
  | propose t x y => exact hc
  | check => exact hc
  | explain => exact hc
  | apply t x y =>
    cases h : cls t with
    | none => simpa [step, h] using hc
    | some v =>
      cases v with
      | ign => simpa [step, h] using hc
      | brk => simpa [step, h] using hc
      | prs =>
        by_cases hl : Licensable s x y
        · simp only [step, h, hl, ite_true]
          exact consistent_extend_of_not_forbidden hl.2
        · simpa [step, h, hl] using hc

/-- No command of the program is a judgment. -/
def NoJudge (p : List (Cmd C T)) : Prop :=
  ∀ c ∈ p, ¬ IsJudge c

-- RR.DEFINES: IDOPS.THM.RUN_PRESERVES_CONSISTENCY
/--
A program with no judgment keeps consistent commitments consistent: licensing a
step never creates a contradiction.
-/
theorem run_preserves_consistency (cls : T → Option ClassificationValue) (p : List (Cmd C T))
    (hp : NoJudge p) :
    ∀ (s : State C T), Consistent s.same s.distinct →
      Consistent (run cls s p).same (run cls s p).distinct := by
  induction p with
  | nil => intro s hc; exact hc
  | cons c p ih =>
    intro s hc
    have hcj : ¬ IsJudge c := hp c (List.mem_cons_self ..)
    have hpj : NoJudge p := fun d hd => hp d (List.mem_cons_of_mem _ hd)
    exact ih hpj (step cls s c) (step_preserves_consistency cls s c hc hcj)

-- RR.DEFINES: IDOPS.THM.JUDGE_DISTINCT_REQUIRED_INCONSISTENT
/--
Judging a pair distinct when it is already required identical makes the
commitments inconsistent. The judgment is recorded, not discarded.
-/
theorem judge_distinct_required_inconsistent (cls : T → Option ClassificationValue)
    (s : State C T) {x y : C} (h : Required s.same x y) :
    ¬ Consistent (step cls s (.judge .distinct x y)).same
      (step cls s (.judge .distinct x y)).distinct := by
  intro hc
  exact hc x y (Or.inr ⟨rfl, rfl⟩) h

-- RR.DEFINES: IDOPS.THM.APPLY_BLOCKED_OF_FORBIDDEN
/-- A preserving step whose endpoints are forbidden to be identical changes neither commitments nor log. -/
theorem apply_blocked_of_forbidden (cls : T → Option ClassificationValue) (s : State C T)
    {t : T} {x y : C} (hp : cls t = some ClassificationValue.prs)
    (hf : Forbidden s.same s.distinct x y) :
    step cls s (.apply t x y) = s := by
  have hl : ¬ Licensable s x y := fun h => h.2 hf
  simp [step, hp, hl]

-- RR.DEFINES: IDOPS.THM.APPLY_FORK_BRANCH_BLOCKED
/--
A fork. If one preserving step from `a` to `b` is recorded and `b` and `c` are
asserted distinct, a preserving step from `a` to `c` is blocked.
-/
theorem apply_fork_branch_blocked (cls : T → Option ClassificationValue) (s : State C T)
    {t : T} {a b c : C} (hp : cls t = some ClassificationValue.prs)
    (hab : s.same a b) (hbc : s.distinct b c) :
    step cls s (.apply t a c) = s :=
  apply_blocked_of_forbidden cls s hp (fork_branch_forbidden hab hbc)

-- RR.DEFINES: IDOPS.THM.APPLY_MERGE_BRANCH_BLOCKED
/--
A merge. If a preserving step from `a` into `c` is recorded and `a` and `b` are
asserted distinct, a preserving step from `b` into `c` is blocked.
-/
theorem apply_merge_branch_blocked (cls : T → Option ClassificationValue) (s : State C T)
    {t : T} {a b c : C} (hp : cls t = some ClassificationValue.prs)
    (hac : s.same a c) (hab : s.distinct a b) :
    step cls s (.apply t b c) = s := by
  refine apply_blocked_of_forbidden cls s hp ⟨a, b, hab, ?_⟩
  exact Generated.trans (Generated.rel (Or.inl hac)) (Generated.symm (Generated.rel (Or.inr ⟨rfl, rfl⟩)))

-- ============================================================
-- STATUS AGREES WITH PERSISTENCE
-- ============================================================

-- RR.DEFINES: IDOPS.THM.STATUS_REQUIRED_IFF
/-- Under consistent commitments, `status` is `required` exactly when `Required` holds. -/
theorem status_required_iff {P D : C → C → Prop} (hc : Consistent P D) (x y : C) :
    status P D x y = Status.required ↔ Required P x y := by
  unfold status
  by_cases hr : Required P x y
  · simp [hc, hr]
  · by_cases hf : Forbidden P D x y <;> simp [hc, hr, hf]

-- RR.DEFINES: IDOPS.THM.STATUS_FORBIDDEN_IFF
/-- Under consistent commitments, `status` is `forbidden` exactly when `Forbidden` holds. -/
theorem status_forbidden_iff {P D : C → C → Prop} (hc : Consistent P D) (x y : C) :
    status P D x y = Status.forbidden ↔ Forbidden P D x y := by
  unfold status
  by_cases hr : Required P x y
  · have hnf : ¬ Forbidden P D x y := fun hf => not_required_and_forbidden hc ⟨hr, hf⟩
    simp [hc, hr, hnf]
  · by_cases hf : Forbidden P D x y <;> simp [hc, hr, hf]

-- RR.DEFINES: IDOPS.THM.STATUS_UNDETERMINED_IFF
/-- Under consistent commitments, `status` is `undetermined` exactly when neither required nor forbidden. -/
theorem status_undetermined_iff {P D : C → C → Prop} (hc : Consistent P D) (x y : C) :
    status P D x y = Status.undetermined ↔ Undetermined P D x y := by
  unfold status Undetermined
  by_cases hr : Required P x y <;> by_cases hf : Forbidden P D x y <;> simp [hc, hr, hf]

-- RR.DEFINES: IDOPS.THM.STATUS_INCONSISTENT_IFF
/-- `status` is `inconsistent` exactly when the commitments are not consistent. -/
theorem status_inconsistent_iff (P D : C → C → Prop) (x y : C) :
    status P D x y = Status.inconsistent ↔ ¬ Consistent P D := by
  unfold status
  by_cases hc : Consistent P D <;> by_cases hr : Required P x y <;>
    by_cases hf : Forbidden P D x y <;> simp [hc, hr, hf]

-- RR.DEFINES: IDOPS.THM.STATUS_REQUIRED_IFF_ALL_ADMISSIBLE
/--
Under consistent commitments, `status` is `required` exactly when every
admissible identity relation identifies the pair. This is the definition the
exhaustive tests in `tests/test_oracle.py` enumerate.
-/
theorem status_required_iff_all_admissible {P D : C → C → Prop} (hc : Consistent P D) (x y : C) :
    status P D x y = Status.required ↔ ∀ E, Admissible P D E → E x y := by
  rw [status_required_iff hc, required_iff_forall_admissible hc]

-- RR.DEFINES: IDOPS.THM.STATUS_FORBIDDEN_IFF_ALL_ADMISSIBLE
/-- Under consistent commitments, `status` is `forbidden` exactly when every admissible identity relation separates the pair. -/
theorem status_forbidden_iff_all_admissible {P D : C → C → Prop} (hc : Consistent P D) (x y : C) :
    status P D x y = Status.forbidden ↔ ∀ E, Admissible P D E → ¬ E x y := by
  rw [status_forbidden_iff hc, forbidden_iff_forall_admissible]

-- RR.DEFINES: IDOPS.THM.UNDETERMINED_NOT_DISTINCT
/--
Not required is not distinct: an undetermined pair is not forbidden, so no
distinct-commitment is implied for it.
-/
theorem not_forbidden_of_status_undetermined {P D : C → C → Prop} (hc : Consistent P D) {x y : C}
    (h : status P D x y = Status.undetermined) : ¬ Forbidden P D x y :=
  ((status_undetermined_iff hc x y).1 h).2

-- ============================================================
-- FAITHFULNESS (adapted from OI.THM.FAITHFUL_GENERATED_IFF_GENERATORS)
-- ============================================================

-- RR.DEFINES: IDOPS.THM.FAITHFUL_GENERATED_IFF_GENERATORS
/--
When the treatment relation is an equivalence, faithfulness to a generated
relation is checked on the generating pairs. This is why the interpreter
compares each class with its first item. Adapted from Operational Identity.
-/
theorem faithful_generated_iff_generators {P O : C → C → Prop} (hO : Equivalence O) :
    Faithful (Generated P) O ↔ ∀ x y, P x y → O x y := by
  constructor
  · intro h x y hp
    exact h x y (Generated.rel hp)
  · intro h x y hg
    exact Generated.le_of_equivalence hO h hg

-- ============================================================
-- ORDER MATTERS
-- ============================================================

-- RR.DEFINES: IDOPS.THM.LICENSING_ORDER_MATTERS
/--
Order changes the result. Over two items with one preserving operator, applying a
step and then judging its endpoints distinct leaves the endpoints joined; judging
them distinct first blocks the step.
-/
theorem licensing_order_matters :
    let cls : Unit → Option ClassificationValue := fun _ => some ClassificationValue.prs
    let s0 : State Bool Unit := State.empty Bool Unit
    (run cls s0 [.apply () false true, .judge .distinct false true]).same false true ∧
    ¬ (run cls s0 [.judge .distinct false true, .apply () false true]).same false true := by
  intro cls s0
  constructor
  · have hl : Licensable s0 false true := by
      refine ⟨?_, ?_⟩
      · intro u v hD
        exact hD.elim
      · rintro ⟨u, v, hD, _⟩
        exact hD.elim
    have hs : (step cls s0 (.apply () false true)).same false true := by
      simp only [step, cls, hl, ite_true]
      exact Or.inr ⟨rfl, rfl⟩
    exact run_mono_same cls [.judge .distinct false true] _ hs
  · have hf : Forbidden (State.empty Bool Unit).same
        (step cls s0 (.judge .distinct false true)).distinct false true := by
      refine ⟨false, true, Or.inr ⟨rfl, rfl⟩, ?_⟩
      exact Generated.rel (Or.inr ⟨rfl, rfl⟩)
    have hblocked := apply_blocked_of_forbidden cls
      (step cls s0 (.judge .distinct false true)) (t := ()) (x := false) (y := true) rfl hf
    show ¬ (step cls (step cls s0 (.judge .distinct false true)) (.apply () false true)).same
      false true
    rw [hblocked]
    intro h
    exact h

end

end SE.IdentityOps
