""" Simple example notify
(c) 2016 EKM Metering.
"""
from ekmmeters import *

#port and meter
my_port_name = "/dev/ttyO4"
my_meter_address = "000300001463"
#logging to console
ekm_set_log(ekm_print_log)

#open port and init
port = SerialPort(my_port_name)
if (port.initPort() == True):
    my_meter = V4Meter(my_meter_address)
    my_meter.attachPort(port)
else:
    # no port no meter
    print("Cannot open port")
    exit()


class ANotifyObserver(MeterObserver):

    def __init__(self):

        super(ANotifyObserver, self).__init__()
        self.m_startup = True
        self.m_last_pulse_cnt = 0

    def update(self, def_buf):

        pulse_cnt = def_buf[Field.Pulse_Cnt_1][MeterData.NativeValue]
        #print str(pulse_cnt)
        # notification watch
        if self.m_startup:
            self.m_last_pulse_cnt = pulse_cnt
            self.m_startup = False
        else:
            if self.m_last_pulse_cnt < pulse_cnt:
                self.doNotify()
                self.m_last_pulse_cnt = pulse_cnt

    def doNotify(self):
        print("Bells!  Alarms!  Do that again!")

ekm_set_log(ekm_no_log)
my_observer = ANotifyObserver()
my_meter.registerObserver(my_observer)


my_meter.setLCDCmd([LCDItems.Pulse_Cnt_1])
my_meter.setPulseInputRatio(Pulse.In1, 1)

poll_reads = 120
print("Starting " + str(poll_reads) + " read poll.")
read_cnt = 0
fail_cnt = 0
while(read_cnt < poll_reads):
    read_cnt += 1
    if not my_meter.request():
        fail_cnt += 1
        if fail_cnt > 3:
            print(">3 consecutive fails. Please check connection and restart")
            exit()
    else:
        fail_cnt = 0

port.closePort()
