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