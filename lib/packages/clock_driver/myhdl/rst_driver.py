from myhdl import always_comb, block

@block
def rst_driver(elapsed_time,reset_duration, reset_high, reset_low):

  @always_comb
  def reset_high_function():
    if elapsed_time < reset_duration:
      reset_high.next = 1
    else:
      reset_high.next = 0

  @always_comb
  def reset_low_function():
    if elapsed_time < reset_duration:
      reset_low.next = 0
    else:
      reset_low.next = 1

  return reset_high_function, reset_low_function

