class Polynom:
    def __init__(self, mn=None):
        if isinstance(mn, Polynom):
            self.polynom = mn.polynom
        elif isinstance(mn, dict):
            self.polynom = mn
        elif poly is None:
            self.polynom = {}
        else:
            raise TypeError

    def _delzeros(self, mn=None):
        if mn==None:
            mn=self.polynom
        ppe={num1: mn[num1] for num1 in mn if mn[num1] != 0}
        if len(ppe) == 0:
            ppe[0] = 0
        return ppe

    def fileinputpoly(self, fname):
        f=open(fname)
        for tep in f:
            num1, num2 = map(float, tep.split())
            self.polynom[num1] = num2
        f.close()
        self.polynom=self._delzeros()

    def set(self, num1, num2):
        self.polynom[num1] = num2
        self.polynom=self._delzeros()

    def derivpoly(self, n=1):
        ppe = copy.deepcopy(self.polynom)
        for i in range(n):
            ppe = {num1-1:ppe[k]*num1 for num1 in ppe if num1!=0}
        return self._delzeros()

    def __getitem__(self, num1):
        try:
            return self.polynom[num1]
        except IndexError:
            return None

    def __call__(self, x):
        return sum([self.polynom[num1]*x**num1 for num1 in self.polynom])

    def __str__(self):
        temp1 = [str(self.polynom[num])+'x^'+str(num) for num in sorted(self.polynom, reverse=True)]
        t = '+'.join(temp1)
        return t

    def __sub__(self, o):
        e = copy.deepcopy(self.polynom)
        if isinstance(o, (float, int)):
            if 0 in e:
                e[0]-= o
                return Polynom(self._delzeros(e))
            else:
                e[0]=-o
                return Polynom(self._delzeros(e))
        elif isinstance(o, Polynom):
            e.update(o.polynom)
            new_poly={num1:self.polynom.get(num1, 0)-o.polynom.get(num1, 0) for num1 in e}
            return Polynom(self._delzeros(new_poly))
        else:
            raise TypeError('Немає сенсу!')

    def __add__(self, o):
        e = copy.deepcopy(self.polynom)
        if isinstance(o, (float, int)):
            if 0 in e:
                e[0] += o
                return Polynom(self._delzeros(e))
            else:
                e[0] = o
                return Polynom(self._delzeros(e))
        elif isinstance(o, Polynom):
            e.update(o.polynom)
            new_poly = {num1:self.polynom.get(num1, 0)+o.polynom.get(num1, 0) for num1 in e}
            return Polynom(self._delzeros(new_poly))
        else:
            raise TypeError('Немає сенсу!')

    def __setitem__(self, num1, num2):
        self.polynom[num1] = num2

    def __mul__(self, o):
        e = {}
        if isinstance(o, (float, int)):
            for num1 in self.polynom:
                e[num1]=self.polynom[num1]*o
            return Polynom(self._delzeros(p))
        elif isinstance(o, Polynom):
            for num01 in self.polynom:
                for num02 in o.polynom:
                    e[num01+num02]=e.get(num01+num02, 0)+self.polynom[num01]*o.polynom[num02]
            return Polynom(self._delzeros(e))
        else:
            raise TypeError('Немає сенсу!')

import copy
if __name__ == '__main__':
    m1 = Polynom({1: 6, 2: 9, 3: -2, 4: 0, 5: 4})
    m2 = Polynom({7: 2, 5: 1, 4: -1, 3: 10, 2: 9})
    temp = m1 + m2 * m1 + m2
    print('Многочлени:\np1 =', m1 ,'\np2 =', m2, '\n')
    print('Результати {}:'.format('p1 + p2 * p1 + p2'), '{}'.format(temp))
    print('Словником:', temp.polynom)
