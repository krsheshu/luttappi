# TCL File Generated by Component Editor 16.0
# Tue May 15 16:56:32 CEST 2018
# DO NOT MODIFY


# 
# streaming_ip_a "streaming_ip_a" v1.0
#  2018.05.15.16:56:32
# Streaming IP A created from myhdl
# 

# 
# request TCL package from ACDS 16.0
# 
package require -exact qsys 16.0


# 
# module streaming_ip_a
# 
set_module_property DESCRIPTION "Streaming IP A created from myhdl"
set_module_property NAME streaming_ip_a
set_module_property VERSION 1.0
set_module_property INTERNAL false
set_module_property OPAQUE_ADDRESS_MAP true
set_module_property AUTHOR ""
set_module_property DISPLAY_NAME streaming_ip_a
set_module_property INSTANTIATE_IN_SYSTEM_MODULE true
set_module_property EDITABLE true
set_module_property REPORT_TO_TALKBACK false
set_module_property ALLOW_GREYBOX_GENERATION false
set_module_property REPORT_HIERARCHY false


# 
# file sets
# 
add_fileset QUARTUS_SYNTH QUARTUS_SYNTH "" ""
set_fileset_property QUARTUS_SYNTH TOP_LEVEL streaming_ip_a_top
set_fileset_property QUARTUS_SYNTH ENABLE_RELATIVE_INCLUDE_PATHS false
set_fileset_property QUARTUS_SYNTH ENABLE_FILE_OVERWRITE_MODE false
add_fileset_file streaming_ip_a_top.v VERILOG PATH converted_hdl/streaming_ip_a_top.v

add_fileset SIM_VERILOG SIM_VERILOG "" ""
set_fileset_property SIM_VERILOG TOP_LEVEL streaming_ip_a_top
set_fileset_property SIM_VERILOG ENABLE_RELATIVE_INCLUDE_PATHS false
set_fileset_property SIM_VERILOG ENABLE_FILE_OVERWRITE_MODE true
add_fileset_file streaming_ip_a_top.v VERILOG PATH converted_hdl/streaming_ip_a_top.v


# 
# parameters
# 


# 
# display items
# 


# 
# connection point reset
# 
add_interface reset reset end
set_interface_property reset associatedClock clock
set_interface_property reset synchronousEdges DEASSERT
set_interface_property reset ENABLED true
set_interface_property reset EXPORT_OF ""
set_interface_property reset PORT_NAME_MAP ""
set_interface_property reset CMSIS_SVD_VARIABLES ""
set_interface_property reset SVD_ADDRESS_GROUP ""

add_interface_port reset reset reset Input 1


# 
# connection point clock
# 
add_interface clock clock end
set_interface_property clock clockRate 0
set_interface_property clock ENABLED true
set_interface_property clock EXPORT_OF ""
set_interface_property clock PORT_NAME_MAP ""
set_interface_property clock CMSIS_SVD_VARIABLES ""
set_interface_property clock SVD_ADDRESS_GROUP ""

add_interface_port clock clk clk Input 1


# 
# connection point src
# 
add_interface src avalon_streaming start
set_interface_property src associatedClock clock
set_interface_property src associatedReset reset
set_interface_property src dataBitsPerSymbol 8
set_interface_property src errorDescriptor ""
set_interface_property src firstSymbolInHighOrderBits true
set_interface_property src maxChannel 0
set_interface_property src readyLatency 0
set_interface_property src ENABLED true
set_interface_property src EXPORT_OF ""
set_interface_property src PORT_NAME_MAP ""
set_interface_property src CMSIS_SVD_VARIABLES ""
set_interface_property src SVD_ADDRESS_GROUP ""

add_interface_port src av_src_channel_o channel Output 4
add_interface_port src av_src_data_o data Output 64
add_interface_port src av_src_empty_o empty Output 3
add_interface_port src av_src_error_o error Output 3
add_interface_port src av_src_startofpacket_o startofpacket Output 1
add_interface_port src av_src_endofpacket_o endofpacket Output 1
add_interface_port src av_src_ready_i ready Input 1
add_interface_port src av_src_valid_o valid Output 1


# 
# connection point snk
# 
add_interface snk avalon_streaming end
set_interface_property snk associatedClock clock
set_interface_property snk associatedReset reset
set_interface_property snk dataBitsPerSymbol 8
set_interface_property snk errorDescriptor ""
set_interface_property snk firstSymbolInHighOrderBits true
set_interface_property snk maxChannel 0
set_interface_property snk readyLatency 0
set_interface_property snk ENABLED true
set_interface_property snk EXPORT_OF ""
set_interface_property snk PORT_NAME_MAP ""
set_interface_property snk CMSIS_SVD_VARIABLES ""
set_interface_property snk SVD_ADDRESS_GROUP ""

add_interface_port snk av_snk_channel_i channel Input 4
add_interface_port snk av_snk_data_i data Input 64
add_interface_port snk av_snk_empty_i empty Input 3
add_interface_port snk av_snk_endofpacket_i endofpacket Input 1
add_interface_port snk av_snk_error_i error Input 3
add_interface_port snk av_snk_startofpacket_i startofpacket Input 1
add_interface_port snk av_snk_ready_o ready Output 1
add_interface_port snk av_snk_valid_i valid Input 1
