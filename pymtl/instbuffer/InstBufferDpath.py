#=========================================================================
# InstBufferDpath.py
#=========================================================================

from pymtl      import *

# BRGTC2 custom MemMsg modified for RISC-V 32

from ifcs import MemReqMsg, MemRespMsg
from ifcs import MemReqMsg4B, MemRespMsg4B

from pclib.rtl        import Mux, RegEnRst
from pclib.rtl.arith  import EqComparator

# No index anymore since it's fully associative!

class InstBufferDpath( Model ):

  def __init__( s, num_entries, line_nbytes ):

    opaque_nbits = 8
    line_nbits   = line_nbytes * 8
    line_bw      = clog2( line_nbytes )
    addr_nbits   = 32
    tag_nbits    = addr_nbits - line_bw
    data_nbits   = 32
    line_nwords  = line_nbits/data_nbits

    #---------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------

    s.buffreq_msg     = InPort ( MemReqMsg4B   )
    s.buffresp_msg    = OutPort( MemRespMsg4B  )
    s.memreq_msg      = OutPort( MemReqMsg( opaque_nbits, data_nbits, line_nbits )  )
    s.memresp_msg     = InPort ( MemRespMsg( opaque_nbits, line_nbits ) )

    # control signals (ctrl->dpath)

    s.buffreq_en      = InPort( 1 )
    s.memresp_en      = InPort( 1 )
    s.arrays_wen_mask = InPort( num_entries )
    s.way_sel         = InPort( 1 )
    s.way_sel_current = InPort( 1 )
    s.buffresp_hit    = InPort( 1 )

    # status signals (dpath->ctrl)

    s.tag_match_mask  = OutPort ( num_entries )

    # Register the unpacked buffreq_msg
    # No need to store data/type because I$ requests are READ-ONLY

    s.buffreq_addr_reg = m = RegEnRst( dtype = addr_nbits, reset_value = 0 )
    s.connect_pairs(
      m.en,  s.buffreq_en,
      m.in_, s.buffreq_msg.addr,
    )

    s.buffreq_opaque_reg = m = RegEnRst( dtype = opaque_nbits, reset_value = 0 )
    s.connect_pairs(
      m.en,  s.buffreq_en,
      m.in_, s.buffreq_msg.opaque,
      m.out, s.buffresp_msg.opaque,
    )

    # Register the unpacked data from memresp_msg

    s.memresp_data_reg = m = RegEnRst( dtype = line_nbits, reset_value = 0 )

    s.connect_pairs(
      m.en,  s.memresp_en,
      m.in_, s.memresp_msg.data,
    )

    # Tag array/data arrary
    # Note that for the fully associative InstBuffer we don't need a huge
    # array -- instead we just need 2/4 registers to hold the tags
    # Also, we don't need those xxx_bar and sram_xxx signals -- no SRAM!
    # Each entry in the tag/data array stores the tag/data of each line

    s.tag_array  = RegEnRst[num_entries]( dtype = tag_nbits, reset_value = 0 )
    s.data_array = RegEnRst[num_entries]( dtype = line_nbits, reset_value = 0 )

    for i in xrange(num_entries):
      s.connect_pairs(
        s.tag_array[i].en,   s.arrays_wen_mask[i],
        # Get the tag of current request
        s.tag_array[i].in_,  s.buffreq_addr_reg.out[line_bw:addr_nbits],

        s.data_array[i].en,  s.arrays_wen_mask[i], # only need to support full line write!
        s.data_array[i].in_, s.memresp_msg.data,
      )

    # Eq comparator to check for tag matching (tag_compare_0)

    s.tag_compare = EqComparator[num_entries]( nbits = tag_nbits )

    for i in xrange(num_entries):
      s.connect_pairs(
        s.tag_compare[i].in0, s.buffreq_addr_reg.out[line_bw:addr_nbits],
        s.tag_compare[i].in1, s.tag_array[i].out,
        s.tag_compare[i].out, s.tag_match_mask[i],
      )

    # Data read mux

    s.read_data = Wire( line_nbits )

    s.data_read_mux = m = Mux( dtype = line_nbits, nports = num_entries )

    for i in xrange( num_entries ):
      s.connect( m.in_[i],  s.data_array[i].out )

    s.connect_pairs(
      m.sel, s.way_sel_current,
      m.out, s.read_data,
    )

    # Select word for buff response (always 4B aligned)

    s.read_word_sel_mux = m = Mux( dtype = data_nbits, nports = line_nwords )

    for i in xrange( line_nwords ):
      s.connect( m.in_[i], s.read_data[i*addr_nbits:(i+1)*addr_nbits] )

    # Choose word to read from buffline based on what the offset was
    s.connect( m.sel, s.buffreq_addr_reg.out[2:line_bw] )

    # READ-ONLY for InstBuffer

    @s.combinational
    def comb_buffresp_msg_pack():
      s.buffresp_msg.type_.value = MemRespMsg.TYPE_READ
      s.buffresp_msg.test.value  = concat( Bits( 1, 0 ), s.buffresp_hit )
      s.buffresp_msg.len.value   = Bits( 2, 0 )
      s.buffresp_msg.data.value  = s.read_word_sel_mux.out

    @s.combinational
    def comb_memreq_msg_pack():
      s.memreq_msg.type_.value  = MemReqMsg.TYPE_READ
      s.memreq_msg.opaque.value = Bits ( opaque_nbits, 0 )
      # No need to select/register the tag from tag array since there is no eviction!
      s.memreq_msg.addr.value   = concat(s.buffreq_addr_reg.out[line_bw:addr_nbits], Bits(line_bw, 0))
      s.memreq_msg.len.value    = Bits ( 4, 0 )

