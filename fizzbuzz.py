# fizzbuzz em uma versão infectada por smalltalk
"""
Notas:
- Funções são utilizadas para simular blocos de código presentes em smalltalk
"""
from collections import deque

from forbiddenfruit import curse


def if_true(self, block):
    # somente executa a função caso self 
    # seja algo avaliado como verdadeiro (truthy)
    # isto é chamado de curto circuito
    self and block()
    return self


def if_false(self, block):
    # somente executa a função caso self 
    # seja algo avaliado como falso (falsy)
    # isto é chamado de curto circuito
    not self and block()
    return self


def println(self):
    """Prints the values to a stream, or to sys.stdout by default.

    >>> "Fizz".print()
    Fizz
    >>> "FizzBuzz".print()
    FizzBuzz
    """
    print(self)


def do(self, block):
    """Evaluate the receiver for each element in aBlock.

    >>> range(1, 11).do(lambda number: number.print())
    """
    deque(map(block, self), maxlen=0)
    return self

# curse é uma maneira de modificar tipos builtins da linguagem
curse(bool, "if_true", if_true)
curse(bool, "if_false", if_false)
curse(str, "print", println)
curse(int, "print", println)
curse(range, "do", do)

"""
Explicação:
Nós adicionamos um método "do" em objetos do tipo "range" que avalia um bloco
para cada elemento no intervalo. 
Este bloco faz a avaliação de um número verificando se o mesmo 
é divisível por 15, e isto resulta em um objeto booleano.
Para este objeto booleano, duas mensagens são enviadas, uma que diz que caso sua avaliação
seja verdadeira, o valor "FizzBuzz" deve ser exibido em tela. A outra informa que se o objeto é 
avaliado como falso, um novo objeto booleano deve ser retornado. Este novo objeto
booleano recebe duas mensagens, uma informando ao objeto que caso sua avaliação seja verdadeira,
a mensagem "Buzz" deve ser exibida na tela e outra que caso sua avaliação seja falsa um 
novo objeto booleano deve ser retornado.
Por fim este novo objeto booleano também recebe duas mensagens, uma informando que se sua avaliação for verdadeira
"Fizz" deve ser exibido em tela e outra que caso seja avaliado como falso, o número deve ser exibido na tela.
"""
range(1, 101).do( 
    # lambdas também são utilizadas para simular blocos 
    lambda number: (number % 15 == 0)
    .if_true("FizzBuzz".print)
    .if_false(
        lambda: (number % 5 == 0)
        .if_true("Buzz".print)
        .if_false(
            lambda: (number % 3 == 0)
            .if_true("Fizz".print)
            .if_false(number.print)
        )
    )
)
# Nota: É importante notar que no fim o que temos são objetos trocando mensagens entre si.
