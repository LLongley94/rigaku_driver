
import os
import time
from datetime import datetime
import math as mth


class RigakuCommands:
    RESPONSE_CODES = {

        0: "An error occured during execution",
        1: "Command executed correctly",
        2: "CAP has stopped - no new commands can be passed",
        3: "CAP listen mode was closed",
        4: "Timeout, no response from CAP"
    }

    TAKE_IMAGE = {
        "name": "xx iss"
    }

    CONNECT_XTALCHECK = {
        "name": "xx xtalcheck connect"

    }

    INITIALIZE_XTALCHECK ={
        "name": "xx xtalcheck initialize"
    }

    DISCONECT_XTALCHECK = {
        "name": "xx xtalcheck disconnect"
    }

    ABSOLUTE_MOVE_XTALCHECK = {
        "name": "xx xtalcheck move"
    }

    RELATIVE_MOVE_XTALCHECK = {
        "name": "xx xtalcheck mover"
    }

    SHORT_OMEGA_SCAN = {
        "name": "dc simplescreen"
    }

    OMEGA_SCAN = {
        "name": "dc simplescan"
    }

    GONIOMETER = {
        "name": "gt a"
    }


class RigakuSimController:
    
    def __init__(self) -> None:
        self.watch_file = "tmp"
        self.control_comands = ""
        self.logger = "logger.txt"
        #self.path = os.getcwd() + "\\" + self.watch_file + "\\"
        self.path = "C:\\Xcalibur\\tmp\\listen_mode\\"
        print(self.path)
        self._last_command = ""

        self.cmd = RigakuCommands()


        self._init_logger()
    
    def _init_logger(self):

        if os.path.isfile(self.logger):
            print(f"log file {self.logger} exists")

        else: 
            with open(self.logger, 'a') as l:
                l.writelines("RigakuSimController logger started")

    def _write_file(self, control_command):
        with open(self.path + "command.in", "w+") as f:
            f.writelines(control_command +" \r\n")
        self._last_command = control_command

    def _file_saver(self, file):
        with open(self.path + file, 'r') as r:
            contents = r.readline()
            print(contents)

    def _write_logger(self, command):
        with open(self.logger, 'a') as l: 
            log_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            log_entry = "\n" + log_time + " command" ":\t" + command
            l.writelines(log_entry)

    def _read_directory(self, timeout):
        wait = 0
        _busy_flag = False
        while True:
            dir_list = os.listdir(self.path)
            for file in dir_list:
                
                if ".busy" in file:
                    print(f"Command {self._last_command} is still executing, wait time {wait} s")
                    _busy_flag = True
                    
                if ".error" in file:
                    print(f"An error in {self._last_command} occured")
                    self._file_saver(file)
                    return 0
                    
                if ".done" in file:
                    print(f"Command {self._last_command} executed")
                    self._file_saver(file)
                    return 1

                if ".stop" in file:
                    print(f"Command {self._last_command} has been stopped")
                    self._file_saver(file)
                    return 2

                if ".closed" in file:
                    print(f"CAP listen mode was closed")
                    self._file_saver(file)
                    return 3
            
            if not _busy_flag:
                print(f"no looked for files found - waiting {wait}")
            
            wait +=1
            if wait > timeout:
                break
            time.sleep(1)


        print("timeout")
        return 4

    def _cleanup(self):
        
        dir_list = os.listdir(self.path)
        print(f"cleaning {self.path} directory")

        for file in dir_list:
            print(f"Removing {file}")
            os.remove(self.path + file)
        
        

    def _send_and_recieve(self, message, timeout = 60):

        print(f"Writing {message} to command.in file")
        self._write_file(message)

        print(f"Watching {self.path}")
        
        response =self._read_directory(timeout)

        print(f"Response was {self.cmd.RESPONSE_CODES[response]}")

        print(f"Writing log file")

        to_log = message + " response: " + self.cmd.RESPONSE_CODES[response]

        self._write_logger(to_log)

        print(f"Cleaning {self.watch_file}")

        self._cleanup()

        print("Cleaned")


    def test(self, dummy= "test.in"):

        self._send_and_recieve(dummy)



    def take_image(self, image_folder, base_image_name, exposure_time = 1, number_images = 1):

        command_root = self.cmd.TAKE_IMAGE["name"]

        timeout = exposure_time + 60 
        
        image_path = os.getcwd() + "\\" + image_folder + "\\"

        command = f"{command_root} {exposure_time} {number_images} {image_path}{base_image_name}"
        self._send_and_recieve(command, timeout)


    def connect(self):
        self._send_and_recieve(self.cmd.CONNECT_XTALCHECK["name"])

    def initialize(self):
        self._send_and_recieve(self.cmd.INITIALIZE_XTALCHECK["name"])

    def disconnect(self):
        self._send_and_recieve(self.cmd.DISCONECT_XTALCHECK["name"])

    def relative_move(self, value_x_mm = 0, value_y_mm = 0, value_z_mm = 0):
        
            command_root = self.cmd.RELATIVE_MOVE_XTALCHECK["name"]

            command = f"{command_root} x y z {value_x_mm} {value_y_mm} {value_z_mm}"

            self._send_and_recieve(command)

    def absolute_move(self, value_x_mm = None, value_y_mm = None, value_z_mm = None):

        axes = [ str(axis) for axis, value in zip(['x', 'y', 'z'], [value_x_mm, value_y_mm, value_z_mm]) if value is not None ]

        values = [ str(value) for value in [value_x_mm, value_y_mm, value_z_mm] if value is not None ]

        command_root = self.cmd.ABSOLUTE_MOVE_XTALCHECK["name"]

        command = f"{command_root} {' '.join(axes)} {' '.join(values)}"

        self._send_and_recieve(command)

    def short_omega_scan(self, scan_folder, base_scan_name, exposure_time = 5, scan_width = 0.5, scan_range = 5):

        command_root = self.cmd.SHORT_OMEGA_SCAN["name"]

        timeout = mth.ceil(exposure_time*(scan_range/scan_width)) + 60 #timeout is at least 60 seconds longer than the scan takes 

        scan_path = os.getcwd() + "\\" + scan_folder + "\\"

        command = f"{command_root} {scan_path} {base_scan_name} [{exposure_time} [{scan_width}] [{scan_range}]]]"
        self._send_and_recieve(command,timeout)

    def omega_scan(self, scan_folder, base_scan_name, exposure_time = 5, scan_width = 0.5, scan_range = 90):
        command_root = self.cmd.OMEGA_SCAN["name"]

        timeout = mth.ceil(exposure_time*(scan_range/scan_width)) + 60 #timeout is at least 60 seconds longer than the scan takes 

        scan_path = os.getcwd() + "\\" + scan_folder + "\\"

        command = f"{command_root} {scan_path} {base_scan_name} {exposure_time} {scan_width} {scan_range}"
        self._send_and_recieve(command,timeout)

    def goniometer_absolute(self, omega=3., theta=3., kappa=-90., phi=0., distance=60.):
        command_root = self.cmd.GONIOMETER["name"]

        command = f"{command_root} {omega} {theta} {kappa} {phi} {distance}"
        
        self._send_and_recieve(command)

    def complete_strategy(self, scan_folder, base_scan_name, exposure_time = 5, scan_width = 0.5):
        strategy = [
        {"theta": -20, "omega0": -21.75, "omega1": -13.25}, 
        {"theta": -5, "omega0": -11.75, "omega1": 1.75}, 
        {"theta": 9, "omega0": 2.25, "omega1": 15.75}, 
        {"theta": 23, "omega0": 16.25, "omega1": 29.75}, 
        {"theta": 37, "omega0": 30.25, "omega1": 43.75}, 
        {"theta": 51, "omega0": 44.25, "omega1": 52.0}
        ]

        run_count = 1

        for run in strategy:
            self.goniometer_absolute(run["omega0"], run["theta"])
            self.omega_scan(scan_folder + "_" + str(run_count), base_scan_name + "_" + str(run_count), exposure_time, scan_width, run["omega1"] - run["omega0"])




    