#RLE

def compress(data):
    result = []
    i = 0

    while i < len(data):
        count = 1
        while i + count < len(data) and data[i] == data[i + count] and count < 255:
            count += 1
        result.append(count)
        result.append(data[i])
        i += count

    return bytes(result)


def decompress(data):
    result = []
    i = 0
    while i < len(data):
        count = data[i]      # from append(count) — сколько раз
        byte  = data[i + 1]  # который байт повторяется
        result.extend([byte] * count)
        i += 2

    return bytes(result)


# ─────────────────────────────────────────────
# HUFFMAN — Шаг 1: Таблица частот
# ─────────────────────────────────────────────
# Идея: чем чаще байт встречается в файле,
# тем короче код мы ему назначим.
# Сначала нужно узнать — сколько раз встречается каждый байт.
#
# Пример: b"AAABBC"
#   → {65: 3, 66: 2, 67: 1}   (65='A', 66='B', 67='C')

def build_freq_table(data: bytes) -> dict[int, int]:
    freq = {}
    for byte in data:
        freq[byte] = freq.get(byte, 0) + 1
    return freq
