#!/usr/bin/python
# -*- coding: utf-8 -*-

from cookielib import CookieJar
from urllib2 import HTTPError, URLError
import urllib2
from datetime import date
from xml.dom.minidom import parseString


class LotteryCaixa(object):
    SUCCESS = 0
    ERROR_HTTP_404 = 1
    ERROR_HTTP_408 = 2
    ERROR_HTTP_GENERIC = 3
    ERROR_URL_GENERIC = 4
    ERROR_DATA_CONTENT = 5

    def __init__(self):
        # Current draw data
        self.draw = ""
        self.draw_date = ""

        # Next draw data
        self.next_draw_date = ""
        self.next_prize_pool = ""

        # Draw location
        self.draw_city = ""
        self.draw_state = ""

        # Numbers
        self.number_list = None

        # Winners data
        self.winners = {}
        self.winners_location = None

        # Lottery URL
        self.host = "www1.caixa.gov.br/"
        self.lottery_type_url = ""

        # Prize
        self.accumulated = ""
        self.total_revenue = ""

    def http_request(self, url):
        """Open HTTP Request for specified url.

        Args:
            url: url address in string format.

        Returns:
            HTTP Get body response content or integer error code.
        """

        try:
            request = urllib2.Request(url)
            cj = CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            f = opener.open(request)
            return f

        except HTTPError as e:
            if(e.code == 404):
                return self.ERROR_HTTP_404
            elif(e.code == 408):
                return self.ERROR_HTTP_408
            else:
                return self.ERROR_HTTP_GENERIC

        except URLError as e:
            return self.ERROR_URL_GENERIC

    def format_winners(self, html_table):
        """Get winners from HTML table and return of winners tuple locations.

        The winners tuple has the format:
            (winners_amount, location)

        where 'winners_amount' is the amount of winners and 'location' is
        the brazilian city and estate (reduced) format.

        Ex: 'Curitiba/PR', 'Rio de Janeiro/RJ', 'Santos/SP'.

        Args:
            html_table: lottery winners in HTML table content in specific
                CAIXA format.

        Returns:
            List with winners in tuple format.
        """
        winners_list = []

        if(html_table == ""):
            return winners_list

        tbody = html_table.split("<tbody>")[1].split("</tbody>")[0]
        tmp = tbody.replace("\t", "")
        tmp = tmp.replace("<tr class=\"destaca_estado\">", "")
        tmp = tmp.replace("<tr>", "")
        tmp = tmp.replace("</tr>", "")
        tmp = tmp.replace("</td>", "")
        tmp = tmp.replace("<span>", "")
        tmp = tmp.replace("</span>", "")

        place_list = tmp.split("<td>")
        place_list.pop(0)

        only_states = False

        # If city name is the state (UF) name, the winners
        # location has only state winners
        if(len(place_list[2]) == 2):
            only_states = True

        i = 0

        while (i < len(place_list)):
            uf = place_list[i]
            winner_amount = int(place_list[i + 1])

            if(only_states is True):
                winners_list.append((place_list[i + 1], place_list[i]))
                j = 0
                i = i + 2
            else:
                j = 0
                i = i + 2
                # Sum winners from same location
                while (j < winner_amount):
                    city = place_list[i].strip()
                    sub_value = place_list[i + 1]
                    j = j + int(sub_value)
                    i = i + 2

                    winners_list.append((sub_value, city + "/" + uf))

        return winners_list

    def format_amount_winners(self, number):
        """Format the prize amount for brazilian notation.

        If number is integer, it's only returns the integer part with
        brazilian format. Otherwise it returns in floating point format.

        Args:
            number: string number without '.' or ',' chars;

        Returns:
            String number in brazilian notation.
        """
        new_number = ""
        vetor = []

        # Integer format
        if(number.isdigit()):
            tmp = int(number)
            while(tmp / 1000 > 0):
                resto = tmp % 1000
                tmp = tmp - resto
                tmp = tmp / 1000
                vetor.append(resto)
            vetor.append(tmp)
            new_number = str(vetor.pop())
            for i in range(len(vetor) - 1, -1, -1):
                new_number = new_number + "." + str(vetor[i])
            return new_number
        # Floating point format
        else:
            centavos = number.split(",")[1]
            tmp = int(number.split(",")[0])
            while(tmp / 1000 > 0):
                resto = tmp % 1000
                tmp = tmp - resto
                tmp = tmp / 1000
                vetor.append(resto)
            vetor.append(tmp)
            new_number = str(vetor.pop())
            for i in range(len(vetor) - 1, -1, -1):
                new_number = new_number + "." + str(vetor[i])
            return new_number + "," + centavos

    def get_result(self, draw=None):
        """Each lottery type has own url.

        Args:
            draw: lottery draw number (default: None).

        Returns:
            Return core representing error:

        """
        old_draw = ""

        if(draw is not None):
            assert type(draw) is int, "draw is not integer: %r" % draw
            assert draw >= 0, "draw must be positive: %r" % draw
            old_draw = (
                "?submeteu=sim&opcao=concurso&txtConcurso=" + str(draw))

        url = "http://" + self.host + self.lottery_type_url + old_draw

        result = self.http_request(url)
        if(type(result) is int):
            return result

        # Parse data content
        if(self._parse_result(result.read()) is False):
            # If parser result fails, it returns the error code
            return self.ERROR_DATA_CONTENT

        return self.SUCCESS

    def _parse_result(self, data):
        """Each lottery type has own parse result content.

        Args:
            data: data content to be parsed.
        """
        pass

    def _add_winner(self, number_match, amount_winners, prize):
        """Add winner tuple with amount of winners and prize indexed by the
        number of matches number.

        Args:
            number_match: amount of matches.
            amount_winners: amount of winners that matches the number match.
            prize: prize for winners that matches the number match.
        """
        if(type(amount_winners) == str):
            num_winners = self._convert_string_int(amount_winners)
        else:
            num_winners = amount_winners

        self.winners[str(number_match)] = \
            (num_winners, self._convert_string_float(prize))

    def _convert_string_float(self, string_float):
        """Convert string float in brazilian format to python float.

        Brazilian string float is used to represents the prize value in
        format:
            x.xxx.xxx,yy
            where x is the integer part and yy is the float part. The integer
            part is splited by '.' char and ',' splits the interger from
            float part.

        Args:
            string_float: brazilian string float number.

        Returns:
            Python float format.
        """
        tmp_float = string_float.replace(".", "")
        tmp_float = tmp_float.replace(",", ".")

        return float(tmp_float)

    def _convert_string_int(self, string_int):
        """Convert string integer in brazilian format to python int.

        Brazilian string int is used to represents values grater than 1000
        with format:
            x.xxx.xxx
            where x is the integer part.

        Args:
            string_int: brazilian string integer number.

        Returns:
            Python integer format.
        """
        tmp_int = string_int.replace(".", "")

        return int(tmp_int)


class MegaSena(LotteryCaixa, object):
    def __init__(self):
        super(MegaSena, self).__init__()

        self.lottery_type_url = \
            "loterias/loterias/megasena/megasena_pesquisa_new.asp"

        # MegaSena special draw and prizes
        self.new_year_prize_pool = ""
        self.next_final_draw = ""
        self.next_final_draw_ending = ""
        self.next_final_prize = ""
        self.next_final_prize_pool = ""

        # MegaSena current draw total revenue
        self.total_revenue = ""

    def __str__(self):
        text_array = []

        text_array.append("MegaSena:")
        text_array.append("draw: %s" % str(self.draw))
        text_array.append("draw_date: %s" % str(self.draw_date))
        text_array.append("next_draw_date: %s" % str(self.next_draw_date))
        text_array.append("next_prize_pool: %s" % str(self.next_prize_pool))
        text_array.append("draw_city: %s" % str(self.draw_city))
        text_array.append("draw_state: %s" % str(self.draw_state))
        text_array.append("number_list: %s" % str(self.number_list))
        text_array.append("winners: %s" % str(self.winners))
        text_array.append("winners_location: %s" % str(self.winners_location))
        text_array.append("lottery_type_url: %s" % str(self.lottery_type_url))

        text_array.append(
            "new_year_prize_pool: %s" % str(self.new_year_prize_pool))
        text_array.append("next_final_draw: %s" % str(self.next_final_draw))
        text_array.append(
            "next_final_draw_ending: %s" % str(self.next_final_draw_ending))
        text_array.append(
            "next_final_prize_pool: %s" % str(self.next_final_prize_pool))
        text_array.append("next_final_prize: %s" % str(self.next_final_prize))
        text_array.append("total_revenue: %s" % str(self.total_revenue))

        return "\n".join(text_array)

    def _parse_result(self, data):
        """Parse result from MegaSena data content.

        Args:
            data: MegaSena result data content format.

        Returns
            True if result was parsed with success or False if failed
            to parse data content.
        """
        fields = data.split("|")

        # Return error for data format content
        if(len(fields) < 5):
            print(
                "MegaSena data content without result data: %r" % (data))
            return False

        self.draw = fields[0]
        self.next_final_prize_pool = self._convert_string_float(fields[1])

        self.draw_date = fields[11]

        self.draw_city = fields[12]
        self.draw_state = fields[13]

        # Get numbers
        tmp = fields[2].split("<li>")
        tmp.pop(0)
        numbers = []
        for i in tmp:
            dezena = i.split("</li>")[0]
            numbers.append(int(dezena))
        numbers.sort()
        self.number_list = numbers

        # Add winners indexed by number of matches
        self._add_winner("6", fields[3], fields[4])
        self._add_winner("5", fields[5], fields[6])
        self._add_winner("4", fields[7], fields[8])

        # MegaSena special draw (draw ending with 0 of 5)
        self.next_final_draw = fields[16]
        self.next_final_draw_ending = fields[17]
        self.next_final_prize = self._convert_string_float(fields[18])

        # Next draw data
        self.next_prize_pool = self._convert_string_float(fields[21])
        self.next_draw_date = fields[22]

        # MegaSena new year special draw
        self.new_year_prize_pool = self._convert_string_float(fields[23])

        # Total reveneu
        self.total_revenue = self._convert_string_float(fields[24])

        tmp = fields[19]

        if(self.winners["6"][0] != 0):
            self.winners_location = self.format_winners(tmp)

        return True


class DuplaSena(LotteryCaixa, object):
    def __init__(self):
        super(DuplaSena, self).__init__()

        self.lottery_type_url = \
            "/loterias/loterias/duplasena/duplasena_pesquisa_new.asp"

        # DuplaSena second draw data
        self.number_list2 = None
        self.winners2 = {}
        self.winners_location2 = None

    def __str__(self):
        text_array = []

        text_array.append("DuplaSena:")
        text_array.append("draw: %s" % str(self.draw))
        text_array.append("draw_date: %s" % str(self.draw_date))
        text_array.append("next_draw_date: %s" % str(self.next_draw_date))
        text_array.append("next_prize_pool: %s" % str(self.next_prize_pool))
        text_array.append("draw_city: %s" % str(self.draw_city))
        text_array.append("draw_state: %s" % str(self.draw_state))
        text_array.append("number_list: %s" % str(self.number_list))
        text_array.append("winners: %s" % str(self.winners))
        text_array.append("winners_location: %s" % str(self.winners_location))
        text_array.append("lottery_type_url: %s" % str(self.lottery_type_url))

        text_array.append("number_list2: %s" % str(self.number_list2))
        text_array.append("winners2: %s" % str(self.winners2))
        text_array.append(
            "winners_location2: %s" % str(self.winners_location2))

        return "\n".join(text_array)

    def _parse_result(self, data):
        fields = data.split("|")

        # for i, field_data in enumerate(fields):
        #     print i, field_data

        # Return error for data format content
        if(len(fields) < 5):
            print(
                "DuplaSena data content without result data: %r" % (data))
            return False

        self.draw = fields[0]
        self.next_prize_pool = self._convert_string_float(fields[5])

        self.draw_date = fields[17]

        self.draw_city = fields[14]
        self.draw_state = fields[15]

        # Get first Dupla Sena draw numbers
        tmp = fields[3].split("<li>")
        tmp.pop(0)
        self.number_list = []
        for i in tmp:
            num = i.split("</li>")[0]
            self.number_list.append(int(num))
        self.number_list.sort()

        # Get second Dupla Sena draw numbers
        tmp = fields[4].split("<li>")
        tmp.pop(0)
        self.number_list2 = []
        for i in tmp:
            num = i.split("</li>")[0]
            self.number_list2.append(int(num))
        self.number_list2.sort()

        self._add_winner("4", fields[27], fields[28])
        self._add_winner("5", fields[25], fields[26])
        self._add_winner("6", fields[6], fields[7])

        self._add_winner2("4", fields[12], fields[13])
        self._add_winner2("5", fields[9], fields[11])
        self._add_winner2("6", fields[8], fields[10])

        self.next_prize_pool = self._convert_string_float(fields[22])
        self.next_draw_date = fields[23]

        if (self.winners["6"][0] != 0):
            self.winners_location = self.format_winners(fields[19])

        if (self.winners2["6"][0] != 0):
            self.winners_location2 = self.format_winners2(fields[19])

        return True

    def _add_winner2(self, number_match, amount_winners, prize):
        """Add winner tuple with amount of winners and prize indexed by the
        number of matches number for second draw.

        Args:
            number_match: amount of matches.
            amount_winners: amount of winners that matches the number match.
            prize: prize for winners that matches the number match.
        """

        if(type(amount_winners) == str):
            num_winners = self._convert_string_int(amount_winners)
        else:
            num_winners = amount_winners

        self.winners2[str(number_match)] = \
            (num_winners, self._convert_string_float(prize))

    def format_winners2(self, html_table):
        """Get winners from HTML table and return of winners tuple locations
        for second numbers draw.

        The winners tuple has the format:
            (winners_amount, location)

        where 'winners_amount' is the amount of winners and 'location' is
        the brazilian city and estate (reduced) format.

        Ex: 'Curitiba/PR', 'Rio de Janeiro/RJ', 'Santos/SP'.

        Args:
            html_table: lottery winners in HTML table content in specific
                CAIXA format.

        Returns:
            List with winners in tuple format.
        """
        winners_list = []

        if(html_table == ""):
            return winners_list

        # Test if the field has first draw winners location
        if(html_table.find('tit_dupla_gan_estado1.jpg') != -1):
            tbody = html_table.split("<tbody>")[2].split("</tbody>")[0]
        elif(html_table.find('tit_dupla_gan_estado2.jpg') != -1):
                tbody = html_table.split("<tbody>")[1].split("</tbody>")[0]
        else:
            return winners_list

        tmp = tbody.replace("\t", "")
        tmp = tmp.replace("<tr class=\"destaca_estado\">", "")
        tmp = tmp.replace("<tr>", "")
        tmp = tmp.replace("</tr>", "")
        tmp = tmp.replace("</td>", "")
        tmp = tmp.replace("<span>", "")
        tmp = tmp.replace("</span>", "")

        place_list = tmp.split("<td>")
        place_list.pop(0)

        only_states = False

        # If city name is the state (UF) name, the winners
        # location has only state winners
        if(len(place_list[2]) == 2):
            only_states = True

        i = 0

        while (i < len(place_list)):
            uf = place_list[i]
            winner_amount = int(place_list[i + 1])

            if(only_states is True):
                winners_list.append((place_list[i + 1], place_list[i]))
                j = 0
                i = i + 2
            else:
                j = 0
                i = i + 2
                # Sum winners from same location
                while (j < winner_amount):
                    city = place_list[i].strip()
                    sub_value = place_list[i + 1]
                    j = j + int(sub_value)
                    i = i + 2

                    winners_list.append((sub_value, city + "/" + uf))

        return winners_list


class Quina(LotteryCaixa, object):
    def __init__(self):
        super(Quina, self).__init__()

        self.lottery_type_url = \
            "/loterias/loterias/quina/quina_pesquisa_new.asp"

    def __str__(self):
        text_array = []

        text_array.append("Quina:")
        text_array.append("draw: %s" % str(self.draw))
        text_array.append("draw_date: %s" % str(self.draw_date))
        text_array.append("next_draw_date: %s" % str(self.next_draw_date))
        text_array.append("next_prize_pool: %s" % str(self.next_prize_pool))
        text_array.append("draw_city: %s" % str(self.draw_city))
        text_array.append("draw_state: %s" % str(self.draw_state))
        text_array.append("number_list: %s" % str(self.number_list))
        text_array.append("winners: %s" % str(self.winners))
        text_array.append("winners_location: %s" % str(self.winners_location))
        text_array.append("accumulated: %s" % str(self.accumulated))
        text_array.append("total_revenue: %s" % str(self.total_revenue))
        text_array.append("lottery_type_url: %s" % str(self.lottery_type_url))

        return "\n".join(text_array)

    def _parse_result(self, data):
        fields = data.split("|")

        # for i, field_data in enumerate(fields):
        #     print i, field_data

        if(len(fields) < 5):
            print(
                "Quina data content without result data: %r" % (data))
            return False

        self.draw = fields[0]
        self.accumulated = self._convert_string_float(fields[13])

        self.draw_date = fields[16]

        self.draw_city = fields[2]
        self.draw_state = fields[3]

        # Pega dezenas
        tmp = fields[14].split("<li>")
        tmp.pop(0)

        self.number_list = []
        for i in range(0, 5):
            number = tmp[i].split("</li>")[0]
            self.number_list.append(int(number))
        self.number_list.sort()

        # Menos premiacao para mario- ex: 0=Quadra > 1=Quina > 2=Sena
        self._add_winner("2", fields[23], fields[22])
        self._add_winner("3", fields[10], fields[11])
        self._add_winner("4", fields[8], fields[9])
        self._add_winner("5", fields[6], fields[7])

        self.next_prize_pool = self._convert_string_float(fields[17])
        self.next_draw_date = fields[18]
        self.total_revenue = self._convert_string_float(fields[20])

        if (self.winners["5"][0] != 0):
            self.winners_location = self.format_winners(fields[19])

        return True


class Lotomania(LotteryCaixa, object):
    def __init__(self):
        super(Lotomania, self).__init__()

        self.lottery_type_url = \
            "/loterias/loterias/lotomania/_lotomania_pesquisa.asp"

        self.winners_zero_location = None

        self.easter_draw_prize = ""

    def __str__(self):
        text_array = []

        text_array.append("Lotomania:")
        text_array.append("draw: %s" % str(self.draw))
        text_array.append("draw_date: %s" % str(self.draw_date))
        text_array.append("next_draw_date: %s" % str(self.next_draw_date))
        text_array.append("next_prize_pool: %s" % str(self.next_prize_pool))
        text_array.append("draw_city: %s" % str(self.draw_city))
        text_array.append("draw_state: %s" % str(self.draw_state))
        text_array.append("number_list: %s" % str(self.number_list))
        text_array.append("winners: %s" % str(self.winners))
        text_array.append("winners_location: %s" % str(self.winners_location))
        text_array.append("accumulated: %s" % str(self.accumulated))
        text_array.append("total_revenue: %s" % str(self.total_revenue))
        text_array.append("lottery_type_url: %s" % str(self.lottery_type_url))
        text_array.append(
            "winners_zero_location: %s" % str(self.winners_zero_location))
        text_array.append(
            "easter_draw_prize: %s" % str(self.easter_draw_prize))

        return "\n".join(text_array)

    def format_winners_zero(self, html_table, only_states=False):
        vetor = []

        # Test tbody tag amount to get the tbody content of zero match
        if(len(html_table.split("<tbody>")) == 2):
            tbody = html_table.split("<tbody>")[1].split("</tbody>")[0]
        elif(len(html_table.split("<tbody>")) == 3):
            tbody = html_table.split("<tbody>")[2].split("</tbody>")[0]

        tmp = tbody.replace("\t", "")
        tmp = tmp.replace("<tr class=\"destaca_estado\">", "")
        tmp = tmp.replace("<tr>", "")
        tmp = tmp.replace("</tr>", "")
        tmp = tmp.replace("</td>", "")
        tmp = tmp.replace("<span>", "")
        tmp = tmp.replace("</span>", "")

        place_list = tmp.split("<td>")
        place_list.pop(0)

        i = 0
        while (i < len(place_list)):
            uf = place_list[i][0:2]
            winner_amount = int(place_list[i + 1])
            j = 0
            i = i + 2
            while (j < winner_amount):
                city = place_list[i].strip()
                sub_value = place_list[i + 1]
                j = j + int(sub_value)
                i = i + 2

                vetor.append((sub_value, city + "/" + uf))

        return vetor

    def _parse_result(self, data):
        fields = data.split("|")

        # for i, field_data in enumerate(fields):
        #     print i, field_data

        if(len(fields) < 5):
            print(
                "Lotomania data content without result data: %r" % (data))
            return False

        self.draw = fields[0]
        self.accumulated = self._convert_string_float(fields[39])

        self.draw_date = fields[41]

        self.draw_city = fields[40]
        self.draw_state = fields[2]

        self.number_list = []
        for i in range(6, 26):
            self.number_list.append(int(fields[i]))
        self.number_list.sort()

        # put 00 number at the end
        if (self.number_list[0] == 0):
            tmp = self.number_list.pop(0)
            self.number_list.append(tmp)

        self._add_winner("0", fields[37], fields[38])
        self._add_winner("16", fields[35], fields[36])
        self._add_winner("17", fields[33], fields[34])
        self._add_winner("18", fields[31], fields[32])
        self._add_winner("19", fields[29], fields[30])
        self._add_winner("20", fields[27], fields[28])

        self.next_prize_pool = self._convert_string_float(fields[68])
        self.next_draw_date = fields[69]

        # Set winners place
        if (self.winners["20"][0] != 0):
            self.winners_location = self.format_winners(fields[43])

        if (self.winners["0"][0] != 0):
            self.winners_zero_location = self.format_winners_zero(fields[43])

        self.total_revenue = self._convert_string_float(fields[70])

        self.easter_draw_prize = self._convert_string_float(fields[71])

        return True


class Lotofacil(LotteryCaixa, object):
    def __init__(self):
        super(Lotofacil, self).__init__()

        self.lottery_type_url = \
            "/loterias/loterias/lotofacil/lotofacil_pesquisa_new.asp"

        self.independency_draw_prize = ""

    def __str__(self):
        text_array = []

        text_array.append("Lotofacil:")
        text_array.append("draw: %s" % str(self.draw))
        text_array.append("draw_date: %s" % str(self.draw_date))
        text_array.append("next_draw_date: %s" % str(self.next_draw_date))
        text_array.append("next_prize_pool: %s" % str(self.next_prize_pool))
        text_array.append("draw_city: %s" % str(self.draw_city))
        text_array.append("draw_state: %s" % str(self.draw_state))
        text_array.append("number_list: %s" % str(self.number_list))
        text_array.append("winners: %s" % str(self.winners))
        text_array.append("winners_location: %s" % str(self.winners_location))
        text_array.append("accumulated: %s" % str(self.accumulated))
        text_array.append("total_revenue: %s" % str(self.total_revenue))
        text_array.append("lottery_type_url: %s" % str(self.lottery_type_url))
        text_array.append(
            "independency_draw_prize: %s" % str(self.independency_draw_prize))

        return "\n".join(text_array)

    def _parse_result(self, data):
        fields = data.split("|")

        # for i, field_data in enumerate(fields):
        #     print i, field_data

        if(len(fields) < 5):
            print(
                "Lotofacil data content without result data: %r" % (data))
            return False

        self.accumulated = self.format_amount_winners(fields[36])

        self.draw_date = fields[34]

        self.draw_city = fields[31]
        self.draw_state = fields[32]

        self.number_list = []
        for i in range(3, 19):
            self.number_list.append(int(fields[i]))
        self.number_list.sort()

        self._add_winner("11", fields[26], fields[27])
        self._add_winner("12", fields[24], fields[25])
        self._add_winner("13", fields[22], fields[23])
        self._add_winner("14", fields[20], fields[21])
        self._add_winner("15", fields[18], fields[19])

        self.next_prize_pool = self._convert_string_float(fields[53])
        self.next_draw_date = fields[54]

        self.total_revenue = self._convert_string_float(fields[55])

        self.independency_draw_prize = self._convert_string_float(fields[56])

        if (self.winners["15"][0] != 0):
            self.winners_location = self.format_winners(fields[28])

        return True


class Timemania(LotteryCaixa, object):
    def __init__(self):
        super(Timemania, self).__init__()

        self.lottery_type_url = \
            "/loterias/loterias/timemania/timemania_pesquisa.asp"

        self.special_team = ""

        self.next_final_zero_prize = ""
        self.next_final_zero_draw = ""

    def __str__(self):
        text_array = []

        text_array.append("Lotofacil:")
        text_array.append("draw: %s" % str(self.draw))
        text_array.append("draw_date: %s" % str(self.draw_date))
        text_array.append("next_draw_date: %s" % str(self.next_draw_date))
        text_array.append("next_prize_pool: %s" % str(self.next_prize_pool))
        text_array.append("draw_city: %s" % str(self.draw_city))
        text_array.append("draw_state: %s" % str(self.draw_state))
        text_array.append("number_list: %s" % str(self.number_list))
        text_array.append("winners: %s" % str(self.winners))
        text_array.append("winners_location: %s" % str(self.winners_location))
        text_array.append("accumulated: %s" % str(self.accumulated))
        text_array.append("total_revenue: %s" % str(self.total_revenue))
        text_array.append("lottery_type_url: %s" % str(self.lottery_type_url))
        text_array.append("special_team: %s" % str(self.special_team))
        text_array.append(
            "next_final_zero_prize: %s" % str(self.next_final_zero_prize))
        text_array.append(
            "next_final_zero_draw: %s" % str(self.next_final_zero_draw))

        return "\n".join(text_array)

    def _parse_result(self, data):
        fields = data.split("|")

        # for i, field_data in enumerate(fields):
        #     print i, field_data

        if(len(fields) < 5):
            print(
                "Timemania data content without result data: %r" % (data))
            return False

        self.draw = fields[0]

        self.draw_date = fields[1]

        self.draw_state = fields[4]
        self.draw_city = fields[5]
        self.special_team = fields[8]

        tmp = fields[6].split("<li>")
        tmp.pop(0)

        self.number_list = []
        for i in tmp:
            number = i.split("</li>")[0]
            self.number_list.append(int(number))
        self.number_list.sort()

        self._add_winner(
            self.special_team, self.format_amount_winners(fields[19]),
            fields[20])
        self._add_winner(
            "3", self.format_amount_winners(fields[17]), fields[18])
        self._add_winner(
            "4", self.format_amount_winners(fields[15]), fields[16])
        self._add_winner(
            "5", self.format_amount_winners(fields[13]), fields[14])
        self._add_winner(
            "6", self.format_amount_winners(fields[11]), fields[12])
        self._add_winner(
            "7", self.format_amount_winners(fields[9]), fields[10])

        self.accumulated = self._convert_string_float(fields[21])
        self.next_draw_date = fields[22]
        self.next_prize_pool = self._convert_string_float(fields[23])

        self.next_final_zero_draw = fields[24].split("(")[1].split(")")[0]
        self.next_final_zero_prize = self._convert_string_float(fields[25])

        self.total_revenue = self._convert_string_float(fields[29])

        if (self.winners["7"][0] != 0):
            self.winners_location = self.format_winners(fields[28])

        return True


class Lotogol(LotteryCaixa, object):
    def __init__(self):
        super(Lotogol, self).__init__()

        self.lottery_type_url = \
            "/loterias/loterias/lotogol/lotogol_pesquisa_new.asp"

        self.matches_result = []

    def __str__(self):
        text_array = []

        text_array.append("Lotogol:")
        text_array.append("draw: %s" % str(self.draw))
        text_array.append("draw_date: %s" % str(self.draw_date))
        text_array.append("next_draw_date: %s" % str(self.next_draw_date))
        text_array.append("next_prize_pool: %s" % str(self.next_prize_pool))
        text_array.append("winners: %s" % str(self.winners))
        text_array.append("winners_location: %s" % str(self.winners_location))
        text_array.append("accumulated: %s" % str(self.accumulated))
        text_array.append("total_revenue: %s" % str(self.total_revenue))
        text_array.append("lottery_type_url: %s" % str(self.lottery_type_url))
        text_array.append("matches_result: %s" % str(self.matches_result))

        return "\n".join(text_array)

    def _add_match_result(self, team1_result, team1_name,
                          team2_result, team2_name, day):
        team1_tuple = (team1_result, team1_name)
        team2_tuple = (team2_result, team2_name)

        self.matches_result.append((team1_tuple, team2_tuple, day))

    def _parse_winners_result(self, html_table):
        """Parse winners result from HTML table
        """
        winners_list = {}

        # html_table = (
        #     '<table  border="0" id="tabela_premiacao" summary="Premi'
        #     'a&ccedil;&otilde;es" cellspacing="0" cellpadding="2">  <t'
        #     'head><tr>     <th class="meio">Faixa de premia��o </th>  '
        #     '     <th class="meio">N&ordm; de ganhadores </th>        '
        #     '<th class="direita">Valor do Pr&ecirc;mio(R$)</th>  </tr>'
        #     '</thead>   <tr>    <td class="meio">1&ordm; (5 acertos)</'
        #     'td>   <td class="meio">1</span></td>  <td class="direita"'
        #     '>86.018,58</td>  </tr>   <tr>        <td class="meio">2&or'
        #     'dm; (4 acertos)</td>   <td class="meio">45</td>    <td cl'
        #     'ass="direita">806,24</td> </tr>   <tr>        <td class="'
        #     'meio">3&ordm; (3 acertos)</td>       <td class="meio">1.6'
        #     '91</td>     <td class="direita">21,45</td> </tr>    <tr> '
        #     '       <td colspan="3">&nbsp;</td> </tr></table>')

        td_middle = html_table.split('<td class="meio">')

        five_td = td_middle[2]
        four_td = td_middle[4]
        three_td = td_middle[6]

        # Parse five matches td element
        five_fields = five_td.replace('</span>', '')
        five_fields = five_fields.replace('<td class="direita">', '')
        five_fields = five_fields.replace('\t', '')
        five_fields = five_fields.replace(' ', '')

        five_winners = five_fields.split('</td>')[0:2]

        # Parse four matches td element
        four_fields = four_td.replace('<td class="direita">', '')
        four_fields = four_fields.replace('\t', '')
        four_fields = four_fields.replace(' ', '')

        four_winners = four_fields.split('</td>')[0:2]

        # Parse three matches td element
        three_fields = three_td.replace('<td class="direita">', '')
        three_fields = three_fields.replace('\t', '')
        three_fields = three_fields.replace(' ', '')

        three_winners = three_fields.split('</td>')[0:2]

        winners_list["5"] = (five_winners[0], five_winners[1])
        winners_list["4"] = (four_winners[0], four_winners[1])
        winners_list["3"] = (three_winners[0], three_winners[1])

        return winners_list

    def _parse_matches_result(self, html_table):
        table_rows = html_table.split('<tr class="linhas">')
        table_rows.pop(0)

        final_results = []

        for row in table_rows:
            # Get teams
            result_content = row.split("</tr>")[0]

            teams_string = \
                result_content.split('#C5C9C8;">')[2].split("</td>")[0]

            tmp_teams = teams_string.replace("<br>", " ")
            tmp_teams = tmp_teams.replace("<br />", " ")
            teams = tmp_teams.split(" x ")

            # Get match date
            match_date = \
                row.split('#C5C9C8;">')[4].split("</td>")[0]

            # Get teams results
            result_content = row.split('<tr height="22">')

            tmp_team1_result = result_content[1].split('"fundo_azul">')[1]
            team1_result = tmp_team1_result.split("</span>")[0]

            tmp_team2_result = result_content[2].split('"fundo_azul">')[1]
            team2_result = tmp_team2_result.split("</span>")[0]

            match_result = (
                (team1_result, teams[0]),
                (team2_result, teams[1]),
                match_date)

            final_results.append(match_result)

        return final_results

    def _parse_result(self, data):
        fields = data.split("|")

        # for i, field_data in enumerate(fields):
        #     print i, field_data

        if(len(fields) < 5):
            print(
                "Lotogol data content without result data: %r" % (data))
            return False

        self.draw = fields[0]
        self.draw_date = fields[1]

        winners_result = self._parse_winners_result(fields[6])

        for winner in winners_result:
            self._add_winner(
                winner, winners_result[winner][0], winners_result[winner][1])

        self.matches_result = self._parse_matches_result(fields[4])

        self.accumulated = self._convert_string_float(fields[9])

        self.next_prize_pool = self._convert_string_float(fields[13])
        self.next_draw_date = fields[14]

        self.total_revenue = \
            self._convert_string_float(fields[15].replace("<br>", ""))

        if (self.winners["5"][0] != 0):
            self.winners_location = self.format_winners(fields[7])

        return True


class LotecaResult(LotteryCaixa, object):
    def __init__(self):
        super(LotecaResult, self).__init__()

        self.teams_col1 = []
        self.teams_col2 = []
        self.result_col1 = []
        self.result_col2 = []

        self.lottery_type_url = \
            "/loterias/loterias/loteca/loteca_pesquisa_new.asp"

    def __str__(self):
        text_array = []

        text_array.append("LotecaResult:")
        text_array.append("draw: %s" % str(self.draw))
        text_array.append("draw_date: %s" % str(self.draw_date))
        text_array.append("next_draw_date: %s" % str(self.next_draw_date))
        text_array.append("next_prize_pool: %s" % str(self.next_prize_pool))
        text_array.append("draw_city: %s" % str(self.draw_city))
        text_array.append("draw_state: %s" % str(self.draw_state))
        text_array.append("number_list: %s" % str(self.number_list))
        text_array.append("winners: %s" % str(self.winners))
        text_array.append("winners_location: %s" % str(self.winners_location))
        text_array.append("accumulated: %s" % str(self.accumulated))
        text_array.append("total_revenue: %s" % str(self.total_revenue))
        text_array.append("lottery_type_url: %s" % str(self.lottery_type_url))

        text_array.append("teams_col1: %s" % str(self.teams_col1))
        text_array.append("teams_col2: %s" % str(self.teams_col2))
        text_array.append("result_col1: %s" % str(self.result_col1))
        text_array.append("result_col2: %s" % str(self.result_col2))

        return "\n".join(text_array)

    def _parse_final_draw(self, html_data):
        # html_data = (
        #     '<span style="color:#666; font-size:13px;"> Valor Acumulado para'
        #     ' o pr&oacute;ximo concurso de final cinco (705)</span>:<br /><s'
        #     'pan style="color: #666; font-size: 14px; font-weight: bold;">R$'
        #     '</span> </b><span style="color: #FF0000; font-size: 18px;">439.'
        #     '092,58</span>')

        final_draw = html_data.split("(")[1].split(")")[0]
        final_prize_pool = \
            html_data.split("<span ")[3].split(">")[1].split("<")[0]

        return (final_draw, final_prize_pool)

    def _parse_result(self, data):
        fields = data.split("|")

        # for i, field_data in enumerate(fields):
        #     print i, field_data

        if(len(fields) < 5):
            print(
                "LotecaResult data content without result data: %r" % (data))
            return False

        self.draw = fields[0]
        self.accumulated = self._convert_string_float(fields[6])
        self.draw_date = fields[7]

        tmp = fields[3].split("<tr class=\"linhas\">")
        tmp.pop(0)

        for i in tmp:
            tr = i.split("<b>")
            res_col1 = tr[2].split("</b>")[0]
            res_col2 = tr[3].split("</b>")[0]
            team1 = i.split(
                "<td align=\"left\" class=\"esquerda\">")[1].split(
                "</td>")[0]
            team2 = i.split(
                "<td align=\"right\" class=\"direita\">")[1].split(
                "</td>")[0]

            self.teams_col1.append(team1)
            self.teams_col2.append(team2)
            self.result_col1.append(int(res_col1))
            self.result_col2.append(int(res_col2))

        tmp = fields[4].replace("<tr >", "<tr>").split("<tr>")

        acert14 = tmp[2].split("<td class=\"meio\">")[2].split("</td>")[0]
        prem14 = tmp[2].split("<td class=\"direita\">")[1].split("</td>")[0]
        acert13 = tmp[3].split("<td class=\"meio\">")[2].split("</td>")[0]
        prem13 = tmp[3].split("<td class=\"direita\">")[1].split("</td>")[0]

        self._add_winner("13", acert13, prem13)
        self._add_winner("14", acert14, prem14)

        if(self.winners["14"][0] != 0):
            self.winners_location = self.format_winners(fields[5])

        final_draw = self._parse_final_draw(fields[9])
        self.final_draw = self._convert_string_float(final_draw[0])
        self.final_prize_pool = self._convert_string_float(final_draw[1])

        self.next_prize_pool = self._convert_string_float(fields[10])
        self.next_draw_date = fields[11]
        self.total_revenue = self._convert_string_float(fields[12])

        return True


class LotecaMatches(LotteryCaixa, object):
    def __init__(self):
        super(LotecaMatches, self).__init__()

        self.teams_col1 = []
        self.teams_col2 = []
        self.matches_date = []

        # Replace default host
        self.host = "www.loterias.caixa.gov.br"
        self.lottery_type_url = \
            "/wps/portal/loterias/landing/loteca/programacao"

        self.next_prize_pool = None
        self.accumulated = None
        self.final_accumulated = None

        self.final_draw = None

        self.xml = None

    def __str__(self):
        text_array = []

        text_array.append("LotecaMatches:")
        text_array.append("draw: %s" % str(self.draw))
        text_array.append("draw_date: %s" % str(self.draw_date))
        text_array.append("next_prize_pool: %s" % str(self.next_prize_pool))
        text_array.append(
            "accumulated from 14 matches: %s" % str(self.accumulated))
        text_array.append(
            "accumulated for final draw: %s" % str(self.final_accumulated))
        text_array.append("final_draw: %s" % str(self.final_draw))
        text_array.append("host: %s" % str(self.host))
        text_array.append("lottery_type_url: %s" % str(self.lottery_type_url))

        text_array.append("teams_col1: %s" % str(self.teams_col1))
        text_array.append("teams_col2: %s" % str(self.teams_col2))
        text_array.append("matches_date: %s" % str(self.matches_date))

        return "\n".join(text_array)

    def get_result(self):
        """These get result retrieve data from new URL from Caixa.
        It's only retrieve the last matches.

        Args:
            draw: lottery draw number (default: None).

        Returns:
            Return core representing error:

        """
        url = "http://" + self.host + self.lottery_type_url

        result = self.http_request(url)
        if(type(result) is int):
            return result

        # Parse data content
        if(self._parse_result(result.read()) is False):
            # If parser result fails, it returns the error code
            return self.ERROR_DATA_CONTENT

        return self.SUCCESS

    def _parse_result(self, data):
        """Parse Loteca matches HTML data from Caixa.

        This parser take div with class "resultado-loteria" and parse it
        to XML DOM object to access Loteca matches data.
        """
        dev_start_str = "<div class=\"resultado-loteria\">"
        result_div = data.split(dev_start_str)[1]

        div_end_str = "<div class=\"wpthemeClear\">"
        result_div = result_div.split(div_end_str)[0]

        # Add XML header to
        xml_version = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"

        result_div = xml_version + dev_start_str + result_div

        # Remove tabspaces, newlines and HTML special chars
        tmp = result_div.replace("\t", "")
        tmp = tmp.replace("\r\n", "").replace("> <", "><")
        tmp = tmp.replace("&nbsp;", "")

        # Fix mal-formed tags syntax when loaded from site
        tmp = tmp.replace("imgsrc=", "img src=")
        tmp = tmp.replace(".png\">", ".png\"/>")
        tmp = tmp.replace("spanclass", "span class")

        # Remove lasts </div> from parent tags
        tmp = tmp.replace("</div></div></div>", "")

        # Load XML DOM with Loteca Matches data
        self.xml = parseString(tmp)
        # print(self.xml.toprettyxml())

        # from xml.dom.minidom import parse

        # self.xml = parse("tmp.xml")
        # print(self.xml.toxml())

        conc_tag = self.xml.getElementsByTagName("small")[0]
        self.draw = conc_tag.firstChild.data.split("(")[0].split(" ")[1]
        self.draw_date = conc_tag.firstChild.data.split("(")[1].split(",")[0]

        tbody = self.xml.getElementsByTagName("tbody")[0]
        fields = tbody.getElementsByTagName("tr")
        for tr in fields:
            td_list = tr.getElementsByTagName("td")
            team1 = td_list[2].firstChild.data
            team2 = td_list[4].firstChild.data
            match_day = td_list[6].firstChild.data

            self.teams_col1.append(team1)
            self.teams_col2.append(team2)
            self.matches_date.append(match_day)

        prize_pool_div = self.xml.getElementsByTagName("div")[1]
        prize_pool_p = prize_pool_div.getElementsByTagName("p")[1]
        prize_pool_str = prize_pool_p.firstChild.data

        self.next_prize_pool = \
            self._convert_string_float(prize_pool_str.split(" ")[1])

        accumulated_div = self.xml.getElementsByTagName("div")[2]
        accumulated_p = accumulated_div.getElementsByTagName("p")[0]
        accumulated_span = accumulated_p.getElementsByTagName("span")[1]

        self.accumulated = \
            self._convert_string_float(
                accumulated_span.firstChild.data.replace("R$", ""))

        final_accumulated_p = accumulated_div.getElementsByTagName("p")[1]
        final_accumulated_span = \
            final_accumulated_p.getElementsByTagName("span")[1]
        self.final_accumulated = \
            self._convert_string_float(
                final_accumulated_span.firstChild.data.replace("R$", ""))

        final_draw_span = \
            final_accumulated_p.getElementsByTagName("span")[0]

        self.final_draw = \
            int(final_draw_span.firstChild.data.split("(")[1].split(")")[0])

        return True


class Federal(LotteryCaixa, object):
    def __init__(self):
        super(Federal, self).__init__()

        self.prize_list = []

        self.lottery_type_url = \
            "/loterias/loterias/federal/federal_pesquisa.asp"

    def __str__(self):
        text_array = []

        text_array.append("Federal:")
        text_array.append("draw: %s" % str(self.draw))
        text_array.append("draw_date: %s" % str(self.draw_date))
        text_array.append("draw_city: %s" % str(self.draw_city))
        text_array.append("draw_state: %s" % str(self.draw_state))
        text_array.append("number_list: %s" % str(self.number_list))
        text_array.append("winners_location: %s" % str(self.winners_location))
        text_array.append(
            "get_total_numbers(): %s" % str(self.get_total_numbers()))

        text_array.append("lottery_type_url: %s" % str(self.lottery_type_url))
        text_array.append("prize_list: %s" % str(self.prize_list))

        return "\n".join(text_array)

    def format_winners(self, winners_str):
        """Format winners based on Federal Lottery string template.

        Args:
            winners_str: winners string with winners location.

        Returns:
            List of location of winners.
        """

        # Possible winners string cases
        # winners_str = (
        #     "OS BILHETES GANHADORES DO PRIMEIRO DISTRIBU\xcdDOS FORAM"
        #     " DISTRIBU\xcdDOS"
        #     " PARA"
        #     " ALTA FLORESTA/MT (S\xc9RIE A) E S\xc3O PAULO/SP (S\xc9RIE B).")

        # winners_str = (
        #     "OS BILHETES GANHADORES DO PRIMEIRO DISTRIBU\xcdDOS FORAM"
        #     " DISTRIBU\xcdDOS PARA"
        #     " S\xc3O PAULO/SP (S\xc9RIE A E S\xc9RIE B).")

        # winners_str = (
        #     "OS BILHETES GANHADORES DO 1\xba PR\xcaMIO FORAM"]
        #     " DISTRIBU\xcdDOS,"
        #     " S\xc9RIE A e B, FORAM DISTRIBU\xcdDOS PARA S\xc3O PAULO/SP")

        test_string = "DISTRIBU\xcdDOS PARA "

        winners_array = []

        if(winners_str.find(test_string) != -1):
            winners_part = winners_str.split(test_string)[1]

            new_winners = winners_part.replace(" (S\xc9RIE A)", "")
            new_winners = new_winners.replace(" (S\xc9RIE B).", "")
            new_winners = new_winners.replace(
                " (S\xc9RIE A E S\xc9RIE B).", "")

            winners_array = new_winners.split(" E ")

        return winners_array

    def _parse_result(self, data):
        fields = data.split("|")

        # for i, field_data in enumerate(fields):
        #     print i, field_data

        if(len(fields) < 5):
            print(
                "LotecaResult data content without result data: %r" % (data))
            return False

        self.draw = fields[2]
        self.draw_date = fields[16]

        self.draw_city = fields[3]
        self.draw_state = fields[4]

        self.number_list = []
        self.number_list.append(self._convert_string_int(fields[6]))
        self.number_list.append(self._convert_string_int(fields[8]))
        self.number_list.append(self._convert_string_int(fields[10]))
        self.number_list.append(self._convert_string_int(fields[12]))
        self.number_list.append(self._convert_string_int(fields[14]))

        self.prize_list.append(self._convert_string_float(fields[7]))
        self.prize_list.append(self._convert_string_float(fields[9]))
        self.prize_list.append(self._convert_string_float(fields[11]))
        self.prize_list.append(self._convert_string_float(fields[13]))
        self.prize_list.append(self._convert_string_float(fields[15]))

        self.winners_location = self.format_winners(fields[17])

    def get_total_numbers(self):
        if(self.number_list is not None):
            total = 0
            for i in self.number_list:
                total += int(i)
            return total

        return None


class Bicho(LotteryCaixa, object):
    def __init__(self):
        self.data = ""
        self.datasemana = ""
        self.federal = False
        self.federalData = ""
        self.res11 = []
        self.res14 = []
        self.res18 = []
        self.res21 = []

    def getResultado(self):
        url = "http://www.ojogodobicho.com/deu_no_poste.htm"

        result = self.http_request(url)
        if ((result == 1) or (result == 2) or (result == 3)):
            return result

        data = result.read()
        # pega o campo com os resultados
        tmp = data.split("<tbody>")[1].split("</tbody>")[0]

        tmp = tmp.replace("<tr>", "")
        tmp = tmp.replace("</tr>", "")
        tmp = tmp.replace("<td>", "")
        tmp = tmp.replace("</td>", "")
        tmp = tmp.replace("</b>", "")
        tmp = tmp.replace("\t", "")
        tmp = tmp.replace("-", "")
        tmp = tmp.replace("\r\n", "")
        tmp = tmp.replace(" ", "")
        tmp = tmp.split("<b>")

        resultado = []

        # Caso nao exista o sorteio das 21 nos Sabados
        if (len(tmp) == 43):
            for i in range(0, 20):
                resultado.append(tmp[1 + (i * 2)])

            for i in range(0, 6):
                self.res11.append(resultado[i * 3])
                self.res14.append(resultado[i * 3 + 1])
                self.res18.append(resultado[i * 3 + 2])
                self.res21.append("0.000")
        else:
            for i in range(0, 27):
                resultado.append(tmp[1 + (i * 2)])

            for i in range(0, 6):
                self.res11.append(resultado[i * 4])
                self.res14.append(resultado[i * 4 + 1])
                self.res18.append(resultado[i * 4 + 2])
                self.res21.append(resultado[i * 4 + 3])
        self.data = date.today().strftime("%d/%m/%Y")
        self.datasemana = date.today().isoweekday()

        # Busca resulado da Federal se for quarta ou sabado
        if((self.datasemana == 3) or (self.datasemana == 6)):
            self.getFederal(0)
