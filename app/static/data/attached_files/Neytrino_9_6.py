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

    def print_info(self):
        for i in range(len(self.bells)):
            print(i + 1, self.bells[i].class_name())
            self.bells[i].print_info()
        print('\n')


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

    def class_name(self):
        return 'BigBell'


class LittleBell(Bell):
    def sound(self):
        print('ding')

    def class_name(self):
        return 'LittleBell'


class SizedBellTower(BellTower):
    def __init__(self, *args, size=10):
        self.size = size
        self.bells = []
        for i in range(len(args)):
            self.append(args[i])

    def append(self, bell):
        if len(self.bells) >= self.size:
            del self.bells[0]
            self.bells.append(bell)
        else:
            self.bells.append(bell)


class TypedBellTower(BellTower):
    def __init__(self, *args, bell_type=LittleBell):
        self.bell_type = bell_type
        self.bells = []
        for i in range(len(args)):
            self.append(args[i])

    def append(self, bell):
        if type(bell) == self.bell_type:
            self.bells.append(bell)


