# Python class to connect and control Robotiq 3-f gripper
# Writing with python 3.5

class Robotiq_USB:

    def __init__(self, LINUX_PORT = '/dev/ttyUSB1',WIN_PORT = 'COM6' , my_baudrate=115200):
        import sys
        import serial

        # Variables
        self.gripper_status = []          # 
        self.current = [0,0,0]            # Last current value in finger A,B,C
        self.position = [0,0,0]           # Last position of finger A,B,C
        self.echo_position = [0,0,0]      # The position request echo tells that the command was well received 
        # Create connection via PC and gripper. Depends on running OS
        try: 
            if sys.platform.startswith('linux'):
                self.stream = serial.Serial( port = LINUX_PORT, baudrate = my_baudrate, timeout=1, parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
            elif sys.platform.startswith('win'):
                self.stream = serial.Serial( port = WIN_PORT, baudrate = my_baudrate, timeout=1, parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
        except ( ValueError, SerialException):
            self.stream.close()
            print('dad')
            raise ConnectionError

        self.update_status()

        # Activate gripper
        if self.gripper_status[4] != 1:
            status_counter = 0
            self.send_command([b"\x09\x10\x03\xE8\x00\x03\x06\x01\x00\x00\x00\x00\x00\x72\xE1"])
            while self.gripper_status[1] != 3:

                self.update_status()
                if status_counter == 10000:
                    self.stream.close()
                    raise TimeoutError
    
    def str_to_bin(self,my_str):
        import binascii
        return binascii.unhexlify(my_str)
            
    def update_status(self):
        # Updates grippers status, position, current
        import binascii
        import serial
        
        self.stream.write(b"\x09\x03\x07\xD0\x00\x08\x45\xC9")
        data = binascii.hexlify(self.stream.readline())
        data_status = format(int(data[6:10],16),'0>16b')
        data_status = [data_status[0:2],data_status[2:4],data_status[4],data_status[5:7],data_status[7],
                       data_status[8:10],data_status[10:12],data_status[12:14],data_status[14:16]]
        self.gripper_status = [ int(i,2) for i in data_status ]
        self.current = [data[16:18],data[22:24],data[28:30]]
        self.current = [ int(i,16) for i in self.current ]
        self.echo_position = [data[12:14],data[18:20],data[24:26]]
        self.echo_position = [ int(i,16) for i in self.echo_position ]
        self.position = [data[14:16],data[20:22],data[26:28]]
        self.position = [ int(i,16) for i in self.position ]
        return data_status

    def move(self,mode,pos,speed,force):
        mode = format(mode, '0>2b')

        msg_mode = "{0:0>2X}".format(int('00001' + mode + '1', 2))
        msg_pos = format(hex(pos)[2:],'0>2')
        msg_speed = format(hex(speed)[2:], '0>2')
        msg_force = format(hex(force)[2:], '0>2')

        check = self.crc16('091003E8000306' + msg_mode + '0000' + msg_pos + msg_speed + msg_force)
        self.send_command([b"\x09\x10\x03\xE8\x00\x03\x06", self.str_to_bin(msg_mode),
                           b"\x00\x00", self.str_to_bin(msg_pos),self.str_to_bin(msg_speed), self.str_to_bin(msg_force), check])
        
    def close(self,mode = None, pos = 255, speed = 255, force = 255):
        # Closes gripper on basic configuration.
        if mode is None:
            mode = self.gripper_status[3]
        self.move(mode,pos,speed,force)
        self.update_status()
        
    def open(self,mode = None, pos = 0, speed = 255, force = 255):
        # Opens gripper on basic configuration.
        if mode is None:
            mode = self.gripper_status[3]
        self.move(mode, pos, speed, force)
        self.update_status()
        
    def check_object(self):
        while True:
            self.update_status()
            if self.gripper_status[0] == 3: return False
            elif self.gripper_status[0] == 0: continue
            else: return True
            
    def set_mode(self,mode):

        mode = format(mode,'0>2b')
        full_mode =  "{0:0>2X}".format(int('00001' + mode + '1',2)) + '00'
        check = self.crc16('090603E8' + full_mode )

        self.send_command([b'\x09\x06\x03\xE8', self.str_to_bin(full_mode),check])
        self.update_status()
        while self.gripper_status[1] != 3:
            self.update_status()

    def deactivate(self):
        check = self.crc16('090603E80000')
        self.send_command([b'\x09\x06\x03\xE8\x00\x00',check])


    def send_command(self,array):
        import serial
        for item in array:
            self.stream.write(item)
        self.stream.readline()

    def exit(self):
        import serial
        self.stream.close()

    def crc16(self, data, bits=8):
        crc = 0xFFFF
        for op, code in zip(data[0::2], data[1::2]):
            crc = crc ^ int(op + code, 16)
            for bit in range(0, bits):
                if (crc & 0x0001) == 0x0001:
                    crc = ((crc >> 1) ^ 0xA001)
                else:
                    crc = crc >> 1
        return self.typecasting(crc)

    def typecasting(self, crc):
        msb = hex(crc >> 8)
        lsb = hex(crc & 0x00FF)
        msg = (lsb + msb).split('0x')

        res = "{0:0>2}".format(msg[1]) + "{0:0>2}".format(msg[2])
        return self.str_to_bin(res)

    def move_finger(self, positions, speeds, forces, scissors = False):
        msg_pos = [format(hex(a)[2:], '0>2') for a in positions]
        msg_speed = [format(hex(a)[2:], '0>2') for a in speeds]
        msg_force = [format(hex(a)[2:], '0>2') for a in forces]

        if scissors: msg_mode = '0908'
        else: msg_mode = '0904'
        msg = '00' + msg_pos[0] + msg_speed[0] + msg_force[0] + \
              msg_pos[1] + msg_speed[1] + msg_force[1] + \
              msg_pos[2] + msg_speed[2] + msg_force[2] + \
              msg_pos[3] + msg_speed[3] + msg_force[3] + '00'

        check = self.crc16('091003E8000810' + msg_mode + msg)
        self.send_command([b"\x09\x10\x03\xE8\x00\x08\x10", self.str_to_bin(msg_mode),
                           self.str_to_bin(msg), check])