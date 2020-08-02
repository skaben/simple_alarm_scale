Alarm level scale for SKABEN, based on Micropython

Topics for subscribe: SCALE, SCALE/\<macaddress\>

Topic for publish initial request: SCALEASK

jSON input message format: {"state":"blue", "level":10, "borders":[50,100,150]}

state - is a color state of dungeon, for state blue and lightblue current 
level marks will blink in change with blue or cyan. In future, in black state 
all scale will blink red-black on full brightness

level - current level of alarm

borders - borders of color states depends of level. 
0 - borders[0] - green state,
borders[0] - borders[1] - yellow state
borders[1] - borders[2] - red state, black state activated only manually

