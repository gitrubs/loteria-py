This is the brazilian lottery program to get results direct from Caixa web API. It's retrieve all data related to one lottery draw with more detailed information of winners, reveneue, acumullated specials prize pool, etc.

# How to use it?

You can import the library at 'lib/resultados.py' and use it as follow (get MegaSena result):

```
from resultados import MegaSena

mega = MegaSena()

# Get last Mega Sena draw
result = mega.get_result()

if(result == 0):
  print str(mega).decode("latin-1")
else:
  print "Error to retrieve MegaSena result."
```

Library implements other lottery type such as:

* DuplaSena
* Quina
* Lotomania
* Lotofacil
* Timemania
* Lotogol
* LotecaResult
* Federal

# Test program

A test program can be found in 'test' directory:

```
python -m app.show_numbers -h
```

To get the last result from MegaSena, run:

```
python -m app.show_numbers -t megasena
```

If you want an specific draw (for example 1828), run:
```
python -m app.show_numbers -t megasena -d 1828
```

# TODO

* Implement the Loteca matches from new web page from Caixa;
* Add exception class;
* Add Python Package (setup.py);
