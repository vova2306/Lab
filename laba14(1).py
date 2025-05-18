import math

def solve_quadratic(a, b, c):
    assert a != 0
    discriminant = b**2 - 4*a*c
    assert discriminant >= 0
    x1 = (-b + math.sqrt(discriminant)) / (2 * a)
    x2 = (-b - math.sqrt(discriminant)) / (2 * a)
    return (x1,) if discriminant == 0 else (x1, x2)

a, b, c = 1, -3, 2
print(solve_quadratic(a, b, c))
