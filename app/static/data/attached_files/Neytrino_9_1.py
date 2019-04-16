class Bell:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def print_info(self):
        if not self.args and not self.kwargs:
            print('-')
        else:
            if self.kwargs is not None:
                now_len = 0
                length = len(self.kwargs)
                for name in sorted(self.kwargs):
                    now_len += 1
                    if now_len == length and len(self.args) != 0:
                        print(name + ':', self.kwargs[name] + ';', end='')
                    elif now_len != length:
                        print(name + ':', self.kwargs[name] + ', ', end='')
                    else:
                        print(name + ':', self.kwargs[name], end='')
            for i in range(len(self.args)):
                if i == 0:
                    if len(self.kwargs) == 0:
                        print(self.args[i], end='')
                    else:
                        print(' ' + self.args[i], end='')
                else:
                    print(', ' + self.args[i], end='')
            print()


class BellTower(Bell):
    def __init__(self, *args):
        self.bells = list(args)

    def sound(self):
        for i in range(len(self.bells)):
            self.bells[i].sound()
        print('...')

    def append(self, bell):
        self.bells.append(bell)


class BigBell(Bell):
    def __init__(self, *args, **kwargs):
        self.num = 0
        self.kwargs = kwargs
        self.args = args

    def sound(self):
        if self.num == 0:
            print('ding')
            self.num = 1
        else:
            print('dong')
            self.num = 0


class LittleBell(Bell):
    def sound(self):
        print('ding')


