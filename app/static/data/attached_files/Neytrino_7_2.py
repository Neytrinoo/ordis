def get_result(path):
    with open(path, 'r') as f:
        record = int(f.readline())
    return record


def set_result(path, result):
    with open(path, 'w') as f:
        f.write(str(result))


def clear(path):
    set_result(path, 0)