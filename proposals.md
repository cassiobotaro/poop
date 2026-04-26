# Proposals — POOP code review

**bug** ✅ resolved

`print` now returns `None` (like Python/Ruby), so the REPL displayhook no longer
shows the value a second time.

---

**bug**

When I type (1).print() the output is

```bash
>>> b = (1).to_(100)
>>> b
range(1, 101)
```

The expected output is

```bash
>>> b = (1).to_(100)
>>> b
range(1, 100)
```

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

