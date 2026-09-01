import sys # command line argument
import os
from compress import compress, decompress

def pack(input_path):
    with open(input_path, "rb") as f:
        original_data = f.read() # context manager

    compressed_data = compress(original_data)  # БАГ 1 исправлен: вызываем compress()

    output_path = input_path + ".ghzip"
    with open(output_path, "wb") as f:
        f.write(compressed_data)

    print(f"Исходный размер: {len(original_data)} байт")
    print(f"Сжатый размер:  {len(compressed_data)} байт")
    if len(compressed_data) > len(original_data):
        print("Cжатый файл больше оригинала")

def unpack(input_path):
    with open(input_path, "rb") as f:
        compressed_data = f.read()

    original_data = decompress(compressed_data)

    output_path = input_path.replace(".ghzip", "") # delete .ghzip extention

    # Проверка: не перезаписывать существующий файл молча
    if os.path.exists(output_path):
        answer = input(f"Файл '{output_path}' уже существует. Перезаписать? (y/n): ")
        if answer.lower() != "y":
            print("Отменено.")
            return

    with open(output_path, "wb") as f:
        f.write(original_data)

    print(f"Распаковка завершена!")
    print(f"Восстановлено: {len(original_data)} байт")

# БАГ 3 исправлен: if __name__ на уровне файла (без отступа)
if __name__ == "__main__": # service var, given to each arch file
    if len(sys.argv) != 3:
        sys.exit(1)

    command = sys.argv[1] # "pack" or "unpack"
    filename = sys.argv[2] #file name

    if command == "pack":
        pack(filename)
    elif command == "unpack":
        unpack(filename)
    else:
        sys.exit(1)