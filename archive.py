"""
archive.py — упаковка и распаковка файлов в формат .ghzip.

Формат файла .ghzip:
  ┌──────────────────────────────────┐
  │ MAGIC     5 bytes  "GHZIP"       │  ← идентификатор формата
  │ VERSION   1 byte   0x01          │  ← версия формата
  │ CRC32     4 bytes  uint32 BE     │  ← контрольная сумма всего блока данных
  │ N_FILES   4 bytes  uint32 BE     │  ← количество файлов в архиве
  ├──────────────────────────────────┤
  │ --- повторяется N раз ---        │
  │ NAME_LEN  2 bytes  uint16 BE     │  ← длина имени файла
  │ NAME      N bytes  UTF-8         │  ← имя файла (относительный путь)
  │ DATA_LEN  4 bytes  uint32 BE     │  ← размер сжатых данных
  │ DATA      M bytes                │  ← сжатые данные
  └──────────────────────────────────┘
"""

import logging
import os
import struct

from compress import compress, decompress
from utils import compute_crc32, read_bytes, verify_crc32, write_bytes

logger = logging.getLogger(__name__)

MAGIC = b"GHZIP"
VERSION = 0x01


# ─── Упаковка ─────────────────────────────────────────────────────────────────

def pack(file_paths: list[str], archive_path: str) -> None:
    """
    Упаковывает список файлов в один архив .ghzip.

    Args:
        file_paths:   список путей к файлам для упаковки
        archive_path: путь к создаваемому архиву
    """
    logger.info(f"Упаковка {len(file_paths)} файл(ов) → {archive_path}")

    # Собираем блок данных (все файлы)
    data_block = bytearray()
    data_block += struct.pack(">I", len(file_paths))  # N_FILES

    for file_path in file_paths:
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        raw = read_bytes(file_path)
        compressed = compress(raw)

        name_bytes = os.path.basename(file_path).encode("utf-8")
        logger.debug(
            f"  {file_path}: {len(raw)} → {len(compressed)} байт "
            f"({100 * len(compressed) / max(len(raw), 1):.0f}%)"
        )

        data_block += struct.pack(">H", len(name_bytes))   # NAME_LEN
        data_block += name_bytes                           # NAME
        data_block += struct.pack(">I", len(compressed))  # DATA_LEN
        data_block += compressed                           # DATA

    # Считаем CRC32 блока данных
    checksum = compute_crc32(bytes(data_block))

    # Пишем итоговый файл
    with open(archive_path, "wb") as f:
        f.write(MAGIC)                           # 5 bytes
        f.write(bytes([VERSION]))                # 1 byte
        f.write(struct.pack(">I", checksum))     # 4 bytes
        f.write(data_block)                      # остальное

    logger.info(f"Архив создан: {archive_path} ({os.path.getsize(archive_path)} байт)")
    print(f"✅ Архив создан: {archive_path}  ({len(file_paths)} файл(ов))")


# ─── Распаковка ───────────────────────────────────────────────────────────────

def unpack(archive_path: str, output_dir: str) -> list[str]:
    """
    Распаковывает архив .ghzip в указанную папку.

    Args:
        archive_path: путь к архиву .ghzip
        output_dir:   папка назначения

    Returns:
        Список путей к извлечённым файлам.
    """
    logger.info(f"Распаковка {archive_path} → {output_dir}")

    raw = read_bytes(archive_path)

    # ── Проверяем заголовок ──────────────────────────────────────────────────
    if len(raw) < 10:
        raise ValueError("Файл слишком маленький — не является архивом GHzip")

    magic = raw[:5]
    if magic != MAGIC:
        raise ValueError(f"Неверная сигнатура файла: {magic!r}. Ожидалось {MAGIC!r}")

    version = raw[5]
    if version != VERSION:
        raise ValueError(f"Неподдерживаемая версия формата: {version}. Поддерживается {VERSION}")

    stored_crc = struct.unpack(">I", raw[6:10])[0]
    data_block  = raw[10:]

    if not verify_crc32(data_block, stored_crc):
        raise ValueError("❌ Архив повреждён: контрольная сумма CRC32 не совпадает!")

    # ── Читаем файлы ─────────────────────────────────────────────────────────
    os.makedirs(output_dir, exist_ok=True)
    idx = 0

    n_files = struct.unpack(">I", data_block[idx:idx+4])[0]; idx += 4
    logger.debug(f"Файлов в архиве: {n_files}")

    extracted: list[str] = []
    for i in range(n_files):
        name_len = struct.unpack(">H", data_block[idx:idx+2])[0]; idx += 2
        name = data_block[idx:idx+name_len].decode("utf-8"); idx += name_len
        data_len = struct.unpack(">I", data_block[idx:idx+4])[0]; idx += 4
        compressed = data_block[idx:idx+data_len]; idx += data_len

        decompressed = decompress(compressed)
        out_path = os.path.join(output_dir, name)
        write_bytes(out_path, decompressed)

        logger.debug(f"  Извлечён: {out_path} ({len(decompressed)} байт)")
        print(f"  📄 {name}  ({len(decompressed)} байт)")
        extracted.append(out_path)

    print(f"✅ Распаковано {len(extracted)} файл(ов) в: {output_dir}")
    return extracted


# ─── Просмотр содержимого ─────────────────────────────────────────────────────

def list_contents(archive_path: str) -> list[str]:
    """
    Возвращает список имён файлов внутри архива без распаковки.

    Args:
        archive_path: путь к архиву .ghzip

    Returns:
        Список имён файлов.
    """
    logger.info(f"Просмотр содержимого: {archive_path}")

    raw = read_bytes(archive_path)

    if len(raw) < 10 or raw[:5] != MAGIC:
        raise ValueError("Файл не является архивом GHzip")

    stored_crc = struct.unpack(">I", raw[6:10])[0]
    data_block  = raw[10:]

    if not verify_crc32(data_block, stored_crc):
        raise ValueError("❌ Архив повреждён: CRC32 не совпадает")

    idx = 0
    n_files = struct.unpack(">I", data_block[idx:idx+4])[0]; idx += 4
    names: list[str] = []

    for _ in range(n_files):
        name_len = struct.unpack(">H", data_block[idx:idx+2])[0]; idx += 2
        name = data_block[idx:idx+name_len].decode("utf-8"); idx += name_len
        data_len = struct.unpack(">I", data_block[idx:idx+4])[0]; idx += 4
        idx += data_len   # пропускаем данные
        names.append(name)

    return names
