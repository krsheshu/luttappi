from myhdl import always_comb,always

#ceil of the log base 2
def CLogB2(x):
  if x < 2:
    return 1
  return 1 + CLogB2(x/2)

# convert vector into array(list)
def vector_to_array(data_width, index, input_vector, output_array):

  @always_comb
  def vector_to_array_process():
    output_array.next = input_vector[data_width*(index+1): data_width*(index)]

  return vector_to_array_process

def simple_wire_assign(dout,din):
  @always_comb
  def simple_wire_assign_process():
    dout.next = din
    if __debug__:   # to create a reg keyword in verilog 
      pass
  return simple_wire_assign_process


def conditional_wire_assign(dout, condition, inp1, inp2):
  @always_comb
  def conditional_wire_assign_process():
    dout.next = inp1 if (condition == 1) else inp2
    if __debug__:   # to create a reg keyword in verilog 
      pass
  return conditional_wire_assign_process


def simple_reg_assign(reset, clk, dout, reset_val, din):
  @always(clk.posedge, reset.posedge)
  def simple_reg_assign_process():
    if(reset==1):
      dout.next = reset_val
    else:
      dout.next = din 
  return simple_reg_assign_process


def conditional_reg_assign(reset, clk, dout, reset_val, inp1, condition):
  @always(clk.posedge, reset.posedge)
  def conditional_reg_assign_process():
    if(reset==1):
      dout.next = reset_val
    elif (condition == 1):
      dout.next = inp1
  return conditional_reg_assign_process

def conditional_clocked_append(reset, clk, out, inp1, condition):
  @always(clk.posedge, reset.posedge)
  def conditional_clocked_append_process():
    if (condition == 1):
      out.append(inp1)
  return conditional_clocked_append_process
