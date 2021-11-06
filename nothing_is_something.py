# baseado na palestra: Nothing is something - Sandi Metz
# https://www.youtube.com/watch?v=OMPfEXIlTVE&t=562s&ab_channel=Confreaks

# envia mensagem ao objeto 1 para invocar o método bit_length
(1).bit_length()
# outra maneira de fazer o mesmo
getattr(1, "bit_length")()
# invoca a função embutida str() sobre o número 1, retornando um objeto string
str(1)
# Nós podemos também chamar o método dunder str, é equivalente,
# mas não é recomendado
(1).__str__()
# envia a mensagem __str__ para o objeto e chama o método
getattr(1, "__str__")()

# acessa a classe do objeto
(1).__class__

# diferente do ruby, True e False são instâncias de bool
(True).__class__
(False).__class__

# objetos truthy em Python são objetos que __bool__ retorna True
# falsy returna False


class Truthy:
    def __bool__(self):
        return True


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


# vamos amaldiçoar os booleanos
from forbiddenfruit import curse  # noqa: E402

# Vamos adicionar dois novos métodos para a classe bool
curse(bool, "if_true", if_true)
curse(bool, "if_false", if_false)

# Vamos utilizar mensagens ao invés de condicionais
# Como a expressão é verdadeira, o bloco é avaliado
(1 == 1).if_true(lambda: print("evaluated block"))
# Não é avaliado porque a expressão é verdadeira
(1 == 1).if_false(lambda: print("block is ignored"))
# Como a expressão é falsa, o bloco não é avaliado
(1 == 2).if_true(lambda: print("block is ignored"))
# Avaliado porque a expressão é falsa
(1 == 2).if_false(lambda: print("evaluated block"))

# Lembrando que qualquer objeto pode ser avaliado como verdadeiro ou falso
# vamos amaldiçoar a classe object
curse(object, "if_true", if_true)
curse(object, "if_false", if_false)

"anything".if_true(lambda: print("evaluated block"))
"anything".if_false(lambda: print("ignored block"))

None.if_true(lambda: print("ignored block"))
None.if_false(lambda: print("evaluated block"))

# Não é sobre mudar o Python
# É uma questão de evitar if's e mudar sua mentalidade

# Esta classe simula algo que parece uma ORM


class Animal:

    # apenas para simular um conteúdo
    repository = ["pig", "sheep"]

    def __init__(self, name):
        self.name = name

    @classmethod
    def find(cls, id_):
        if id_ not in cls.repository:
            return None
        return cls(id_)

    def __str__(self):
        return f"Animal({self.name})"


# retorna um animal se existir, senão None
print(Animal.find("pig"))
print(Animal.find(""))

ids = ["pig", "", "sheep"]

# Em Python, objetos de sequência como lista não tem
# um método map, ao invés disto, temos uma função embutida
# map que recebe uma função e um ou
# vários iteráveis (objetos que seguem o protocolo de iterável)
animals = map(Animal.find, ids)

# nós também não temos um método "each"
# o código abaixo irá falhar
# for animal in animals:
#     print(animal.name)

# nota: map e for não são infectados por SmallTalk mas
# eu decidi manter isso por enquanto

# If you send it a message, nil is something. - Sandi Metz
# Se você enviar uma mensagem, nil é algo. - Sandi Metz

# Poderiamos utilizar a captura de exceções
# for animal in animals:
#     try:
#         print(animal.name)
#     except AttributeError:
#         print("no animal")
# try é um if que depende de execução de código
# e então talvez eu tenha isso em muitas partes


class MissingAnimal:
    @property
    def name(self):
        return "no animal"


# envolvido para evitar repetir if
# em alguns lugares
class GuaranteedAnimal:
    @classmethod
    def find(cls, id_):
        return Animal.find(id_) or MissingAnimal()


# utilize GuaranteedAnimal e tenha certeza de que um animal será retornado
animals = map(GuaranteedAnimal.find, ids)
for animal in animals:
    print(animal.name)

# Orientação a objetos é sobre objetos e mensagens

# O código abaixo está comentado para não conflitar com
# sua respectiva refatoração que aparece mais abaixo

# A classe house que recita o texto
# class House:
#     @property
#     def data(self):
#         return [
#             "the horse and the hound and the horn that belonged to",
#             "the farmer sowing his corn that kept",
#             "the rooster that crowed in the morn that woke",
#             "the priest all shaven and shorn that married",
#             "the man all tattered and torn that kissed",
#             "the maiden all forlorn that milked",
#             "the cow with the crumpled horn that tossed",
#             "the dog that worried",
#             "the cat that killed",
#             "the rat that ate",
#             "the malt that lay in",
#             "the house that Jack built",
#         ]

#     def recite(self):
#         return "\n".join(self.line(i) for i, _ in enumerate(self.data, 1))

#     def line(self, number):
#         return f"This  is {self._phrase(number)}\n"

#     def _phrase(self, number):
#         return " ".join(self.data[-number:])


# print(House().line(12))
# print(House().recite())

import random  # noqa: E402


def shuffle(self):
    """Shuffle the sequence x in place.

    >>> [1, 2, 3].shuffle()
    [3, 1, 2]
    """
    data = self.copy()
    random.shuffle(data)
    return data


# apenas para diversão, eu adicionarei um método de embaralhamento
# em listas
curse(list, "shuffle", shuffle)

# RandomHouse "é uma" casa que embaralha o texto
# class RandomHouse(House):
#     @cached_property
#     def data(self):
#         return super().data.shuffle()


# randomhouse = RandomHouse()
# print(randomhouse.line(1))
# print(randomhouse.line(2))
# print(randomhouse.line(3))
# print(randomhouse.line(12))


# class House:
#     @property
#     def data(self):
#         return [
#             "the horse and the hound and the horn that belonged to",
#             "the farmer sowing his corn that kept",
#             "the rooster that crowed in the morn that woke",
#             "the priest all shaven and shorn that married",
#             "the man all tattered and torn that kissed",
#             "the maiden all forlorn that milked",
#             "the cow with the crumpled horn that tossed",
#             "the dog that worried",
#             "the cat that killed",
#             "the rat that ate",
#             "the malt that lay in",
#             "the house that Jack built",
#         ]

#     def recite(self):
#         return "\n".join(self.line(i) for i, _ in enumerate(self.data, 1))

#     def line(self, number):
#         return f"This  is {self._phrase(number)}\n"

#     def parts(self, number):
#         return self.data[-number:]

#     def _phrase(self, number):
#         return " ".join(self.parts(number))


# print(House().parts(3))
# print(House().line(12))
# print(House().recite())


from itertools import chain  # noqa: E402


def zip_(self, iterable):
    """A zip object yielding tuples until an input is exhausted.

    >>> [1, 2, 3].zip([1, 2, 3])
    [(1, 1), (2, 2), (3, 3)]

    >>> [1, 2, 3].zip([3, 2])
    [(1, 3), (2, 2)]
    """
    return list(zip(self, iterable))


def flatten(self):
    """Return a copy of the array collapsed into one dimension.

    >>> [(1, 1), (2, 2), (3, 3)].flatten()
    [1, 1, 2, 2, 3, 3]
    """
    return list(chain.from_iterable(self))


# apenas por diversão novamente
curse(list, "zip", zip_)
curse(list, "flatten", flatten)

# EchoHouse "é uma" casa que ecoa partes
# class EchoHouse(House):
#     def parts(self, number):
#         data = super().parts(number)
#         return data.zip(data).flatten()


# print(EchoHouse().line(1))
# print(EchoHouse().line(2))
# print(EchoHouse().line(3))
# print(EchoHouse().line(12))

# mais classes, menos ifs
# comportamento abstrato


class DefaultOrder:
    def order(self, data):
        return data


class RandomOrder:
    def order(self, data):
        return data.shuffle()


class DefaultFormatter:
    def format(self, parts):
        return parts


class EchoFormatter:
    def format(self, parts):
        return parts.zip(parts).flatten()


class House:
    DATA = [
        "the horse and the hound and the horn that belonged to",
        "the farmer sowing his corn that kept",
        "the rooster that crowed in the morn that woke",
        "the priest all shaven and shorn that married",
        "the man all tattered and torn that kissed",
        "the maiden all forlorn that milked",
        "the cow with the crumpled horn that tossed",
        "the dog that worried",
        "the cat that killed",
        "the rat that ate",
        "the malt that lay in",
        "the house that Jack built",
    ]

    def __init__(self, orderer=DefaultOrder(), formatter=DefaultFormatter()):
        self.formatter = formatter
        self.data = orderer.order(self.DATA)

    def recite(self):
        return "\n".join(self.line(i) for i, _ in enumerate(self.data, 1))

    def line(self, number):
        return f"This  is {self._phrase(number)}\n"

    def parts(self, number):
        return self.formatter.format(self.data[-number:])

    def _phrase(self, number):
        return " ".join(self.parts(number))


print(House().line(12))
print(House(RandomOrder()).line(12))
print(House(formatter=EchoFormatter()).line(12))

# injeta um objeto para desempenhar o papel da coisa que varia

# House TEM um ORDENADOR
# House TEM um FORMATADOR

# É uma composição + injeção de dependência
# busca de abstração!!!

# herança não é para compartilhar comportamento

# isole a coisa que varia
# nomeie o conceito
# defina o papel
# injete os jogadores
