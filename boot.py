
# This file is executed on every boot (including wake-boot from deepsleep)
import esp, uos, machine, gc
esp.osdebug(None)
gc.collect()


