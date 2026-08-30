import os;
import zipfile;

#CLI

# python main.py pack input.txt -o archive.ghzip
# python main.py unpack archive.ghzip -o output_folder


def create_archive(file_name, archive_name):
    with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(file_name)
    print(f"Файл {file_name} успешно архивирован в {archive_name}")

# Пример вызова
create_archive('document.txt', 'my_archive.zip')



import zipfile
from pathlib import Path

def create_archive_from_folder(folder_path, archive_name):
    folder = Path(folder_path)
    with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in folder.rglob('*'):
            if file_path.is_file():
                zipf.write(file_path, arcname=file_path.relative_to(folder))