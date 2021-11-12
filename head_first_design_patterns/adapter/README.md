# Adapter

O padrão de adaptador é usado para converter a interface de uma classe para
outra interface que os clientes esperam.

EnumerationIterator é um adaptador que converte uma Enumeration em um Iterator.

IteratorEnumeration é um adaptador que converte um Iterator em uma Enumeration.

É utilizado tipos genéricos (T) para representar os tipo de dados que serão usados
nos adaptadores.

Não é necessário heranças pois estamos utilizando tipagem estrutural implícita.

Uma única exceção é a herança a Iterator que traz consigo o benefício de ganhar
o método `__iter__` retornando ele mesmo.

\_T_co é um tipo covariante, uma boa explicação pode ser encontrada [aqui](https://blog.daftcode.pl/covariance-contravariance-and-invariance-the-ultimate-python-guide-8fabc0c24278)

Como não existe o protocolo Enumeration no Python, definimos um para manter o código similar ao original.

ConcreteEnumeration é uma classe que implementa a interface Enumeration.

Turkey, Drone e Duck são interfaces, que devem ser implementadas por classes concretas.

Elas definem alguns comportamentos esperados pelos clientes destas classes.

Adaptador é um padrão que permite classes trabalharem juntas
que não foram projetadas para trabalhar juntas.

Mesmo que soe confuso, um Drone pode ser adaptado para ser usado como um Duck.

DuckAdapter é uma classe que implementa a interface Turkey, ela adapta um pato para ser usado como um peru.

TurkeyAdapter é uma classe que implementa a interface Duck, ela adapta um peru para ser usado como um pato.
