import os
import zipfile


class ZipProgram:

    def __init__(self, archive_name):
        # имя архива, например "my.zip"
        self.archive_name = archive_name

    def create(self, folder_path):
        """Создаёт zip-архив из папки."""
        # проверяем, что папка существует
        if not os.path.exists(folder_path):
            print("Папка не найдена!")
            return

        # открываем zip на запись
        with zipfile.ZipFile(self.archive_name, "w") as zf:
            # проходим по всем файлам в папке
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    # полный путь к файлу на диске
                    file_path = os.path.join(root, file)
                    # имя файла внутри архива (без лишнего пути)
                    arc_name = os.path.relpath(file_path, folder_path)
                    # добавляем файл в архив
                    zf.write(file_path, arc_name)
                    print("Добавлен:", arc_name)

        print("Архив создан:", self.archive_name)

    def extract(self, output_folder):
        """Распаковывает zip-архив в папку."""
        if not os.path.exists(self.archive_name):
            print("Архив не найден!")
            return

        # создаём папку, если её нет
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        with zipfile.ZipFile(self.archive_name, "r") as zf:
            zf.extractall(output_folder)
            print("Распаковано в:", output_folder)

    def show_files(self):
        """Показывает список файлов в архиве."""
        if not os.path.exists(self.archive_name):
            print("Архив не найден!")
            return

        with zipfile.ZipFile(self.archive_name, "r") as zf:
            print("Файлы в архиве:")
            for name in zf.namelist():
                print(" -", name)


# --- запуск программы ---
if __name__ == "__main__":
    print("=== Zip Program ===")
    print("1 - создать архив")
    print("2 - распаковать архив")
    print("3 - показать файлы в архиве")

    choice = input("Выберите действие: ")

    if choice == "1":
        folder = input("Путь к папке: ")
        name = input("Имя архива (например data.zip): ")
        program = ZipProgram(name)
        program.create(folder)

    elif choice == "2":
        name = input("Имя архива: ")
        output = input("Куда распаковать: ")
        program = ZipProgram(name)
        program.extract(output)

    elif choice == "3":
        name = input("Имя архива: ")
        program = ZipProgram(name)
        program.show_files()

    else:
        print("Неизвестная команда")
