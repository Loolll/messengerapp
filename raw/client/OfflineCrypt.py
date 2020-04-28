# OfflineCrypt.py


class EncryptEN:
    ALPHABET = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
                'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    ALLOWED_MESSAGE_SYMBOLS = ALPHABET.copy() + [x for x in """1234567890!@#$%^~&*()[]{}-+_=><?,./\\ "'|№;:"""] + ['\n']
    # Initialize ASCII
    ORD_LOWER_MIN = 97
    ORD_LOWER_MAX = 122
    ORD_UPPER_MIN = 65
    ORD_UPPER_MAX = 90

    @staticmethod
    def __enc_alphabet_gen_linear(key: str):
        """ Generating of encryption alphabet via linear shift. """
        assert all([x in EncryptEN.ALPHABET for x in key]), 'Disallowed symbols.'
        assert all([x == 1 for x in [key.lower().count(symbol) for symbol in key.lower()]]), 'Repeating symbols.'

        enc_alphabet = [x for x in key.upper()]
        enc_alphabet += list(filter(lambda x: x is not None, [x if x not in enc_alphabet else None for x in
                                                              EncryptEN.ALPHABET[:26]]))
        enc_alphabet += [x for x in ("".join(enc_alphabet)).lower()]

        return enc_alphabet

    @staticmethod
    def __hash_sum_gen(key: str, length: int):
        """ Generation of hash sum for vertical shift.
            Math algorithm for process of calculating hash sum:
             sum(ASCII(i)^2 <-i- every symbol of key) * key length^2 """
        assert all([x in EncryptEN.ALPHABET for x in key]), 'Disallowed symbols.'

        hash_sum = str(sum([ord(x)**2 for x in key]) * len(key)**2)
        hash_len = int(len(hash_sum))  # Need to optimize algorithm

        return hash_sum[:length] if length < hash_len else (hash_sum*(length//hash_len+1))[:length] if \
            hash_len % length != 0 else (hash_sum*(length//hash_len))[:length]

    @staticmethod
    def __shift(symbol: str, count: int):
        """ ASCII vertical shift"""
        assert len(str(abs(count))) < 2, " Shift must be in range of [-9, 9]"
        # assert to check allowed symbols doesn't need in cause of private method

        if symbol.islower():
            if ord(symbol) + count > EncryptEN.ORD_LOWER_MAX:
                return chr(EncryptEN.ORD_LOWER_MIN + (ord(symbol) + count - EncryptEN.ORD_LOWER_MAX) - 1)
            elif ord(symbol) + count < EncryptEN.ORD_LOWER_MIN:
                return chr(EncryptEN.ORD_LOWER_MAX + (ord(symbol) + count - EncryptEN.ORD_LOWER_MIN) + 1)
            else:
                return chr(ord(symbol) + count)
        else:
            if ord(symbol) + count > EncryptEN.ORD_UPPER_MAX:
                return chr(EncryptEN.ORD_UPPER_MIN + (ord(symbol) + count - EncryptEN.ORD_UPPER_MAX) - 1)
            elif ord(symbol) + count < EncryptEN.ORD_UPPER_MIN:
                return chr(EncryptEN.ORD_UPPER_MAX + (ord(symbol) + count - EncryptEN.ORD_UPPER_MIN) + 1)
            else:
                return chr(ord(symbol) + count)

    @staticmethod
    def __parse_in(text: str):
        """ Function will parse some UTF-8 symbols in ~^ABCD^~ where ABCD are letters but in the sense of numbers
            of ASCII code of this symbol.
            For example: Russian word 'п{1087}р{1088}и{1080}в{1074}е{1077}т{1090}' (in {} ASCII code of symbol) will
            transform into --> '~^BAIH^~~^BAII^~~^BAIA^~~^BAHE^~~^BAHH^~~^BAJA^~' """

        return "".join([('~^' + "".join([EncryptEN.ALPHABET[int(xx)] for xx in str(x)]) + '^~')
                        if chr(x) not in EncryptEN.ALLOWED_MESSAGE_SYMBOLS else chr(x) for x in [ord(x) for x in text]])

    @staticmethod
    def __parse_out(text: str):
        """ Function that has reverse process of __parse_in func"""
        result = str("")
        buffer = str("")
        for i in range(len(text)):
            # Parsing every symbol in i
            if text[i] == '~' and i != len(text)-1 and text[i+1] == '^':
                buffer = '~^'
            elif text[i] == '~' and i != 0 and text[i-1] == '^' and buffer != "":
                # Decrypt from buffer to result and clean buffer
                result += chr(int("".join([str(EncryptEN.ALPHABET.index(x)) for x in buffer[2:]])))
                buffer = ""
            else:
                if '~^' in buffer:
                    if text[i] != '^':
                        buffer += text[i]
                else:
                    result += text[i]
        return result

    @staticmethod
    def encrypt(key: str, message: str):
        """ Encrypting message """
        assert not message.count('~') and not message.count('^'), "Disallowed '^' or '~'."
        try:
            message = EncryptEN.__parse_in(message)
        except UnicodeError:
            exit('Disallowed symbols.')

        alphabet_enc = EncryptEN.__enc_alphabet_gen_linear(key)  # Getting encrypted alphabet
        hash_sum = EncryptEN.__hash_sum_gen(key, len(message))  # Getting hash key

        return "".join([
            EncryptEN.__shift(alphabet_enc[EncryptEN.ALPHABET.index(symbol)], int(shift)) if
            symbol in EncryptEN.ALPHABET else symbol for symbol, shift in zip(message, str(hash_sum))
        ])  # Return encrypted message

    @staticmethod
    def decrypt(key: str, message: str):
        """ Decrypting message """
        assert all([x in EncryptEN.ALLOWED_MESSAGE_SYMBOLS for x in message]), 'Disallowed symbols.'

        alphabet_enc = EncryptEN.__enc_alphabet_gen_linear(key)  # Getting encrypted alphabet
        hash_sum = EncryptEN.__hash_sum_gen(key, len(message))  # Getting hash key

        return EncryptEN.__parse_out("".join([
            EncryptEN.ALPHABET[alphabet_enc.index(EncryptEN.__shift(symbol, 0-int(shift)))]
            if symbol in EncryptEN.ALPHABET else symbol for symbol, shift in zip(message, str(hash_sum))
        ]))  # Return decrypted message
