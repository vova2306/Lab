#реалізація кожної функції закоментована
def elk(x, k): #point a
    yield 1
    a = x
    c = 1
    for k in range(1, k+1):
        a *= (x**2)/(c*(c+2))
        c += 2
        yield a

#x, k = map(int, input().split())
#if __name__ == '__main__':
#    for a in elk(x, k):
#        print(a)

def S(n): #point b
    s = 1
    yield s
    c = 1
    a = -2/c
    for i in range(2, n+1):
        print(a, c)
        s = s + a
        c += 1
        a *= -2/c
        yield s

#n = int(input())
#if __name__ == '__main__':
#    for a in S(n):
#        pass
#    print(a)

def D(n): #point c
    yield 7
    yield 39

    d2, d1 = 7, 39
    for i in range(3, n+1):
        d2, d1 = d1, 7*d1 - 10*d2
        yield d1

#n = int(input())
#if __name__ == '__main__':
#    for d in D(n):
#        pass
#    print(d)

def R(n, u, v): #point d
    c = 2
    a = u
    b = v
    r = u*v/c
    yield r
    for i in range(2, n+1):
        a, b = 2*b + a, 2*a**2 + b
        c = c * (i + 1)
        r = r + a*b/c
        yield r

#if __name__ == '__main__':
#    for r in R(4, 1, 1):
#        pass
#    print(r)

def T(x, e):
    t1 = 1
    yield t1
    a = 1
    b = 2
    s = 1000000
    i = 2
    x0 = x
    while abs(s) >= e:
        t2 = t1 - (a/b)*x
        s = t2 - t1
        t1 = t2
        a = a * (i + 1)
        b = b * (i + 2)
        x = (-x) * x0
        i += 2
        yield t2

#x, e = map(float, input().split())
#if __name__ == '__main__':
#    for t2 in T(x, e):
#        pass
#    print(t2)



