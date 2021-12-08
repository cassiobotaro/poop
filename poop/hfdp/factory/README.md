# Factory

## Como executar os exemplos

```bash
# exemplo home theater
poetry run home_theater
```

## Notas

Notes:

    - use ABC to formalize that is an abstract method
    - only inheriting from ABC does not guarantee that it cannot be
    instantiated
    - @abstractmethod on __init__ guarantees that the class cannot be
    instantiated, only your specialization

    - super().__init__() guarantees that the instance have all
    required attributes
    - we are in the pizza namespace, Pizza sufix is redundant
    - Each pizza has its own characteristics

    when I ran mypy, I got a lot of errors, so I decided to create an
    invalid flavor pizza, respecting the pizza type interface.
    It's a Null object Pattern.
    Helps to avoid multiple ifs (including exceptions) when an item is not
    found.
