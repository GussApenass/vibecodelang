type Username > string

interface > User [
    name: string
    age: number
]

var name: Username > "John"
var age: number > 20
var active: bool > true

out("Hello @{name}")
out("Age is @{age}")

if [name == "john" and active == true] {
    out("hello john")
} elseif [name == "admin"] {
    out("welcome admin")
} else {
    out("unknown user")
}