# -*- encoding: utf-8 -*-


class A(object):
    def __init__(self, number):
        self.number = number

    # def __repr__(self):
    #     return str(self.number)

    def get_number(self):
        return self.number


class B(A):
    def __init__(self, number):
        super(B, self).__init__(number)

    def get_number(self):
        return super(B, self).get_number()

    def __call__(self, *args, **kwargs):
        return 123


if __name__ == '__main__':
    """use for test"""
    a=['ギガンティックO.T.N','スパイラルブレイカー']
    b=['或る街の白昼夢','戯言クライン','すきなの。','曖昧ばんび~な','Sweet Ices Cream','ばんび~の','終末一般論']

    for aa in a:
        for ab in b:
            print '{0}{1}'.format(aa,ab).decode('utf-8').encode('mbcs')