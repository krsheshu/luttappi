from myhdl import Signal, delay, instance, always, always_comb, block

@block
def clk_driver(elapsed_time,clk, period=20):

  cycle_count=Signal(0)
  lowTime = int(period/2)
  highTime = period - lowTime

  @instance
  def driveClk():
    while True:
      yield delay(lowTime)
      clk.next = 1
      yield delay(highTime)
      clk.next = 0

  @always(clk.negedge)
  def num_clocks():
    cycle_count.next = cycle_count+1

  @always_comb
  def find_elapsed_time():
    elapsed_time.next=period*(cycle_count)

  return driveClk, num_clocks, find_elapsed_time
