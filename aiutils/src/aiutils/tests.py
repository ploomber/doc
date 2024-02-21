"""
Code for generating data for test cases
"""

from pathlib import Path
import requests


def download_arxiv_paper(paper_id: str, path_to_data: str):
    """
    Download papers from arxiv
    """

    url = f"https://arxiv.org/pdf/{paper_id}.pdf"

    path_to_data = Path(path_to_data)
    path_to_data.mkdir(exist_ok=True)
    path_to_paper = path_to_data / f"{paper_id}.pdf"

    if not path_to_paper.exists():
        response = requests.get(url)
        response.raise_for_status()

        with open(path_to_paper, "wb") as f:
            f.write(response.content)
