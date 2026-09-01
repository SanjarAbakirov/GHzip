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
# там по два байта, так как 3А 2Е и т.д. i - стоим с позиции и считаем пары 

    while i < len(data):
        #  сколько раз повторяется символ - append(count)
        count = data[i]
        byte = data[i + 1]
        result.extend([byte] * count) # все элементы списка
        i += 2
    return bytes(result)



            

            
