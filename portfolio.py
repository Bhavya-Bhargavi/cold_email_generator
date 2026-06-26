from pathlib import Path
import pandas as pd
import chromadb
import uuid


class Portfolio:
    def __init__(self, file_path=None):
        base_dir = Path(__file__).resolve().parent
        if file_path is None:
            candidates = [
                base_dir / "resource" / "my_portfolio.csv",
                base_dir.parent / "my_portfolio.csv",
                base_dir / "my_portfolio.csv",
            ]
            for candidate in candidates:
                if candidate.exists():
                    file_path = candidate
                    break
            else:
                file_path = candidates[0]

        self.file_path = Path(file_path).resolve()
        if not self.file_path.exists():
            raise FileNotFoundError(f"Portfolio CSV not found: {self.file_path}")

        self.data = pd.read_csv(self.file_path)
        self.chroma_client = chromadb.PersistentClient(str(base_dir.parent / "vectorstore"))
        self.collection = self.chroma_client.get_or_create_collection(name="portfolio")

    def load_portfolio(self):
        if not self.collection.count():
            for _, row in self.data.iterrows():
                self.collection.add(documents=row["Techstack"],
                                    metadatas={"links": row["Links"]},
                                    ids=[str(uuid.uuid4())])

    def query_links(self, skills):
        return self.collection.query(query_texts=skills, n_results=2).get('metadatas', [])