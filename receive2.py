import serial
import time
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
CHECK_ATTEMPTS = 2

RESET_COMMAND = b"Communication check\r\n"
ANS_COMM_OK = 'Confirm Communication check'
START_COMM = b"start\r\n"
STOP_COMM = b'stop\r\n'
#'/dev/ttyAMA0'
class Data_request:
    def __init__(self, port='/dev/ttyAMA0'):
        self.CHECK_ATTEMPTS = 2
        self.RESET_COMMAND = b"Communication check\r\n"
        self.ANS_COMM_OK = 'Confirm Communication check'
        self.START_COMM = b"start\r\n"
        self.STOP_COMM = b'stop\r\n'
        logger.debug("init")
        self.ser = serial.Serial(port, 115200, timeout=1)
        self.ser.close()
        
        
    def check_comm(self):
        try:
            check=0
            while True:
                if check == self.CHECK_ATTEMPTS:
                    return False
                else:
                    pass
                logger.info("check arduino comm")
                self.ser.open()
                self.ser.write(self.RESET_COMMAND)
                while True:
                    try:
                        logger.info("read arduino ans")
                        line = self.ser.readline().decode('utf-8').rstrip()
                        break
                    except UnicodeDecodeError:
                        pass
                if line == self.ANS_COMM_OK:
                    logger.info("arduino comm OK, ans: {}".format(line))
                    self.ser.flush()
                    self.ser.flushInput()
                    self.ser.flushOutput()
                    return True
                else:
                    logger.error("arduino comm NOT OK, ans: {}".format(line))
                    self.ser.read_all()
                    self.ser.flush()
                    self.ser.close()
                    time.sleep(1)
                logger.debug('...')
                check +=1
                
        except Exception as e:
            logger.error(e)
            return False
            
    def get_data(self, duration, path):
        logger.info("request arduino to start")
        self.ser.write(START_COMM)
        file = open(path + "tempdata.txt","w")
        try:
            logger.info ('the measurement time is set to:' + str(duration))
            now = time.time()
        
            while (time.time()- now < duration ):
                line = self.ser.readline().decode('utf-8', errors='ignore')
                logger.debug("data received: {}".format(line))
                if line:
                    if ";" not in line:
                        #return "Invalid data"
                        logger.error ("invalid data")
                        return False
                    else:
                        file.write(line)
                else:
                    logger.info("arduino stops sending data")
                    #return "Comm error"
                    return False
                
                time.sleep(0.0001)
            self.stop_data_acquisition()
            file.close()
        except KeyboardInterrupt as e:
            logger.error("request arduino to stop by keyboard interrupt")
            #return "keyboard interrupt"
            return False
        except Exception as e:
            logger.error("Error: {}".format(e))
            #return "keyboard interrupt"
            return False
        return True
    def stop_data_acquisition(self):
        logger.debug("send stop to arduino")
        self.ser.write(STOP_COMM)
        self.ser.close()
    
# def data_request(duration, path):
#     try:
#         print("init")
#         ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)
#         ser.close()
#         check = 0
#         while True:
#             
#             if check == CHECK_ATTEMPTS:
#                 #return "arduino not found"
#                 return False
#             else:
#                 pass
#             
#             print("check arduino comm")
#             ser.open()
#             ser.write(RESET_COMMAND)
#             while True:
#                 try:
#                     print("read arduino ans")
#                     line = ser.readline().decode('utf-8').rstrip()
#                     break
#                 except UnicodeDecodeError:
#                     pass
#             if line == ANS_COMM_OK:
#                 print("arduino comm OK, ans: {}".format(line))
#                 ser.flush()
#                 ser.flushInput()
#                 ser.flushOutput()
#                 #print(line+'...')
#                 break
#             else:
#                 print("arduino comm NOT OK, ans: {}".format(line))
#                 ser.read_all()
#                 ser.flush()
#                 ser.close()
#                 time.sleep(1)
#             print('...')
#             check +=1
#             
#         print(line + ": done")
#         print("request arduino to start")
#         ser.write(START_COMM)
#         
#     except (FileNotFoundError, serial.SerialException) as e:
#         print("Error {}".format(e))
#         #return e
#         return False
# 
#     file = open(path + "tempdata.txt","w")
#     try:
#         #print('Set the measurement time (minutes): ')
#         #duration = int(input(''))
#         
#         print ('the measurement time is set to:' + str(duration))
#         now = time.time()
#         
#         while (time.time()- now < duration ):
#             line = ser.readline().decode('utf-8', errors='ignore')
#             print("data received: {}".format(line))
#             if line:
#                 if ";" not in line:
#                     #return "Invalid data"
#                     print ("invalid data")
#                     return False
#                 else:
#                     file.write(line)
#             else:
#                 print("arduino stops sending data")
#                 #return "Comm error"
#                 return False
#                 
#             time.sleep(0.0001)
#     except KeyboardInterrupt as e:
#         print("request arduino to stop by keyboard interrupt")
#         #return "keyboard interrupt"
#         return False
#     
#     finally:
#         print("finally")
#         file.close()
#         print("send stop to arduino")
#         ser.write(STOP_COMM)
#         ser.close()
#         
#     #return "OK"
#     return True


if __name__ == '__main__':
    
    path = "/home/pi/Documents/SoundAnalyze/Results/"
    duration =10
#     data_request(duration, path)

    request_data = Data_request(port='/dev/ttyAMA0')
    if request_data.check_comm():
        request_data.get_data(duration, path)
    
    