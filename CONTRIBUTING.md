# Contributing to AI Video Restoration

Thank you for your interest in contributing! This project is primarily a
portfolio/research archive, but improvements, bug fixes, and documentation
enhancements are welcome.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Style](#coding-style)
- [Reporting Issues](#reporting-issues)

---

## Code of Conduct

Be respectful, constructive, and professional. Harassment of any kind will not
be tolerated.

---

## How to Contribute

There are several ways to contribute to this project:

| Type | Examples |
|---|---|
| 🐛 Bug Fix | Fix incorrect optical flow parameters, broken CSV parsing |
| 📝 Documentation | Improve README, add inline comments, fix typos |
| 🎨 Preview Site | UI/UX improvements to the `preview/` React app |
| ⚡ Performance | Speed up embedding generation, reduce memory usage |
| 🧪 Testing | Add unit tests for utility functions |
| 🔧 New Feature | Add a new restoration method, support additional video formats |

---

## Preview Development

See [preview/README.md](preview/README.md) for running the demo site locally.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- FFmpeg 6.0+ (on system PATH)
- Git

### Steps

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/ai-video-restoration.git
cd ai-video-restoration

# 3. Create a virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create a feature branch
git checkout -b feature/your-feature-name
```

---

## Pull Request Process

1. **Fork** the repository and create a branch from `main`.
2. **Make your changes** — keep commits small and focused.
3. **Write clear commit messages** following the format:
   ```
   type(scope): short description

   Longer description if needed.
   ```
   Types: `fix`, `feat`, `docs`, `refactor`, `perf`, `test`, `chore`

4. **Update the README or docs/** if your change affects the pipeline or usage.
5. **Add or update tests** in `tests/` for any new or changed utility functions.
6. **Run the test suite** locally before pushing (see [Testing](#testing) below).
7. **Open a Pull Request** against the `main` branch with a clear description
   of what was changed and why.
8. **Respond to review feedback** promptly.

---

## Testing

The project uses **pytest** for all utility tests.  The CI workflow
(`.github/workflows/tests.yml`) runs these automatically on every push and
pull request against `main`.

### Running tests locally

```bash
# Install test dependencies (if not already installed)
pip install pytest numpy opencv-python-headless

# Run all tests
pytest

# Run a specific test file
pytest tests/test_video_utils.py -v

# Run a specific test class or function
pytest tests/test_matcher_utils.py::TestBatchCosineSimilarity -v

# Stop on first failure
pytest -x
```

### Writing new tests

- Place test files in `tests/` with the naming pattern `test_<module_name>.py`.
- Use **synthetic NumPy arrays** and **`tmp_path` fixtures** — do not rely on
  real video files or network access in unit tests.
- For functions that call FFmpeg/OpenCV on real files, add a `@pytest.mark.skipif`
  guard that checks for the binary:
  ```python
  import shutil, pytest
  ffmpeg_available = pytest.mark.skipif(
      shutil.which("ffmpeg") is None, reason="ffmpeg not available"
  )
  ```
- Follow the `TestClassName` / `test_method_name` convention so pytest
  discovery works without configuration changes.

### What the CI checks

The GitHub Actions workflow runs on Python 3.10, 3.11, and 3.12 in parallel.
It installs `opencv-python-headless` (no display required) and runs:

```bash
pytest tests/ -v --tb=short
```

All tests must pass on all three versions before a PR can be merged.

---

## Coding Style

- Follow [PEP 8](https://peps.python.org/pep-0008/).
- Use type annotations (`def foo(x: int) -> str:`).
- Keep functions short and single-purpose.
- Add docstrings to all public functions.
- Prefer `pathlib.Path` over `os.path` for file operations.
- Use `tqdm` for any loop that processes more than a handful of items.

### Example

```python
def normalize_embeddings(embeddings: np.ndarray, epsilon: float = 1e-12) -> np.ndarray:
    """
    L2-normalize a 2D array of feature embeddings row-wise.

    Args:
        embeddings: Shape (N, D) float32 array of raw embeddings.
        epsilon: Small constant to avoid division by zero.

    Returns:
        Shape (N, D) float32 array of unit-norm embeddings.
    """
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    valid = norms[:, 0] > epsilon
    normalized = np.zeros_like(embeddings, dtype=np.float32)
    normalized[valid] = embeddings[valid] / norms[valid]
    return normalized
```

---

## Reporting Issues

When opening an issue, please include:

- **Python version** (`python --version`)
- **OS** (Windows 10/11, Ubuntu, macOS)
- **GPU / CPU** and CUDA version if applicable
- **Error traceback** (full, not truncated)
- **Steps to reproduce**

Use the appropriate issue template if one is available.

---

## License

By contributing to this project, you agree that your contributions will be
licensed under the [MIT License](LICENSE).

