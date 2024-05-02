import nox
from nox.sessions import Session

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
