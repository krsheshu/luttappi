from myhdl import always, always_comb, Signal, instances, block

@block
def streaming_ip_a_2xinp(reset, clk, av_snk0, av_snk1, av_src, data_enable_o):

  src_valid = Signal(bool(0))
  snk_ready = Signal(bool(0))

  @always_comb
  def output_gen_wires():
    av_src.valid_o.next = src_valid
    av_snk0.ready_o.next = snk_ready
    av_snk1.ready_o.next = snk_ready

  #Registering valid
  @always(clk.posedge, reset.posedge)
  def src_valid_reg_process():
    if reset==1:
      src_valid.next = 0
    elif av_snk0.valid_i == 1 and av_snk1.valid_i== 1 and av_src.ready_i == 1:
      src_valid.next = 1
    elif (av_snk0.valid_i == 0 or av_snk1.valid_i == 0) and av_src.ready_i == 1 and src_valid == 1:
      src_valid.next = 0
    elif av_snk0.valid_i == 1 and av_snk1.valid_i== 1 and av_src.ready_i == 0 and src_valid == 0:
      src_valid.next = 1

  @always_comb
  def snk_ready_process():
    if (src_valid == 1 and av_src.ready_i == 0):
      snk_ready.next = 0
    elif ( av_snk0.valid_i == 1 and av_snk1.valid_i== 1):
      snk_ready.next = 1
    else:
      snk_ready.next = 0

  #Dataenable as output
  @always_comb
  def data_enable_process():
    if reset==1:
      data_enable_o.next = 0
    elif snk_ready == 1 and av_snk0.valid_i == 1 and av_snk1.valid_i == 1:
      data_enable_o.next = 1
    else:
      data_enable_o.next = 0

  return instances()

