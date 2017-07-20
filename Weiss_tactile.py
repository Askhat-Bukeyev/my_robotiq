# Class to connect with Weiss tactile sensor
# writing on python 2.7

class Weiss_tactile():

    def __init__(self, PORT='/dev/ttyACM0',BAUDRATE = 115200):
        import serial
        import numpy

        self.lenght = 6
        self.weight = 4
        self.frame = numpy.zeros( (self.lenght,self.weight))

        self.stream = serial.Serial(port=PORT, baudrate=BAUDRATE, timeout=1, parity=serial.PARITY_NONE,
                               stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
        if not self.stream.isOpen(): self.stream.close()

    def read_frame(self):
        import binascii
        self.stream.write("\xAA\xAA\xAA\x20\x01\x00\x00\x8F\x83")
        msg = binascii.hexlify(self.stream.readline())
        return msg

    def parse(self,msg):
        if (int(msg[12:16],16) != 0):
            print ("Can't parse! We recieved error.")
            return -1

        parsed_data = [c+d+a+b for a,b,c,d in zip(msg[26::4],msg[27::4],msg[28::4],msg[29::4])]
        for i in xrange(self.lenght):
            self.frame[i] = [int(item,16) for item in parsed_data[i*4:(i+1)*4]]

    def update(self):
        msg = self.read_frame()
        self.parse(msg)

    def get_frame(self):
        self.update()
        return self.frame