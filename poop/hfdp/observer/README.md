# Observers

## Como executar os exemplos

```bash
# exemplo simples de observador
poetry run simple_observer
# exemplo de simples observáveis
poetry run simple_observable
# exemplo tkinter (gui)
poetry run tkinter_observer
# exemplo estação do tempo
poetry run weather_station
# exemplo estação de trabalho com display de índice de calor
weather_station_heat_index
# exemplo estação do tempo (com interface observable)
poetry run weather_station_observable
# exemplo estação de trabalho com display de índice de calor (com interface observable)
weather_station_heat_index_observable
```

## Notas

# Notes:

# All classes are DisplayElement due to the display method.

# No inheritance is needed.

# Structural typing is used here.

# They are also called as observers (they have update method).

"""
Notes:

- Setter is used to notify that changes have occurred
- Fields temperature, humidity, pressure are "private".
  This means that we are preventing the alteration of any of
  them without notification from their observers
- I have doubts about the presence of getters methods in this class.
- WheaterData represents a topic to subcribe containing
  states that change.
  WeatherData is a subject (Structural typing),
  it have all required methods to be a subject.
  No need inheretance to implement a subject.
  """

"""
Notes:

- All instantied displays are registred in a subject(topic).
- When the states changes(set_measurements), all display are notified.
- We can register and unregister a observer as
  we can see in the last two lines.
  """
