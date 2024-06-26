
import logging
import threading
import time


class DistanceWriter:
    def __init__(self, autopilot: "AutoPilot", period):
        self.autopilot = autopilot
        self.period = period

        self.alive = True
        self.writer_thread = threading.Thread(target=self.writer_worker)
        self.writer_thread.daemon = True
        self.writer_thread.start()

    def writer_worker(self):
        distance = 255
        while self.alive:
            logging.debug(f"Distance Writer is writing {distance}")
            self.autopilot.write((distance).to_bytes(1, byteorder="big"))
            distance -= 3
            if distance <= 0:
                logging.info("Distance Writer has finished")
                self.alive = False
                return
            time.sleep(self.period)

    def stop(self):
        logging.debug(
            f"Distance Writer will stop in {self.serial.timeout} seconds")
        self.alive = False

    def join(self):
        logging.debug(f"Distance Writer thread will be joined")
        self.writer_thread.join(0.1)



def int2bytes(value: int | bytes):
    """
    Ensures the given value is bytes and of the right length
    """
    if type(value) == int:
        return value.to_bytes(2, byteorder="little")
    elif len(value) != 2:
        raise Exception("Bytes object is of wrong length!")
    return value

def bytes2int(value: int | bytes):
    """
    Ensures the given value is int
    """
    if type(value) == int:
        # Though it should be less than 256*256-1
        return value
    elif len(value) == 2:
        return int.from_bytes(value, byteorder="little")
    else:
        raise Exception("Bytes object is of wrong length!")