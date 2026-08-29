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