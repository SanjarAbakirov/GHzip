"""
utils.py — вспомогательные функции для GHzip.
Отвечает за: чтение/запись байт, вычисление контрольной суммы CRC32.
"""

import zlib
import logging

logger = logging.getLogger(__name__)


def read_bytes(path: str) -> bytes:
    """Читает файл целиком и возвращает его содержимое как байты."""
    logger.debug(f"Читаю файл: {path}")
    with open(path, "rb") as f:
        data = f.read()
    logger.debug(f"Прочитано {len(data)} байт из {path}")
    return data


def write_bytes(path: str, data: bytes) -> None:
    """Записывает байты в файл по указанному пути."""
    logger.debug(f"Записываю {len(data)} байт в: {path}")
    with open(path, "wb") as f:
        f.write(data)
    logger.debug(f"Запись завершена: {path}")


def compute_crc32(data: bytes) -> int:
    """
    Вычисляет контрольную сумму CRC32 для проверки целостности данных.
    Возвращает беззнаковое 32-битное целое число.
    """
    checksum = zlib.crc32(data) & 0xFFFFFFFF
    logger.debug(f"CRC32 = {checksum:#010x}")
    return checksum


def verify_crc32(data: bytes, expected: int) -> bool:
    """
    Проверяет целостность данных, сравнивая CRC32 с ожидаемым значением.
    Возвращает True если данные не повреждены, False иначе.
    """
    actual = compute_crc32(data)
    if actual != expected:
        logger.error(f"CRC32 не совпадает: ожидалось {expected:#010x}, получено {actual:#010x}")
        return False
    return True