"""
main.py — точка входа CLI утилиты GHzip.

Использование:
  python main.py pack   <file1> [file2 ...] -o archive.ghzip
  python main.py unpack <archive.ghzip>    -o ./output_folder/
  python main.py list   <archive.ghzip>
"""

import argparse
import logging
import sys

from archive import list_contents, pack, unpack


def setup_logging(verbose: bool) -> None:
    """Настраивает логирование: --verbose включает DEBUG уровень."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(levelname)s | %(name)s | %(message)s",
    )


def cmd_pack(args: argparse.Namespace) -> int:
    """Обработчик команды pack."""
    try:
        pack(args.files, args.output)
        return 0
    except FileNotFoundError as e:
        print(f"❌ Ошибка: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}", file=sys.stderr)
        return 1


def cmd_unpack(args: argparse.Namespace) -> int:
    """Обработчик команды unpack."""
    try:
        unpack(args.archive, args.output)
        return 0
    except ValueError as e:
        print(f"❌ Ошибка: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}", file=sys.stderr)
        return 1


def cmd_list(args: argparse.Namespace) -> int:
    """Обработчик команды list."""
    try:
        names = list_contents(args.archive)
        print(f"📦 Содержимое архива: {args.archive}")
        print(f"   Файлов: {len(names)}")
        print()
        for i, name in enumerate(names, start=1):
            print(f"  {i:3}. {name}")
        return 0
    except ValueError as e:
        print(f"❌ Ошибка: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    """Создаёт и возвращает парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog="ghzip",
        description="GHzip — утилита для упаковки и распаковки файлов (.ghzip)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Примеры:\n"
            "  python main.py pack document.txt photo.png -o archive.ghzip\n"
            "  python main.py unpack archive.ghzip -o ./extracted/\n"
            "  python main.py list archive.ghzip\n"
        ),
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Включить подробный вывод для отладки",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="КОМАНДА")
    subparsers.required = True

    # ── pack ──────────────────────────────────────────────────────────────────
    pack_parser = subparsers.add_parser(
        "pack",
        help="Упаковать файлы в архив .ghzip",
    )
    pack_parser.add_argument(
        "files",
        nargs="+",
        metavar="ФАЙЛ",
        help="Файлы для упаковки (можно указать несколько)",
    )
    pack_parser.add_argument(
        "-o", "--output",
        required=True,
        metavar="АРХИВ",
        help="Путь к создаваемому архиву (например: archive.ghzip)",
    )
    pack_parser.set_defaults(func=cmd_pack)

    # ── unpack ────────────────────────────────────────────────────────────────
    unpack_parser = subparsers.add_parser(
        "unpack",
        help="Распаковать архив .ghzip",
    )
    unpack_parser.add_argument(
        "archive",
        metavar="АРХИВ",
        help="Путь к архиву .ghzip",
    )
    unpack_parser.add_argument(
        "-o", "--output",
        default=".",
        metavar="ПАПКА",
        help="Папка для извлечённых файлов (по умолчанию: текущая папка)",
    )
    unpack_parser.set_defaults(func=cmd_unpack)

    # ── list ──────────────────────────────────────────────────────────────────
    list_parser = subparsers.add_parser(
        "list",
        help="Показать содержимое архива .ghzip",
    )
    list_parser.add_argument(
        "archive",
        metavar="АРХИВ",
        help="Путь к архиву .ghzip",
    )
    list_parser.set_defaults(func=cmd_list)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    setup_logging(args.verbose)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())