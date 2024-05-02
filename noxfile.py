import nox
from nox.sessions import Session

@nox.session
def package(session: Session) -> None:
    session.install('-r', 'requirements.txt')
    session.run(
        "pyinstaller", "--onefile",
        "--add-data=./src/faf/tools.py:./",
         "-n", "faf",
        "./src/faf/main.py",
        external=True,
    )
