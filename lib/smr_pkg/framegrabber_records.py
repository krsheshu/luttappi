from myhdl import Signal, intbv

class framegrabber_syncfifo_output():
    def __init__(self, data_width=90):
        if not 90== data_width:
            raise ValueError("FIFO data_width must be 90")
        self.data_o       = Signal(intbv(0)[data_width:])
        self.valid_o      = Signal(bool(0))

class framegrabber_roi():
    def __init__(self, nb_bits_roi=16):
        if not 16 == nb_bits_roi:
            raise ValueError("Number of bits to represent ROI must be 16")
        self.roi_width          = Signal(intbv(0)[nb_bits_roi:])
        self.roi_height         = Signal(intbv(0)[nb_bits_roi:])
        self.roi_width_offset   = Signal(intbv(0)[nb_bits_roi:])
        self.roi_height_offset  = Signal(intbv(0)[nb_bits_roi:])

class framegrabber_control_register():
    def __init__(self, nb_bits_max_supported_rois=4):
        if not 4 == nb_bits_max_supported_rois:
            raise ValueError("Number of bits of control register must be 12")
        self.reserved            = Signal(bool(0))
        self.img_reset_o         = Signal(bool(0))
        self.img_clkout_on_o     = Signal(bool(0))
        self.start_condition_i   = Signal(bool(0))
        self.nb_supported_rois   = Signal(intbv(0)[nb_bits_max_supported_rois:])
        self.remapper_enable_i   = Signal(bool(0))
        self.subsampling_i       = Signal(bool(0))
        self.lvds_sync_ok_i      = Signal(bool(0))
        self.crc_startcond_i     = Signal(bool(0))

class framegrabber_streaming_status_register():
    def __init__(self, nb_bits_streaming_fsm=3):
        if not 3 == nb_bits_streaming_fsm:
            raise ValueError("Number of bits of streaming FSM register must be 3")
        self.streaming_fsm       = Signal(intbv(0)[nb_bits_streaming_fsm:])
        self.userfifo_empty      = Signal(bool(0))
        self.datafifo_empty      = Signal(bool(0))

class framegrabber_frame_sync_flags():
    def __init__(self):
        self.frame_valid        = Signal(bool(0))
        self.frame_start        = Signal(bool(0))
        self.frame_end          = Signal(bool(0))
        self.frame_end_multiroi = Signal(bool(0))

class framegrabber_crc_data():
    def __init__(self, nb_bits_crc_debug=160, nb_bits_crc_error_cnt=256):
        if not 160 == nb_bits_crc_debug:
            raise ValueError("Number of bits of CRC debug data must be 160")
        self.debug               = Signal(intbv(0)[nb_bits_crc_debug:])
        self.error_cnt           = Signal(intbv(0)[nb_bits_crc_error_cnt:])
        self.error_pulse         = Signal(bool(0))
        self.error_cnt_reset     = Signal(bool(0))

class framegrabber_frame_id():
    def __init__(self, nb_bits_frame_id=16):
        if not 16 == nb_bits_frame_id:
            raise ValueError("Number of bits of frame id must be 16")
        self.id               = Signal(intbv(0)[nb_bits_frame_id:])
        self.reset            = Signal(bool(0))

class framegrabber_remapper_output():
    def __init__(self, data_width=160):
        if not 160== data_width:
            raise ValueError("Remapper data_width must be 160")
        self.data_o       = Signal(intbv(0)[data_width:])
        self.valid_o      = Signal(bool(0))

class framegrabber_line_sync_flags():
    def __init__(self):
        self.line_start        = Signal(bool(0))
        self.line_end          = Signal(bool(0))

class framegrabber_bitdepthconverter_output():
    def __init__(self, data_width=128):
        if not 128== data_width:
            raise ValueError("Bitdepth converter data_width must be 160")
        self.data_o       = Signal(intbv(0)[data_width:])
        self.valid_o      = Signal(bool(0))

class framegrabber_roi_list():
    def __init__(self, nb_bits_roi=16, nb_supported_rois=8):
        if not 16 == nb_bits_roi:
            raise ValueError("Number of bits to represent ROI must be 16")
        if not 8 == nb_supported_rois:
            raise ValueError("Number of supported ROIs must be 16")
        self.roi_width          = [Signal(intbv(0)[nb_bits_roi:]) for i in range(nb_supported_rois)]
        self.roi_height         = [Signal(intbv(0)[nb_bits_roi:]) for i in range(nb_supported_rois)]
        self.roi_width_offset   = [Signal(intbv(0)[nb_bits_roi:]) for i in range(nb_supported_rois)]
        self.roi_height_offset  = [Signal(intbv(0)[nb_bits_roi:]) for i in range(nb_supported_rois)]

