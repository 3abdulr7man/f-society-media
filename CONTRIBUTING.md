# Contributing to F-SOCIETY YT-DLP PRO

Thank you for your interest in contributing! Contributions make the open-source community an amazing place to learn, inspire, and create.

We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features

---

## Code of Conduct

By participating, you are expected to uphold our Code of Conduct. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details.

---

## How to Contribute

### 1. Fork & Clone
Fork the repository on GitHub and clone your fork locally:

```bash
git clone https://github.com/your-username/F-SOCIETY-YTDLP.git
cd F-SOCIETY-YTDLP
```

### 2. Configure Environment
Set up a Python virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable development mode with tests support
pip install -e .
```

### 3. Create a Branch
Always create a branch off of `main` for your modifications. Give it a descriptive name:

```bash
git checkout -b feature/your-amazing-feature
# or
git checkout -b fix/bug-description
```

### 4. Code and Style Guidelines
- Write clean, readable code conforming to [PEP 8](https://peps.python.org/pep-0008/).
- Document new functions, classes, and parameters.
- Do not add large monolithic functions; modularize components inside `src/core/`, `src/cli/`, or `src/gui/`.

### 5. Run Tests
Ensure all existing tests pass, and write new unit tests in `tests/` for your additions:

```bash
python tests/test_suite.py
```

### 6. Submit a Pull Request
Commit your changes with clear messages, push them to your fork, and open a Pull Request against our `main` branch.

In your Pull Request:
1. Explain the purpose of the change.
2. Outline the solution.
3. List any testing completed.
4. Reference related issue IDs (e.g. `Closes #12`).
