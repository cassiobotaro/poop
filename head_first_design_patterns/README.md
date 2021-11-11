# HEAD FIRST: DESIGN PATTERNS

## Básico da programação orientada a objetos

- Abstração
- Encapsulamento
- Polimorfismo
- Herança

## Princípios OO

Encapsule o que varia

Prefira composição a herança

Programe para interfaces, não para implementações

Esforce-se para obter designs fracamente acoplados entre objetos que interagem

Classes devem ser abertas para extensão, mas fechadas para modificação

Depende de abstrações. Não dependa de classes concretas

Fale apenas com seus amigos

## Padrões OO

**Strategy** - Define uma família de algoritmos, encapsula cada um,
e os torna intercambiáveis.
A estratégia permite que o algoritmo varie independentemente dos clientes que o utilizam.

**Observer** - Define uma dependência um-para-muitos entre objetos
de modo que quando um objeto muda de estado, todos os seus dependentes são
notificado e atualizado automaticamente.

**Decorator** - Anexe responsabilidades adicionais a um objeto dinamicamente.
Os decoradores fornecem uma alternativa flexível à criação de subclasses para estender a funcionalidade.

**Factory Method** - Defines an interface for creating an object, but let
subclasses decide which classes to instantiate. Factory Method lets a class
defer instantiation to the subclasses.
Define uma interface para a criação de um objeto, mas permite que as subclasses decidam qual objeto instanciar.
_Factory Method_ permite a uma classe adiar a instanciação para as subclasses.

**Abstract Factory** - Fornece uma interface para a criação de famílias de objetos relacionados ou dependentes sem especificar suas classes concretas.

**Singleton** - Certifique-se de que uma classe tenha apenas uma instância e forneça um ponto global de acesso a ela.

**Command** - Encapusula uma requisição como um objeto, permitindo que você parametrize os clientes com diferentes requisições, fila ou requisições de _log_, e suporte operações desfazíveis.

**Adapter** - Converte a interface de uma classe para a interface que os clientes esperam. Permite que classes trabalhem em conjunto que não podiam fazer antes por incompatibilidade de interfaces.

**Facade** - Provê uma interface unificada para um conjunto de interfaces em um subsistema. _Facade_ define uma interface mais alta que torna o subsistema mais fácil de usar.
