from zipfile import Path

class ReadFolderRepository:
    def read_folder_repository(folder_path: str) -> str:
        """
        Read all text files in a folder and concatenate their contents.
        """
        all_text = []
        for file_path in Path(folder_path).glob("*.txt"):
            with open(file_path, 'r', encoding='utf-8') as f:
                all_text.append(f.read())
        return "\n".join(all_text)