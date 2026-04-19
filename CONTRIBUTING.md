# Contributing to SmartBill Pro

Thank you for your interest in contributing to SmartBill Pro! 🎉

## Getting Started

1. **Fork** the repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/SmartBill.git
   cd SmartBill
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the app** to verify setup:
   ```bash
   python main.py
   ```

## Running Tests

```bash
python -m unittest tests.test_smartbill -v
```

All 59 tests must pass before submitting a pull request.

## Project Structure

```
modules/
├── config.py           # Constants, colors, fonts
├── db_manager.py       # Database operations
├── validators.py       # Input validation
├── report_generator.py # Report generation
└── backup_manager.py   # Backup & restore
tests/
└── test_smartbill.py   # Unit tests
```

## Code Style Guidelines

- Follow **PEP 8** conventions
- Use **docstrings** for all public methods
- Keep functions focused and under 50 lines
- Use type hints where practical
- All database operations go in `db_manager.py`
- All validation logic goes in `validators.py`

## Submitting Changes

1. Create a **feature branch**: `git checkout -b feature/your-feature`
2. Make your changes
3. Run the tests: `python -m unittest tests.test_smartbill -v`
4. Commit: `git commit -m "Add: description of your change"`
5. Push: `git push origin feature/your-feature`
6. Open a **Pull Request**

## Reporting Bugs

Open an issue with:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Python version (`python --version`)
- OS version

## Feature Requests

Open an issue with the `enhancement` label describing:
- What feature you'd like
- Why it would be useful
- Any implementation ideas

---

Thank you for helping make SmartBill Pro better! 🚀
