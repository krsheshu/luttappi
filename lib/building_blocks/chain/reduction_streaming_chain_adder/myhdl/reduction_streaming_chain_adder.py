from myhdl import always, always_comb, Signal, instances
from avalon_buses import AvalonST_SNK, AvalonST_SRC
from streaming_simple_adder import StreamingSimpleAdderPars, StreamingSimpleAdder
from common_functions import simple_wire_assign, simple_reg_assign 

class StreamingChainAdderPars():
  def __init__(self):
    """ StreamingChainAdder pars """
    self.NB_CHAIN_ADDERS=32
    self.SNK0_DATAWIDTH=32
    self.SNK1_DATAWIDTH=32
    self.SRC_DATAWIDTH=32
    self.a=0
  def __call__(self, pars):
    self.NB_CHAIN_ADDERS=pars.NB_CHAIN_ADDERS
    self.SNK0_DATAWIDTH   = pars.SNK0_DATAWIDTH
    self.SNK1_DATAWIDTH   = pars.SNK1_DATAWIDTH
    self.SRC_DATAWIDTH    = pars.SRC_DATAWIDTH


class StreamingChainAdder():
  """ StreamingChainAdder Top """
  def __init__(self):
    pass

  def block_connect(self, pars, reset, clk, av_snk0, av_snk1, av_src):
    """ streaming_simple adder block"""

    av_snk0_if  = [AvalonST_SNK(pars.SNK0_DATAWIDTH) for i in range(pars.NB_CHAIN_ADDERS)]
    av_snk1_if  = [AvalonST_SNK(pars.SNK1_DATAWIDTH) for i in range(pars.NB_CHAIN_ADDERS)]
    av_src_if   = [AvalonST_SRC(pars.SRC_DATAWIDTH) for i in range(pars.NB_CHAIN_ADDERS)]


    add_pars = StreamingSimpleAdderPars()
    add_pars.SNK0_DATAWIDTH = pars.SNK0_DATAWIDTH 
    add_pars.SNK1_DATAWIDTH = pars.SNK1_DATAWIDTH 
    add_pars.SRC_DATAWIDTH  = pars.SRC_DATAWIDTH

    
    snk0_valid_inst = [None for i in range(pars.NB_CHAIN_ADDERS)]
    snk0_data_inst  = [None for i in range(pars.NB_CHAIN_ADDERS)]
    snk0_ready_inst = [None for i in range(pars.NB_CHAIN_ADDERS)]
    snk1_valid_inst = [None for i in range(pars.NB_CHAIN_ADDERS)]
    snk1_data_inst  = [None for i in range(pars.NB_CHAIN_ADDERS)]
    snk1_ready_inst = [None for i in range(pars.NB_CHAIN_ADDERS)]
    src_valid_inst  = [None for i in range(pars.NB_CHAIN_ADDERS)]
    src_data_inst   = [None for i in range(pars.NB_CHAIN_ADDERS)]
    src_ready_inst  = [None for i in range(pars.NB_CHAIN_ADDERS)]

    for i in range(pars.NB_CHAIN_ADDERS):
      snk0_valid_inst[i]  = simple_wire_assign(av_snk0_if[i].valid_i, av_snk0[i].valid_i)
      snk0_data_inst[i]   = simple_wire_assign(av_snk0_if[i].data_i, av_snk0[i].data_i)
      snk0_ready_inst[i]  = simple_wire_assign(av_snk0[i].ready_o, av_snk0_if[i].ready_o)

      snk1_valid_inst[i]  = simple_wire_assign(av_snk1_if[i].valid_i , av_snk1[i].valid_i)
      snk1_data_inst[i]   = simple_wire_assign(av_snk1_if[i].data_i , av_snk1[i].data_i)
      snk1_ready_inst[i]  = simple_wire_assign(av_snk1[i].ready_o , av_snk1_if[i].ready_o)

      src_valid_inst[i]   = simple_wire_assign(av_src[i].valid_o , av_src_if[i].valid_o)
      src_data_inst[i]    = simple_wire_assign(av_src[i].data_o , av_src_if[i].data_o)
      src_ready_inst[i]   = simple_wire_assign(av_src_if[i].ready_i , av_src[i].ready_i)

  
    chain_inst=[None for i in range(pars.NB_CHAIN_ADDERS)]
    add_inst=[None for i in range(pars.NB_CHAIN_ADDERS)]
    for i in range(pars.NB_CHAIN_ADDERS):
      add_inst[i]   = StreamingSimpleAdder()
      chain_inst[i] = add_inst[i].block_connect(add_pars, reset, clk, av_snk0_if[i],  av_snk1_if[i], av_src_if[i])
   
    return instances() 
