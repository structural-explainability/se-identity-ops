/-
Copyright (c) 2026 Denise M. Case. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Denise M. Case
-/
module -- shake: keep-all

public import SE.IdentityOps.Syntax
public import SE.IdentityOps.Semantics
public import SE.IdentityOps.Properties

/-!
# SE IdentityOps

Lean 4 core of the IdentityOps experiment: the command language, the model
state, the meaning of each command, and properties of that meaning.

This is a research experiment. It states the intended meaning of the Python
reference interpreter. The Python code is not verified by this development; the
correspondence between them is an explicit obligation (see SEMANTICS.md).
-/
