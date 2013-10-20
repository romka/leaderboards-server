__author__ = 'Roman Arkharov'

class Crypt:
    def __init__(self, sequence):
        self.sequence = sequence

    def convert(self, byte, key, direction):
        if direction is True:
            new = byte + key
            if new > 255:
                new -= 255
        else:
            new = byte - key
            if new < 0:
                new += 255
        return new

    def crypt(self, data):
        result = ''
        max_counter = len(self.sequence)
        counter = 0

        #log.msg('data to crypt ' + data)
        xxx = ''
        for i in range(0, len(data)):
            ch = self.convert(ord(data[i: i + 1]), self.sequence[counter], True)
            ch = str(ch)
            while len(ch) < 3:
                ch = '0' + ch

            result += ch

            xxx += data[i: i + 1] + ' => ' + str(ord(data[i: i + 1])) + ' => ' + ch + ' ||| '

            counter += 1
            if counter >= max_counter:
                counter = 0

        #log.msg('crypted chars')
        #log.msg(xxx)
        #log.msg('crypt result')
        #log.msg(result)

        return result

    def decrypt(self, data):
        result = ''
        max_counter = len(self.sequence)
        counter = 0

        xxx = ''
        for i in range(0, len(data), 3):
            ch = int(data[i: i + 3])
            ch2 = self.convert(ch, self.sequence[counter], False)

            #xxx = xxx + ', ' + str(ch2)
            xxx = xxx + 'ch = ' + str(ch) + ', ch2 = ' + str(ch2) + ' ||| '

            result += chr(ch2)

            counter += 1
            if counter >= max_counter:
                counter = 0

        #log.msg('decrypted chars')
        #log.msg(xxx)

        return result

