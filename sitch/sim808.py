import io
import serial


class FonaReader(object):
    """ Initialization causes the module to go into engineering mode, which will
    cause it to return cell network information.
    It has an iterator (generator) built in that cranks out dicts.

    """
    def __init__(self, ser_port):
        self.initstring = "AT+CENG=2,1\r\n"
        print "opening serial port: %s" % ser_port
        self.serconn = serial.Serial(ser_port, 9600, timeout=1)
        # self.sio = io.TextIOWrapper(io.BufferedRWPair(self.serconn,
        #                                              self.serconn))
        # self.sio.write(self.initstring)
        # self.sio.flush()
        self.serconn.write(self.initstring)
        self.serconn.sendBreak()
        self.trigger_gps()

    def __iter__(self):
        while True:
            line = None
            line = self.serconn.readline()
            if line is not None:
                print line
                processed_line = self.process_line(line)
                yield processed_line

    def trigger_gps(self):
        self.serconn.write("AT+CIPGSMLOC=1,1\r\n")
        self.serconn.sendBreak()
        return None

    def set_band(self, band):
        if band in ["EGSM_MODE", "PGSM_MODE", "DCS_MODE", "GSM850_MODE",
                    "PCS_MODE", "EGSM_DCS_MODE", "GSM850_PCS_MODE",
                    "EGSM_PCS_MODE", "ALL_BAND"]:
            term_command = "AT+CBAND=\"%s\"" % band
            self.serconn.write(term_command)
        else:
            print "Not setting band, unrecognized value: %s" % band

    @classmethod
    def process_line(cls, line):
        processed = None
        if line.startswith('+CENG: '):
            dataz = line.split(' ')[1].replace('"', '')
            line_parts = dataz.split(',')
            if len(line_parts) == 12:
                processed = FonaReader.process_12(line_parts)
            if len(line_parts) == 7:
                processed = FonaReader.process_7(line_parts)
            if len(line_parts) == 8:
                processed = FonaReader.process_8(line_parts)
        elif line.startswith('+CIPGSMLOC:'):
            dataz = line.split(' ')[1]
            line_parts = dataz.split(',')
            if line_parts[0] == 0:
                processed = FonaReader.process_gps(line_parts)
        else:
            print "Unprocessable line from SIM808!"
            print line
        return processed

    @classmethod
    def process_12(cls, parts):
        retval = {"cell": parts[0],
                  "arfcn": parts[1],
                  "rxl": parts[2],
                  "rxq": parts[3],
                  "mcc": parts[4],
                  "mnc": parts[5],
                  "bsic": parts[6],
                  "cellid": parts[7],
                  "rla": parts[8],
                  "txp": parts[9],
                  "lac": parts[10],
                  "ta": parts[11]
                  }
        return retval

    @classmethod
    def process_8(cls, parts):
        retval = {"cell": parts[0],
                  "arfcn": parts[1],
                  "rxl": parts[2],
                  "bsic": parts[3],
                  "cellid": parts[4],
                  "mcc": parts[5],
                  "mnc": parts[6],
                  "lac": parts[7]
                  }
        return retval

    @classmethod
    def process_7(cls, parts):
        retval = {"cell": parts[0],
                  "arfcn": parts[1],
                  "rxl": parts[2],
                  "bsic": parts[3],
                  "mcc": parts[4],
                  "mnc": parts[5],
                  "lac": parts[6]
                  }
        return retval

    @classmethod
    def process_gps(cls, parts):
        retval = {"status": parts[0],
                  "lon": parts[1],
                  "lat": parts[2],
                  "date": parts[3],
                  "time": parts[4]
                  }
        return retval
