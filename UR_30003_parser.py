import struct
# add description later
# lets create a dictionary packet_layout that will contain info on packet structure

packet_layout = {
1 : ("Message_Size",4,1), # always equal to 812
2 : ("Time",8,1),
3 : ("q target" , 8,6),
4 : ("qd target" , 8,6),
5 : ("qdd target" , 8,6),
6 : ("I target" , 8,6),
7 : ("M target" , 8,6),
8 : ("q actual" , 8,6),
9 : ("qd actual" , 8,6),
10 : ("I actual" , 8,6),
11 : ("Tool Accelerometer values" , 8,3),
12 : ("Unused" , 8,15), # parses into 15 0.0
13 : ("TCP force" , 8,6),
14 : ("Tool vector" , 8,6),
15 : ("TCP speed" , 8,6),
16 : ("Digital input bits" , 8,1),
17 : ("Motor temperatures" , 8,6),
18 : ("Controller Timer" , 8,1),
19 : ("Test value" , 8,1),
20 : ("Robot Mode" , 8,1),
21 : ("Joint Modes" , 8,6)
}

def bytes2value(list_of_bytes):
    # if 4 then value is int if 8 then double
    # !NB it is expected that list_of_bytes are given as they come from the port
    list_of_bytes.reverse()
    value = 0
    if len(list_of_bytes) == 4:
        value = struct.unpack('I',bytearray(list_of_bytes))
        value = value[0]
    elif len(list_of_bytes) == 8:
        value = struct.unpack('d', bytearray(list_of_bytes))
        value = value[0]
    else:
        print('list_of_bytes length is not 4 or 8. Does not correspond to UR5 documentation. Returning 0')
    return  value

def parse(packet):
    # it is assumed that the packet is in list of decimal format
    if len(packet) != 812:
        print("packet length is not equal to 812, cannot parse")
        packet_parsed =[]
    else:
        i = 0
        packet_parsed = {}
        # for every item in library
        for j in xrange(packet_layout.__len__()):
            # for number of times that item repeats
            dummy = []
            for k in xrange(packet_layout[j+1][2]):
                dummy.append(bytes2value(packet[i:i+packet_layout[j+1][1]]))
                i +=  packet_layout[j+1][1]
            packet_parsed[packet_layout[j+1][0]] = dummy

    if packet_parsed["Message_Size"][0] != 812:
        print('invalid packet')
    return  packet_parsed
    
def pack_finder(msg):
    result = 0
    for i in xrange(msg.__len__()-812,-1,-1):
        tmp = msg[i:i+4]
        tmp.reverse()
        if  struct.unpack('I',bytearray(tmp))[0]== 812:
            result = parse(msg[i:i+812])
            
    if result == 0:
        print("Can not find full 812-size-package in msg")
    return result
