function sum[a: number, b: number] > number {
    return a + b
}

var result: number > sum(1, 3)
out("Result is @{result}")

for [i: number = 0; i < 3; i = i + 1] {
    out("for loop @{i}")
}

var x: number > 0
while [x < 3] {
    out("while loop @{x}")
    x = x + 1
}
