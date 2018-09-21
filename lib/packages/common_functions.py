from myhdl import always_comb,always, Signal

class Reset():
  LOW=0 
  HIGH=1 

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


def conditional_wire_assign(dout, condition, din1, din2):
  @always_comb
  def conditional_wire_assign_process():
    dout.next = din1 if (condition == 1) else din2
    if __debug__:   # to create a reg keyword in verilog 
      pass
  return conditional_wire_assign_process

def conditional_wire_assign_lt(dout, op1, op2, din1, din2):
  """ Conditional wire assign where dout = din1 when op1<op2 else din2"""
  @always_comb
  def conditional_wire_assign_lt_process():
    dout.next = din1 if (op1 < op2) else din2
    if __debug__:   # to create a reg keyword in verilog 
      pass
  return conditional_wire_assign_lt_process

def simple_reg_assign(reset, clk, dout, reset_val, din):
  @always(clk.posedge, reset.posedge)
  def simple_reg_assign_process():
    if(reset==1):
      dout.next = reset_val
    else:
      dout.next = din
  return simple_reg_assign_process


def conditional_reg_assign(reset, clk, dout, reset_val, condition, din):
  @always(clk.posedge, reset.posedge)
  def conditional_reg_assign_process():
    if(reset==1):
      dout.next = reset_val
    elif (condition == 1):
      dout.next = din
      print(din) 
  return conditional_reg_assign_process

def conditional_clocked_append(reset, clk, out, condition, inp):
  @always(clk.posedge, reset.posedge)
  def conditional_clocked_append_process():
    if (condition == 1):
      print(inp)
      print(out)
      out.append(inp)
      print(out)
  return conditional_clocked_append_process

def conditional_reg_counter(reset, clk, counter, reset_val, condition):
  @always(clk.posedge, reset.posedge)
  def conditional_reg_counter_process():
    if(reset==1):
      counter.next = reset_val
    elif (condition == 1):
      counter.next = counter + 1
  return conditional_reg_counter_process

def conditional_clocked_appendfile(reset, clk, condition, inp, filename):
  @always(clk.posedge, reset.posedge)
  def conditional_clocked_appendfile_process():
    if (condition == 1):
      #print inp
      fp=open(filename,"a")
      fp.write("{:d}\n".format(int(inp)))
      fp.close()
  return conditional_clocked_appendfile_process
