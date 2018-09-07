from myhdl import Signal, intbv

class SrcBuffer_Regs():
    def __init__(self, data_width=8, nb_status_regs=4):
        if not 32== data_width:
            raise ValueError("avalon memory-map bus data_width must be 32")
        self.ctrl_reg = Signal(intbv(0)[data_width:])
        self.nr_frames_dropped = Signal(intbv(0)[data_width:])
        self.nr_pixels_dropped_invalid_frame = Signal(intbv(0)[data_width:])
        self.nr_pixels_dropped_overflow = Signal(intbv(0)[data_width:])
        self.nr_pixels_stuffed = Signal(intbv(0)[data_width:])
        self.fifo_fill_level = Signal(intbv(0)[data_width:])
        self.fifo_max_level = Signal(intbv(0)[data_width:])
        self.nr_cycles_readylow_src = Signal(intbv(0)[data_width:])
        self.nr_cycles_readylow_validhigh_src = Signal(intbv(0)[data_width:])
        self.nr_datawords_snk = Signal(intbv(0)[data_width:])
        self.nr_datawords_src = Signal(intbv(0)[data_width:])
        self.reset_reg = Signal(intbv(0)[nb_status_regs:])

class srcbuffer_column_flush_regs():
    def __init__(self, nb_bits_parameter=16, nb_columnflush_regs=16):
        if not 16 == nb_bits_parameter:
            raise ValueError("Number of bits to represent column_flush startx, startx and width must be 16")
        if not 16 == nb_columnflush_regs:
            raise ValueError("Number of column_flush registers limited to 16")
        self.startx          = [Signal(intbv(0)[nb_bits_parameter:]) for i in range(nb_columnflush_regs)]
        self.starty          = [Signal(intbv(0)[nb_bits_parameter:]) for i in range(nb_columnflush_regs)]
        self.width           = [Signal(intbv(0)[nb_bits_parameter:])  for i in range(nb_columnflush_regs)]

