# bittide_sim_wip

For argument reference:

`python3 System.py --help`

To view control graphs without a state machine attached:

`python3 System.py --conf arch.json`

Included are three example config files, one for each of the PI, Reframing, and FFP controllers with a three-node mesh topology.

To use the architecture creation tool:
`python3 GraphMaker.py`


You will need to install some python packages from pip, off the top of my head you'll probably want:
`pysimplegui`
`matplotlib`
`progress`

Removing the disable_app flag will block, attempting to connect to FSM applications

# Known issues:
~~The transmission links aren't being pre-filled, so use of a non-zero transmission delay with an integral term will always produce a error term which pulls the frequencies to zero~~ FIXED (hopefully)