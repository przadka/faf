import nox
from nox.sessions import Session

@nox.session
def package(session: Session) -> None:
    session.install('-r', 'requirements.txt')
    session.run(
        "pyinstaller", "--onefile",
        "--add-data=/home/michal/.virtualenvs/langchain/lib/python3.10/site-packages/langchain/chains/llm_summarization_checker/prompts/:langchain/chains/llm_summarization_checker/prompts/",
        "--add-data=./src/faf/helpers.py:./",
        "--add-data=./src/faf/tools.py:./",
        "./src/faf/main.py",
        external=True,
    )
