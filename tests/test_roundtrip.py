"""
tests/test_roundtrip.py — тесты целостности GHzip.

Проверяем главное правило: упаковал → распаковал → получил то же самое.
"""

import os
import sys
import tempfile
import unittest

# Добавляем корень проекта в путь, чтобы импорты работали из папки tests/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from archive import list_contents, pack, unpack
from compress import rle_decode, rle_encode


# ─── Тесты алгоритма сжатия ──────────────────────────────────────────────────

class TestRLE(unittest.TestCase):
    """Тесты алгоритма RLE encode/decode."""

    def test_empty_bytes(self):
        """Пустые данные остаются пустыми."""
        self.assertEqual(rle_encode(b""), b"")
        self.assertEqual(rle_decode(b""), b"")

    def test_single_byte(self):
        """Один байт корректно кодируется и декодируется."""
        data = b"A"
        self.assertEqual(rle_decode(rle_encode(data)), data)

    def test_repeating_bytes(self):
        """Повторяющиеся байты сжимаются."""
        data = b"AAABBBCC"
        encoded = rle_encode(data)
        # 3A + 3B + 2C → 3 пары = 6 байт (вместо 8)
        self.assertEqual(len(encoded), 6)
        self.assertEqual(rle_decode(encoded), data)

    def test_no_repeats(self):
        """Уникальные байты без сжатия (worst case — каждый байт 1 раз)."""
        data = b"ABCD"
        encoded = rle_encode(data)
        self.assertEqual(rle_decode(encoded), data)

    def test_max_run_length(self):
        """255 одинаковых байт = максимальная длина серии."""
        data = b"X" * 255
        encoded = rle_encode(data)
        self.assertEqual(len(encoded), 2)   # одна пара (255, 'X')
        self.assertEqual(rle_decode(encoded), data)

    def test_over_max_run_length(self):
        """256+ одинаковых байт разбиваются на несколько серий."""
        data = b"X" * 300
        encoded = rle_encode(data)
        self.assertEqual(rle_decode(encoded), data)

    def test_binary_data(self):
        """Работает с произвольными бинарными данными."""
        data = bytes(range(256))
        self.assertEqual(rle_decode(rle_encode(data)), data)


# ─── Тесты архива ─────────────────────────────────────────────────────────────

class TestRoundtrip(unittest.TestCase):
    """Тесты pack → unpack: данные должны совпадать с оригиналом."""

    def setUp(self):
        """Создаём временную директорию для каждого теста."""
        self.tmp = tempfile.mkdtemp()

    def _make_file(self, name: str, content: bytes) -> str:
        """Вспомогательный метод: создаёт временный файл с заданным содержимым."""
        path = os.path.join(self.tmp, name)
        with open(path, "wb") as f:
            f.write(content)
        return path

    def test_single_text_file(self):
        """Упаковка и распаковка одного текстового файла."""
        content = b"Hello, GHzip! \xd0\x9f\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82!"
        src = self._make_file("hello.txt", content)
        archive = os.path.join(self.tmp, "test.ghzip")
        out_dir = os.path.join(self.tmp, "out_single")

        pack([src], archive)
        unpack(archive, out_dir)

        restored_path = os.path.join(out_dir, "hello.txt")
        self.assertTrue(os.path.exists(restored_path))
        with open(restored_path, "rb") as f:
            self.assertEqual(f.read(), content)

    def test_multiple_files(self):
        """Упаковка и распаковка нескольких файлов."""
        files_data = {
            "a.txt": b"File A content " * 10,
            "b.txt": b"File B content " * 20,
            "c.bin": bytes(range(256)),
        }
        paths = [self._make_file(name, data) for name, data in files_data.items()]
        archive = os.path.join(self.tmp, "multi.ghzip")
        out_dir = os.path.join(self.tmp, "out_multi")

        pack(paths, archive)
        unpack(archive, out_dir)

        for name, original_data in files_data.items():
            restored = os.path.join(out_dir, name)
            self.assertTrue(os.path.exists(restored), f"Файл не найден: {name}")
            with open(restored, "rb") as f:
                self.assertEqual(f.read(), original_data, f"Данные не совпадают: {name}")

    def test_empty_file(self):
        """Пустой файл упаковывается и распаковывается корректно."""
        src = self._make_file("empty.txt", b"")
        archive = os.path.join(self.tmp, "empty.ghzip")
        out_dir = os.path.join(self.tmp, "out_empty")

        pack([src], archive)
        unpack(archive, out_dir)

        restored = os.path.join(out_dir, "empty.txt")
        self.assertTrue(os.path.exists(restored))
        with open(restored, "rb") as f:
            self.assertEqual(f.read(), b"")

    def test_list_contents(self):
        """list_contents возвращает правильные имена файлов."""
        names = ["alpha.txt", "beta.txt", "gamma.bin"]
        paths = [self._make_file(n, b"data") for n in names]
        archive = os.path.join(self.tmp, "list_test.ghzip")

        pack(paths, archive)
        contents = list_contents(archive)

        self.assertEqual(sorted(contents), sorted(names))

    def test_corrupted_archive_raises(self):
        """Повреждённый архив вызывает ошибку ValueError."""
        src = self._make_file("file.txt", b"Some content")
        archive = os.path.join(self.tmp, "corrupted.ghzip")

        pack([src], archive)

        # Портим архив: переписываем несколько байт в середине
        with open(archive, "r+b") as f:
            f.seek(15)
            f.write(b"\xFF\xFF\xFF\xFF")

        out_dir = os.path.join(self.tmp, "out_corrupted")
        with self.assertRaises(ValueError):
            unpack(archive, out_dir)

    def test_wrong_magic_raises(self):
        """Файл с неверной сигнатурой вызывает ошибку ValueError."""
        fake = os.path.join(self.tmp, "fake.ghzip")
        with open(fake, "wb") as f:
            f.write(b"WRONGMAGIC_DATA")

        with self.assertRaises(ValueError):
            unpack(fake, self.tmp)

    def test_binary_data_roundtrip(self):
        """Бинарные данные (все 256 значений байт) корректно проходят roundtrip."""
        content = bytes(range(256)) * 100
        src = self._make_file("binary.bin", content)
        archive = os.path.join(self.tmp, "binary.ghzip")
        out_dir = os.path.join(self.tmp, "out_binary")

        pack([src], archive)
        unpack(archive, out_dir)

        with open(os.path.join(out_dir, "binary.bin"), "rb") as f:
            self.assertEqual(f.read(), content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
