# Prior Art

This page compares IdentityOps with existing work. Its purpose is to prevent a
claim of novelty from resting on different terminology.

**No claim of novelty is made.** A difference is recorded only where a comparison
exercised it, and even then it may be a difference of vocabulary or cost rather
than of expressive power.

## What the Comparison Covers

Primary comparison: **LACE** and its extensions **LACE+** and the systems **ASPEN**
and **ASPEN+**, as described in the survey
[Recent Advances in Logic-Based Entity Resolution](https://orca.cardiff.ac.uk/id/eprint/181984/)
(Bienvenu et al., SIGMOD Record, 2025) and the papers it summarizes. Secondary
comparison: Dedupalog, Swoosh, Cedar, Catala, and the SE theories IdentityOps builds on.

What was read for this page:

- the survey above, in full text;
- LACE: [Bienvenu, Cima, Gutiérrez-Basulto, LACE (PODS 2022)](https://www.labri.fr/perso/meghyn/papers/BieCimGut-PODS22.pdf);
- LACE+: [Combining Global and Local Merges (KR 2023)](https://arxiv.org/abs/2305.16926);
- ASPEN: [ASPEN: ASP-Based System for Collective Entity Resolution (KR 2024)](https://arxiv.org/abs/2408.06961);
- ASPEN+: [Advances in Logic-Based Entity Resolution: Enhancing ASPEN with Local Merges and Optimality Criteria (KR 2025)](https://arxiv.org/abs/2508.10504), and the [published code](https://github.com/zl-xiang/ASPEnP).

What was **not** done: ASPEN and ASPEN+ were not run. Their code needs a Python 3.9
environment, a bundled asprin copy, a Python schema configuration, and precomputed
similarity facts, and the published repository carries no license file. The
formulations tried are my own plain-clingo encodings of LACE-style semantics, written
by the author of the IdentityOps interpreter. They are not independent of it. See
[LACE Attempts](./lace-attempts.md).

## What LACE, LACE+, and ASPEN+ Provide

As described in the survey and papers:

- **Declarative merge rules** over object references (hard rules: a match is
  sufficient to merge; soft rules: a match is evidence, the merge is optional).
- **Denial constraints** that block combinations of merges, generalizing
  functional dependencies.
- **Dynamic semantics**: rule bodies are evaluated over the instance that results
  from merges already derived, so merges can trigger further merges.
- **Solutions as equivalence relations**, built only by rule applications, and
  **maximal solutions** under set inclusion.
- **Justifications**: every merge in a solution can be traced to the rule
  applications that produced it, and ASPEN produces proof trees.
- **Alternative resolutions**: a space of solutions, with **certain** merges (in all)
  and **possible** merges (in some), and seven optimality criteria for preferred
  solutions (ASPEN+).
- **Local merges of values** (LACE+), in addition to global merges of object references.
- **Complexity results** for recognition, existence, possible and certain merges.
- A repair extension (Replace) with fact deletions.

The survey states that temporal evolution is not addressed; its "evolving instance"
is the database changing during one resolution run. It lists as open: explanations
over the whole solution space, ontologies, scalability, and learning specifications.

## Capability Comparison

For each proposed IdentityOps capability, the relation to LACE as examined. The four
labels are exact:

- **Demonstrated in LACE**: described in the cited work as a LACE capability.
- **Potentially expressible in LACE**: I wrote an encoding that reproduces the
  result, or can see one, but it is not a task the cited work defines.
- **Unclear or requiring further investigation**.
- **Outside the demonstrated scope examined**: not described in the cited work, and
  I found no direct encoding.

The capabilities:

1. **Key criterion as a declared relation** (regime by key column).
   *Demonstrated in LACE.* A hard rule joining on an equal key.
2. **Explicit same and distinct judgments with a consistency check.**
   *Demonstrated in LACE.* Same-judgments as hard merges or facts; distinct-judgments
   as denial constraints; consistency as existence of a solution.
3. **Required, forbidden, and undetermined status of a pair.**
   *Potentially expressible in LACE.* Certain merges correspond to required and are
   a defined LACE task. Telling forbidden from undetermined needs one soft rule
   offering every pair as a candidate merge, so that possible merges are exactly the
   non-forbidden pairs. My encoding reproduced the interpreter's status on all 4,455
   pairs of all assignments for 3 and 4 items. Without that quadratic soft rule an
   unmerged pair is simply unmerged.
4. **Inconsistent commitments reported with a witness** (the conflicting distinct
   judgment and the chain of same-commitments that joins its endpoints).
   *Unclear or requiring further investigation.* LACE detects absence of a solution.
   The survey describes explanations of merges, not of why no solution exists, and
   lists explanations over the solution space as open. I did not test this.
5. **Derivation of a required pair as a chain.**
   *Demonstrated in LACE* (justifications and proof trees). IdentityOps chains are a
   simpler analogue, a shortest chain of same-commitments. No advantage is claimed.
6. **Audit of an implementation mechanism against a declared criterion** (`faithful`).
   *Potentially expressible in LACE.* Two hard-rule sets, one for the criterion and one
   for the mechanism, plus ordinary meta-rules comparing their results, reproduced the
   Chicago and SBOM counts exactly. LACE does not define this comparison.
7. **Merges a mechanism makes that a criterion does not support** (`collisions`).
   *Potentially expressible in LACE,* by the same encoding, and also reproduced exactly.
8. **A verdict withheld when the criterion or check has no grounding source**
   (`unwarranted`). *Outside the demonstrated scope examined.* This is a design
   choice about reporting, not a reasoning capability.
9. **A gated, snapshot-producing state change** (`apply`). *Outside the demonstrated
   scope examined.* Whether a preserving step can be added without contradiction can
   be decided by re-solving with the step added, and my driver reproduced the
   interpreter's licensed and blocked outcomes that way. The sequence of states and
   the retained snapshots live in the driver, not in LACE.
10. **Operators classified identity-ignoring, breaking, or inapplicable, reported as
    such.** *Outside the demonstrated scope examined.* LACE rules either merge or do not.
    The four steps in the synthetic persistence program with these classifications
    could not be encoded; see [LACE Attempts](./lace-attempts.md).
11. **Lineage kept apart from identity** (two successors of one state are not
    identical unless a licensed step joins them).
    *Potentially expressible in LACE.* No rule, no merge. What is new is only the
    explicit report that an ignoring operator was seen and joined nothing.
12. **Dependence on operation order.** *Outside the demonstrated scope examined.* LACE
    solutions are declarative and order-insensitive by design. IdentityOps' order
    sensitivity (licensing is order-dependent) is a different modeling choice and is
    not claimed as an advantage.
13. **Persistence across stages or time.** *Outside the demonstrated scope examined.*
    The survey states temporal evolution is not addressed. IdentityOps has no
    evidence yet either: the persistence experiment ran only synthetic controls.
14. **Named causes for an unsettled result** (insufficient information,
    inapplicability, operator underdetermination). *Unclear or requiring further
    investigation.* LACE reports certain, possible, or no solution. Whether named
    causes add anything beyond that vocabulary is unestablished.

Capabilities LACE+ and ASPEN+ have that IdentityOps **excludes** by design, and does
not claim: similarity predicates, soft rules, optimality criteria, alternative
resolutions and preferred solutions, local merges of values, dynamic rule semantics,
and repair by deletion. For the Chicago data, local merges of values may model the
spelling variants IdentityOps found (see below); that is unresolved.

## Specific Differences Demonstrated

Only these were demonstrated, by running the comparison:

1. **Cost of reading "undetermined" from a LACE-style encoding.** The open-world
   encoding grounds to 100, 400, 1,600, and 6,400 atoms at 10, 20, 40, and 80 items
   (quadratic), and grounding time rose from about a thousandth of a second to about half
   a second on the machine used (timings depend on the machine and are not committed). The interpreter
   computes statuses by closure on 20,000 items in a fraction of a second. This is the
   cost of my encoding, not a proof that ASPEN+ cannot do better.
2. **Vocabulary for steps.** Ignoring, breaking, and inapplicable operators have no
   LACE counterpart; four steps in the synthetic persistence program were reported as
   "not expressible". This is a difference of vocabulary, and whether it is useful is
   unestablished.
3. **Warrant.** IdentityOps withholds a verdict when a regime names no source. LACE
   has no such notion. This is a reporting rule that could be added to any system.
4. **Order.** IdentityOps programs are order-sensitive in `judge` and `apply`; LACE
   specifications are not. Neither is better in general.

Nothing here shows that IdentityOps can specify, execute, or audit something LACE
cannot. Whether it is **useful** in a way LACE is not (an explicit audit-oriented
vocabulary, a small interpreter) is a separate question that this experiment does not
answer.

## What Would Establish or Reject a Difference

- Run ASPEN and ASPEN+ themselves on the Chicago slice and compare their explanations
  with IdentityOps' witnesses and chains.
- Try LACE+ local merges on the two Chicago variants found (an ampersand against the
  word "and"; a renamed vendor under one ID) to see what a value merge would say.
- Ask whether a LACE-style specification can state, rather than only reproduce,
  the audit as a first-class task with its own justification.
- Test claim 4 above: what LACE reports when distinct judgments make a specification
  unsatisfiable, and whether it localizes the conflict.

## Other Prior Art

- **Dedupalog** (Arasu, Ré, Suciu, "Large-scale deduplication with constraints using
  Dedupalog", ICDE 2009): declarative deduplication with hard and soft rules. LACE
  builds on it, as the LACE papers state.
- **Swoosh** (Benjelloun, Garcia-Molina, Menestrina, Su, Whang, Widom, "Swoosh: a generic
  approach to entity resolution", VLDB Journal 18(1), 2009): match and merge as black
  boxes, with properties that make resolution efficient.
  IdentityOps treats the mechanism as a black box in the same spirit, and audits its
  recorded output.
- **Negative rules in entity resolution** ([ER-N, VLDB Journal](https://vldb.org/vldb_journal/index.php/component/article_manager/article/1105)):
  rules that disallow inconsistent solutions. Relevant to distinct-judgments; not
  compared in detail.
- **Cedar** ([How We Built Cedar, 2024](https://arxiv.org/abs/2407.01688)):
  a Lean model, a production implementation, and differential random testing between
  them. IdentityOps follows the same shape at a much smaller scale, with an
  exhaustive small-state comparison in place of random inputs, and with no claim that
  the Python code is verified.
- **Catala** ([Merigoux, Chataing, Protzenko, ICFP 2021](https://arxiv.org/abs/2103.03198)):
  a language with formal semantics, deliberately not Turing-complete. IdentityOps
  keeps its language small for the same reason.
- **`se-theory-persistence`** and **`se-theory-operational-identity`**: the commitment
  calculus and the declared-versus-implemented comparison that IdentityOps reuses.
  Prior work inside the SE program, not outside it.

## Sources

- Bienvenu et al., [Recent Advances in Logic-Based Entity Resolution](https://orca.cardiff.ac.uk/id/eprint/181984/).
- Bienvenu, Cima, Gutiérrez-Basulto, [LACE](https://www.labri.fr/perso/meghyn/papers/BieCimGut-PODS22.pdf).
- Bienvenu, Cima, Gutiérrez-Basulto, Ibáñez-García, [Combining Global and Local Merges](https://arxiv.org/abs/2305.16926).
- Xiang et al., [ASPEN](https://arxiv.org/abs/2408.06961) and [ASPEN+](https://arxiv.org/abs/2508.10504); code at [zl-xiang/ASPEnP](https://github.com/zl-xiang/ASPEnP).
- [How We Built Cedar](https://arxiv.org/abs/2407.01688); [Catala](https://arxiv.org/abs/2103.03198).
