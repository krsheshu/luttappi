from myhdl import Signal, intbv

class srcbuffer_sync_signals_interface():
    def __init__(self, index_width=12):
        if not 12 == index_width:
            raise ValueError("column and row index_width must be 32")
        self.column_index = Signal(intbv(0)[index_width:])
        self.row_index    = Signal(intbv(0)[index_width:])
        self.column_flush = Signal(bool(0))

