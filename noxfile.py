import nox
from nox.sessions import Session

@nox.session(name="test")
@nox.session(name="tests")
def run_tests(session: Session) -> None:
    """Run the test suite with pytest."""
    session.install('-r', 'requirements.txt')
    session.install('pytest-cov')  # Install pytest-cov for coverage reports
    # Use python -m pytest to include the current directory in the Python path
    session.run("python", "-m", "pytest", "--cov=src.faf")

@nox.session
def package(session: Session) -> None:
    session.install('-r', 'requirements.txt')
    session.run(
        "pyinstaller", "--onefile",
        "--hidden-import=tiktoken_ext.openai_public",
        "--hidden-import=tiktoken_ext", # required, as in: https://github.com/openai/tiktoken/issues/43
        "--add-data=./src/faf/tools.py:./",
        "-n", "faf",
        "./src/faf/main.py",
        external=True,
    )
