# Pyco

A python-inspired, statically typed programming language.

Example:

```txt
def fib(n: int): int {
    a, b: int
    b = 1

    for _ in each(n) {
        swap: int = a
        a = b
        b = b + swap
    }

    return a
}

print(a)
```
