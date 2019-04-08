from myhdl import Signal, intbv,always, block

class AvalonMM():
    """ class to access Altera's avalon memory-mapped interface """
    def __init__(self, data_width=8, address_width=4):
        """ configure the memory-mapped interface with corresponding address and datawidth"""
        if not 32== data_width:
            raise ValueError("avalon memory-map bus data_width must be 32")
        if not 1 <= address_width  <= 32:
            raise ValueError("avalon memory-map bus address_width between 1-32")
        ## address bus
        self.address_i = Signal(intbv(0)[address_width:])
        ## write data bus
        self.writedata_i = Signal(intbv(0)[data_width:])
        ## write enable signal
        self.write_i = Signal(bool(0))
        ## read enable signal
        self.read_i = Signal(bool(0))
        ## read data bus
        self.readdata_o = Signal(intbv(0)[data_width:])

@block
def avalon_access(clk, avs_mm, address, read_data, write_data, read_enable, write_enable):
    """ function to support both read and write accesses over avalon memory-mapped interface """
    @always(clk.posedge)
    def avalon_bus_access():
      """ function to support either read or write operation """
      if(read_enable==1):
        avs_mm.address_i.next = address
        avs_mm.writedata_i.next = 0x0
        avs_mm.write_i.next = 0
        avs_mm.read_i.next = 1
        read_data.next = avs_mm.readdata_o
      elif(write_enable==1):
        avs_mm.address_i.next = address
        avs_mm.writedata_i.next = write_data
        avs_mm.write_i.next = 1
        avs_mm.read_i.next = 0
        read_data.next = 0x0

    return avalon_bus_access

class AvalonST_SNK():
    """ class to access Altera's streaming sink interface """
    def __init__(self, data_width=8, error_width=3, empty_width=3, channel_width=4):
        """ configure the streaming sink interface with corresponding datawidth and streaming related signal  """
        ## ready output signal
        self.ready_o = Signal(bool(0))
        ## start of packet input signal
        self.startofpacket_i = Signal(bool(0))
        ## end of packet input signal
        self.endofpacket_i = Signal(bool(0))
        ## valid input signal
        self.valid_i = Signal(bool(0))
        ## error input signal, currently not used
        self.error_i = Signal(intbv(0)[error_width:])
        ## empty input signal, currently not used
        self.empty_i = Signal(intbv(0)[empty_width:])
        ## channel input signal, currently not used
        self.channel_i = Signal(intbv(0)[channel_width:])
        ## data bus input signal
        self.data_i = Signal(intbv(0)[data_width:])
class AvalonST_SRC():
    """ class to access Altera's streaming source interface """
    def __init__(self, data_width=8, error_width=3, empty_width=3, channel_width=4):
        """ configure the streaming source interface with corresponding datawidth and streaming related signal  """
        ## ready input signal
        self.ready_i = Signal(bool(0))
        ## start of packet output signal
        self.startofpacket_o = Signal(bool(0))
         ## end of packet output signal
        self.endofpacket_o = Signal(bool(0))
         ## valid  output signal
        self.valid_o = Signal(bool(0))
         ## error output signal, currently not used
        self.error_o = Signal(intbv(0)[error_width:])
         ## empty output signal, currently not used
        self.empty_o = Signal(intbv(0)[empty_width:])
         ## channel output signal, currently not used
        self.channel_o = Signal(intbv(0)[channel_width:])
         ## data bus input signal
        self.data_o = Signal(intbv(0)[data_width:])

class AvalonST_SNK_ARRAY():
    """ class to access an array of streaming sink interfaces """
    def __init__(self, length=1, data_width=8, error_width=3, empty_width=3, channel_width=4):
        """ configure the streaming sink interface array with corresponding array length, datawidth, streaming related signal  """
        self.ready_o = Signal(intbv(0)[length:])
        self.startofpacket_i = Signal(bool(0))
        self.endofpacket_i =  Signal(intbv(0)[length:])
        self.valid_i =  Signal(intbv(0)[length:])
        self.error_i = Signal(intbv(0)[error_width:])
        self.empty_i = Signal(intbv(0)[empty_width:])
        self.channel_i = Signal(intbv(0)[channel_width:])
        self.data_i = Signal(intbv(0)[data_width*length:])

class AvalonST_SRC_ARRAY():
    """ class to access an array of streaming source interfaces """
    def __init__(self, length= 1, data_width=8, error_width=3, empty_width=3, channel_width=4):
        """ configure the streaming source interface array with corresponding array length, datawidth, streaming related signal  """
        self.ready_i = Signal(intbv(0)[length:])
        self.startofpacket_o = Signal(intbv(0)[length:])
        self.endofpacket_o = Signal(intbv(0)[length:])
        self.valid_o = Signal(intbv(0)[length:])
        self.error_o = Signal(intbv(0)[error_width:])
        self.empty_o = Signal(intbv(0)[empty_width:])
        self.channel_o = Signal(intbv(0)[channel_width:])
        self.data_o = Signal(intbv(0)[data_width*length:])

class PipelineST():
    """ class to access Pipeline Stream """
    def __init__(self, data_width=8, channel_width=4,init_data=0):
        """ Pipeline Stream Signals """
        ## start of packet output signal
        self.sop= Signal(bool(0))
         ## end of packet output signal
        self.eop= Signal(bool(0))
         ## valid  output signal
        self.valid = Signal(bool(0))
         ## channel output signal, currently not used
        self.channel = Signal(intbv(0)[channel_width:])
         ## data bus input signal
        if (isinstance(init_data,float)):
          self.data = Signal(float(0.0))
        else:
          self.data = Signal(intbv(0,min=-(2**(data_width-1)-1), max=(2**(data_width-1)-1)))#[data_width:])
        
