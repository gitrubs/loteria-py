This is the brazilian lottery program to get results direct from Caixa web API. It's retrieve all data related to one lottery draw with more detailed information of winners, reveneue, acumullated specials prize pool, etc.

# How to use it?

You can import the library at 'lib/resultados.py' and use it as follow (get MegaSena result):

```
from resultados import MegaSena

mega = MegaSena()

result = mega.get_result(draw=lottery_draw)

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
python test/show_numbers.py -h
```

To get the last result from MegaSena, run:

```
python test/show_numbers.py -t megasena
```

If you want an specific draw (for example 1828), run:
```
python test/show_numbers.py -t megasena -d 1828
```

# TODO

* Implement the Loteca matches from new web page from Caixa;
