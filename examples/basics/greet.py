"""
Interactive greeting using Str.input().

Smalltalk:
    | name |
    name := UIManager default request: 'What is your name? '.
    Transcript showCr: 'Hello, ', name, '!'.
"""

name = "What is your name? ".input()
("Hello, " + name + "!").print()
