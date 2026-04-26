# Proposals — POOP code review

**bug** ✅ resolved

`print` now returns `None` (like Python/Ruby), so the REPL displayhook no longer
shows the value a second time.

---

**bug** ✅ resolved

`Range.__str__` now uses the original `stop` value instead of exposing the
internal Python range (`stop + sign`). Iteration was already correct (inclusive);
only the display was wrong.

---

**improvement**

Quickstart in the readme summarizing the infections and showing some examples.

---

**improvement**

Add more code examples and review the existing ones.

---

**improvement**

Add pipeline and dependabot.

---

**improvement**

Review the builtin functions to check if they are blocked / implemented as methods.

---

**improvement**

Create a github workflow to run on each pr or push to main using uv and run ruff format and linter, tests, ty.

