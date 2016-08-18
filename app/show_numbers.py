#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse

from lib.resultados import MegaSena
from lib.resultados import DuplaSena
from lib.resultados import Quina
from lib.resultados import Lotomania
from lib.resultados import Lotofacil
from lib.resultados import Timemania
from lib.resultados import Lotogol
from lib.resultados import LotecaResult
from lib.resultados import LotecaMatches
from lib.resultados import Federal
from lib.resultados import Bicho


def main(lottery_type, lottery_draw):
    if(lottery_type == "megasena"):
        mega = MegaSena()

        result = mega.get_result(draw=lottery_draw)

        # data = (
        #     '1825|0,00|<span class="num_sorteio"><ul><li>21</li><li>54</li>'
        #     '<li>10</li><li>50</li><li>51</li><li>11</li></ul></span>|1|27.'
        #     '333.858,49|41|43.198,01|3.176|796,65|<a class="btn_conc_ant_meg'
        #     'asena" href="javascript:carrega_concurso(1824);" tabindex="27"'
        #     ' title="Ver concurso anterior">Ver concurso anterior</a>||07/06'
        #     '/2016|IGUATU|CE|Caminh�o da Sorte||1830|0|2.050.768,44|<div id='
        #     '"ganhadores_novo_modelo">    <table>     <thead>         <tr>  '
        #     '              <th class="largura_uf">UF</th>              <th>N'
        #     '� de Ganhadores</th>           </tr>       </thead>        <tbo'
        #     'dy>         <tr class="destaca_estado">             <td>CE</td>'
        #     '             <td>1</td></tr>         <tr>                <td><s'
        #     'pan>FORTALEZA                                         </span></'
        #     'td>                <td>1</td>          </tr>       </tbody>    '
        #     '</table></div>|<span class="num_sorteio"><ul><li>10</li><li>11<'
        #     '/li><li>21</li><li>50</li><li>51</li><li>54</li></ul></span>|2.'
        #     '200.000,00|09/06/2016|29.583.323,40|30.719.489,50')

        # data = (
        #   '1823|5.920.075,17|<span class="num_sorteio"><ul><li>54'
        #   '</li><li>34</li><li>59</li><li>21</li><li>09</li><li>04'
        #   '</li></ul></span>|0|0,00|70|25.579,78|4.110|622,37|<a class'
        #   '="btn_conc_ant_megasena" href="javascript:carrega_concurso(1822);'
        #   '" tabindex="27" title="Ver concurso anterior">Ver concurso'
        #   ' anterior</a>|<a class="btn_conc_prx_megasena" href="javascript:'
        #   'carrega_concurso(1824);" tabindex="27" tilte="Ver pr�ximo'
        #   'concurso">Ver'
        #   ' pr�ximo concurso</a>|01/06/2016|SãO PAULO|SP|Espaço Caixa'
        #   ' Loterias|'
        #   '|1825|5|11.476.812,76||<span class="num_sorteio"><ul><li>04</li>'
        #   '<li>09</li><li>21</li><li>34</li><li>54</li><li>59</li></ul>'
        #   '</span>'
        #   '|10.000.000,00|04/06/2016|28.531.767,32|31.057.124,00')
        # mega._parse_result(data)
        if(result == 0):
            print str(mega).decode("latin-1")
        else:
            print "Error to retrieve MegaSena result."

    elif(lottery_type == "duplasena"):
        dupla = DuplaSena()
        result = dupla.get_result(draw=lottery_draw)
        if(result == 0):
            print str(dupla).decode("latin-1")
        else:
            print "Error to retrieve DuplaSena result."

    elif(lottery_type == "quina"):
        quina = Quina()
        result = quina.get_result(draw=lottery_draw)
        if(result == 0):
            print str(quina).decode("latin-1")
        else:
            print "Error to retrieve Quina result."

    elif(lottery_type == "lotomania"):
        lotomania = Lotomania()
        result = lotomania.get_result(draw=lottery_draw)
        if(result == 0):
            print str(lotomania).decode("latin-1")
        else:
            print "Error to retrieve Lotomania result."

    elif(lottery_type == "lotofacil"):
        lotofacil = Lotofacil()
        result = lotofacil.get_result(draw=lottery_draw)
        if(result == 0):
            print str(lotofacil).decode("latin-1")
        else:
            print "Error to retrieve Lotofacil result."

    elif(lottery_type == "timemania"):
        timemania = Timemania()
        result = timemania.get_result(draw=lottery_draw)
        if(result == 0):
            print str(timemania).decode("latin-1")
        else:
            print "Error to retrieve Timemania result."

    elif(lottery_type == "lotogol"):
        lotogol = Lotogol()

        result = lotogol.get_result(draw=lottery_draw)
        if(result == 0):
            print str(lotogol).decode("latin-1")
        else:
            print "Error to retrieve Lotogol result."

    elif(lottery_type == "loteca-result"):
        loteca_result = LotecaResult()
        result = loteca_result.get_result(draw=lottery_draw)
        if(result == 0):
            print str(loteca_result).decode("latin-1")
        else:
            print "Error to retrieve Loteca-Result result."

    elif(lottery_type == "loteca-matches"):
        loteca_matches = LotecaMatches()
        result = loteca_matches.get_result()
        return 0
        if(result == 0):
            print str(loteca_matches).decode("latin-1")
        else:
            print "Error to retrieve Loteca-Matches result. %r" % result

    elif(lottery_type == "federal"):
        federal = Federal()
        result = federal.get_result(draw=lottery_draw)
        if(result == 0):
            print str(federal).decode("latin-1")
        else:
            print "Error to retrieve Bicho result."

    elif(lottery_type == "bicho"):
        bicho = Bicho()
        result = bicho.get_result(draw=lottery_draw)
        if(result == 0):
            print str(bicho).decode("latin-1")
        else:
            print "Error to retrieve Bicho result."


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        default="megasena",
        dest="lottery_type",
        choices=[
            "megasena", "duplasena", "quina", "lotomania", "timemania",
            "lotofacil", "loteca-result", "loteca-matches", "federal",
            "bicho", "lotogol"],
        help="Caixa Lottery type (default: %(default)s).")

    parser.add_argument(
        "-d", "--draw",
        default=None,
        type=int,
        dest="lottery_draw",
        help="Caixa Lottery draw number (default: %(default)s).")

    args = parser.parse_args()

    print args

    main(args.lottery_type, args.lottery_draw)
