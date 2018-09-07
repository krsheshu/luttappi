from myhdl import Signal, intbv

class framegrabber_imager_interface():
    def __init__(self, interface_width=90):
        if not 90== interface_width:
            raise ValueError("Imager interface width must be 90")
        self.data_i       = Signal(intbv(0)[interface_width:])
        self.clk_i        = Signal(bool(0))
        self.reset_i      = Signal(bool(0))
        self.reset_o      = Signal(bool(0))
        self.clkout_on_o  = Signal(bool(0))

class framegrabber_phasealignment_interface():
    def __init__(self, nb_channels=9):
        if not 9 == nb_channels:
            raise ValueError("Number of LVDS channels must be 9 (8 data and 1 sync)")
        self.channel_align_o = Signal(intbv(0)[nb_channels:])
        self.cntsel_o        = Signal(bool(0))
        self.sclk_o          = Signal(bool(0))
        self.phase_en_o      = Signal(bool(0))
        self.updn_o          = Signal(bool(0))
        self.phase_done_i    = Signal(bool(0))

class framegrabber_trigger_interface():
    def __init__(self, external_trigger_datawidth=2400):
        if not 2400 == external_trigger_datawidth:
            raise ValueError("Datawidth from trigger module does not match")
        self.ext_data_i       = Signal(intbv(0)[external_trigger_datawidth:])
        self.ext_data_valid_i = Signal(bool(0))
        self.ext_data_clr_i   = Signal(bool(0))
        self.dummy_profile    = Signal(bool(0))
        self.last_profile     = Signal(bool(0))
        self.frame_valid_o    = Signal(bool(0))
        self.skipping_done_o  = Signal(bool(0))

class framegrabber_sync_flags_interface():
    def __init__(self, nb_bits_roi_id=3):
        if not 3 == nb_bits_roi_id:
            raise ValueError("Number of bits for roi_id does not match")
        self.roi_id           = Signal(intbv(0)[nb_bits_roi_id:])
        self.line_start      = Signal(bool(0))
        self.line_end        = Signal(bool(0))
        self.frame_start       = Signal(bool(0))
        self.frame_end         = Signal(bool(0))
        self.frame_end_multiroi= Signal(bool(0))

