# -*- encoding: utf-8 -*-


class A(object):
    def __init__(self, number):
        self.number = number

    def __repr__(self):
        return str(self.number)

    def get_number(self):
        return self.number


class B(A):
    def __init__(self, number):
        super(B, self).__init__(number)

    def get_number(self):
        return super(B, self).get_number()


if __name__ == '__main__':
    """use for test"""

    b = B(1234)


    def timeout(a,**kwargs):
        print b
        print kwargs

    def time(a,b='123',**kwargs):
        kwargs['b']=b
        timeout(a,**kwargs)

    time(1,adb='213',ewr='234',kls=12)