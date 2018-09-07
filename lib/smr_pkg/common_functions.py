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
  #print "in wire assign"
  @always_comb
  def simple_wire_assign_process():
    dout.next = din
    if __debug__:   # to create a reg keyword in verilog 
      pass
  return simple_wire_assign_process

def simple_reg_assign(reset,clk,dout,din):
  @always(clk.posedge, reset.posedge)
  def simple_reg_assign_process():
    if(reset==1):
      dout.next = 0
    else:
      dout.next = din
  return simple_reg_assign_process

def conditional_reg_assign(reset,clk,dout,din,condition):
  @always(clk.posedge, reset.posedge)
  def conditional_reg_assign_process():
    if(reset==1):
      dout.next = 0
    elif (condition == 1):
      dout.next = din
  return conditional_reg_assign_process
