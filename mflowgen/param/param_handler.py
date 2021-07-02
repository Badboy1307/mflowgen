#=========================================================================
# param_handler.py
#=========================================================================
# Handler for param-related commands
#
# Author : Christopher Torng
# Date   : July 2, 2021
#

import os
import re
import shutil
import subprocess
import sys
import yaml

from datetime       import datetime

from mflowgen.utils import bold, yellow
from mflowgen.utils import read_yaml, write_yaml

#-------------------------------------------------------------------------
# Parameter updates on the command line
#-------------------------------------------------------------------------
# Parameters can be set in the following ways:
#
#     - statically    -- in a node's configure.yml
#     - dynamically   -- at graph construction time in a construct.py
#     - interactively -- via the command line as supported here
#
# On the command line, we want a simple interface to update any node in
# the graph (or to update all nodes). It looks like this:
#
#     % mflowgen param update --step 5 --key clock_period --value 2.0
#     % mflowgen param update  -s 5     -k   clock_period  -v     2.0
#
# Updating all nodes can use the --all flag like this:
#
#     % mflowgen param update --all    --key clock_period --value 2.0
#
# Internally, parameters for the currently elaborated mflowgen graph
# (i.e., after executing mflowgen run) are stored in the hidden metadata
# directory '.mflowgen'. Specifically, this is in the configure.yml and
# mflowgen-run script for each node. To change a parameter on the command
# line, we need to modify these files.
#

class ParamHandler:

  def __init__( s ):

    # Valid commands

    s.commands = [
      'update',
      'help',
    ]

  #-----------------------------------------------------------------------
  # launch
  #-----------------------------------------------------------------------
  # Dispatch function for commands
  #

  def launch( s, args, help_, key, value, step, all_ ):

    if help_ and not args:
      s.launch_help()
      return

    try:
      command = args[0]
      assert command in s.commands # valid commands only
    except Exception as e:
      print( 'param: Unrecognized commands (see "mflowgen param help")' )
      sys.exit( 1 )

    try:
      assert len( args ) <= 1 # no further positional args are allowed
    except Exception as e:
      print()
      print( 'param: Unrecognized positional args' )
      # Allow this exception to pass, but force set the "help" flag so
      # users can see what they should be doing instead.
      help_ = True

    if   command == 'update' : s.launch_update( help_, key, value, step, all_ )
    else                     : s.launch_help()

  #-----------------------------------------------------------------------
  # launch_update
  #-----------------------------------------------------------------------
  # Internally, this command does the following:
  #
  # - Updates the configure.yml for the step given by --step
  # - Sets "parameters[key] = value"
  # - If --all is given, we update all nodes in the graph
  #

  def launch_update( s, help_, key, value, step, all_ ):

    # Help message

    def print_help():
      print()
      print( bold( 'Usage:' ), 'mflowgen param update',
                                  '--key/-k <key>',
                                  '--value/-v <value>',
                                  '[--step/-s <int>]',
                                  '[--all]'                              )
      print()
      print( bold( 'Example:' ), 'mflowgen param update',
                                  '--key clock_period --value 2.0',
                                  '--all'                                )
      print()
      print( 'Updates the parameter for the given step in the build'     )
      print( 'graph. The parameter key-value pair is only updated if'    )
      print( 'the key is defined and exists. The --all option applies'   )
      print( 'the update to all nodes in the currently elaborated graph.')
      print()

    if help_ or not key or not value or not (step or all_):
      print_help()
      return

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Implement here
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    # End of implementation
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    print(
      'Updated parameter "{key}" = "{value}" for step "{step}"'.format(
      key   = key,
      value = value,
      step  = step,
    ) )

  #-----------------------------------------------------------------------
  # launch_help
  #-----------------------------------------------------------------------

  def launch_help( s ):
    print()
    print( bold( 'Param Commands' ) )
    print()
    print( bold( ' - update :' ), 'Interactive update parameters'        )
    print()
    print( 'Run any command with -h to see more details'                 )
    print()


