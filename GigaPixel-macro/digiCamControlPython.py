import os
import subprocess
import time
import psutil


# Simple python class to use digiCamControl via the single command system to control your camera.
# Digicamcontrol (https://digicamcontrol.com/) needs to be installed.
# For documentation please visit https://github.com/Eagleshot/digiCamControlPython

class Camera:
    """
    Python interface for the open source digicam-control software. Initialize the program by specifying where
    digiCamControl is installed. If left empty, the default location (C:/Program Files (x86)/digiCamControl) will be
    assumed. If openProgram is set to true, digiCamControl will automatically be opened in the background.
    """

    def __init__(self, exe_dir: str = r'C:\Program Files (x86)\digiCamControl'):

        self.capture_command = "Capture"  # Default capture command

        # Check if file path exists
        if os.path.exists(exe_dir + r"/CameraControlRemoteCmd.exe"):
            self.exe_dir = exe_dir

            # Open program if closed
            if not "CameraControl.exe" in (i.name() for i in psutil.process_iter()):
                subprocess.Popen(self.exe_dir + r"/CameraControl.exe")
                time.sleep(10)

        else:
            print("Error: digiCamControl not found.")

    # %% Capture
    def capture(self, location: str = "") -> int | str:
        """
        Takes a photo - filename and location can be specified in string location, otherwise the default will be used.
        :param location: Location and filename of the image to be saved.
        :return: An integer indicating the success of the operation
        """
        r = self.run_cmd(self.capture_command + " " + location)
        if r == 0:
            print("Captured image.")
            return self.__get_cmd("lastcaptured")
        else:
            return r


    # %% Folder
    def set_folder(self, folder: str):
        """
        Set the folder where the pictures are saved.
        :param folder: Folder where the pictures are saved.
        :return: Value indicating the success of the operation (0 = success, -1 = error)
        """
        self.__set_cmd("session.folder", folder)

    def set_image_name(self, name: str):
        """
        Set the name of the images.
        :param name: Prefix of the image name.
        :return:
        """
        self.__set_cmd("session.name", name)

    def set_counter(self, counter: int = 0):
        """
        Set the counter to a specific number (default = 0).
        :param counter: Integer number to set the counter to. default = 0
        :return: Value indicating the success of the operation (0 = success, -1 = error)
        """
        self.__set_cmd("session.Counter", str(counter))

    # %% Transfer mode
    def set_transfer(self, location: str) -> int:
        """
        Define where the pictures should be saved - "Save_to_camera_only", "Save_to_PC_only" or
        "Save:to_PC_and_camera" :param location: Value to set the transfer mode to. Possible values:
        "Save_to_camera_only", "Save_to_PC_only" or "Save:to_PC_and_camera"
        :return: Code indicating the success of the operation
        """
        print(f"The pictures will be saved to: {location}.")
        return self.run_cmd(f"set transfer {location}")

    # %% Autofocus
    def show_live_view(self) -> int:
        """
        Show the live view window.
        :return: Code indicating the success of the operation
        """
        print("Showing live view window.")
        return self.run_cmd("do LiveViewWnd_Show")

    def set_autofocus(self, status: bool = True):
        """
        Turn the autofocus on (default) or off.
        :param status: Boolean value to turn the autofocus on or off. Default = True
        :return:
        """
        if status:
            self.capture_command = "Capture"
            print("Autofocus is on.")
        else:
            self.capture_command = "CaptureNoAf"
            print("Autofocus is off.")

    # %% Shutterspeed
    def set_shutterspeed(self, shutter_speed: str) -> int:
        """
        Set the shutter speed
        :param shutter_speed: Set the shutter speed - e.g. "1/50", "1/250" or 1s.
        :return: Value indicating the success of the operation
        """
        return self.__set_cmd("shutterspeed", shutter_speed)

    def get_shutterspeed(self):
        """
        Get the current shutter speed
        :return: Value indicating the success of the operation
        """
        return self.__get_cmd("shutterspeed")

    def list_shutterspeed(self):
        """
        Get a list off all possible shutter speeds
        :return: Value indicating the success of the operation
        """
        return self.__list_cmd("shutterspeed")

    # %% ISO
    def set_iso(self, iso: int = 100) -> int:
        """
        Set the current ISO value
        :param iso: Current ISO value - e.g. 100, 200 or 400.
        :return: Value indicating the success of the operation
        """
        return self.__set_cmd("Iso", str(iso))

    def get_iso(self):
        """
        Get the current ISO Value.
        :return: Value indicating the success of the operation
        """
        return self.__get_cmd("Iso")

    def list_iso(self) -> list:
        """
        Get a list off all possible ISO values - e.g. 100, 200 or 400.
        :return: Value indicating the success of the operation
        """
        return self.__list_cmd("Iso")

    # %% Aperture
    def set_aperture(self, aperture: float = 2.8) -> int:
        """
        Set the aperture
        :param aperture: Set the cam aperture - e.g. 2.8 or 8.0.
        :return: Value indicating the success of the operation
        """
        return self.__set_cmd("aperture", str(aperture))

    def get_aperture(self) -> int | str:
        """
        Get the current aperture - e.g. 2.8 or 8.0.
        :return: Value indicating the success of the operation
        """
        return self.__get_cmd("aperture")

    def list_aperture(self) -> list:
        """
        Get a list off all possible aperture values - e.g. 2.8 or 8.0.
        :return: Value indicating the success of the operation
        """
        return self.__list_cmd("aperture")

    # %% Exposure Compensation
    def set_exposure_comp(self, ec: str = "0.0") -> int:
        """
        Set the exposure compensation - e.g. "-1.0" or "+2.3"
        :param ec: Current exposure compensation - e.g. "-1.0" or "+2.3"
        :return: Value indicating the success of the operation
        """
        return self.__set_cmd("exposurecompensation", ec)

    def get_exposure_comp(self) -> int | str:
        """
        Get the current exposure compensation - e.g. "-1.0" or "+2.3"
        :return: Value indicating the success of the operation
        """
        return self.__get_cmd("exposurecompensation")

    def list_exposure_comp(self) -> list:
        """
        Get a list off all possible exposure compensation values - e.g. "-1.0" or "+2.3"
        :return: List of all possible exposure compensation values - e.g. "-1.0" or "+2.3"
        """
        return self.__list_cmd("exposurecompensation")

    # %% Compression
    def set_compression(self, comp: str = "RAW") -> int:
        """
        Set the compression - e.g. "RAW" or "JPEG (BASIC)"
        :param comp: Current compression. default = "RAW"
        :return: Value indicating the success of the operation
        """
        return self.__set_cmd("compressionsetting", comp)

    def get_compression(self) -> int | str:
        """
        Get the current compression - e.g. "RAW" or "JPEG (BASIC)"
        :return: Value indicating the success of the operation
        """
        return self.__get_cmd("compressionsetting")

    def list_compression(self) -> list:
        """
        Get a list off all possible compression setting - e.g. "RAW" or "JPEG (BASIC)"
        :return: Value indicating the success of the operation
        """
        return self.__list_cmd("compressionsetting")

    # %% Whitebalance
    def set_whitebalance(self, wb: str) -> int:
        """
        Set the white balance - e.g. "Auto" or "Daylight" or "Cloudy"
        :param wb: Set the white balance - e.g. "Auto" or "Daylight" or "Cloudy"
        :return: Value indicating the success of the operation
        """
        return self.__set_cmd("whitebalance", wb)

    def get_whitebalance(self) -> int | str:
        """
        Get the current white balance - e.g. "Auto" or "Daylight" or "Cloudy"
        :return: Value indicating the success of the operation
        """
        return self.__get_cmd("whitebalance")

    def list_whitebalance(self) -> list:
        """
        Get a list off all possible white balance values - e.g. "Auto" or "Daylight" or "Cloudy"
        :return: Value indicating the success of the operation
        """
        return self.__list_cmd("whitebalance")

    # %% Video
    def start_video(self) -> int:
        """
        Start recording a video.
        :return: Value indicating the success of the operation
        """
        self.show_live_view() # May be necessary
        return self.run_cmd("do StartRecord")

    def stop_video(self) -> int:
        """
        Stop recording a video.
        :return: Value indicating the success of the operation
        """
        return self.run_cmd("do StopRecord")

    # %% Commands
    def run_cmd(self, cmd: str) -> int:
        """
        Run a generic command directly with CameraControlRemoteCmd.exe
        :param cmd: Command to run on digiCamControl
        :return: Value indicating the success of the operation
        """
        r = subprocess.check_output(
            f"cd {self.exe_dir} && CameraControlRemoteCmd.exe /c {cmd}", shell=True).decode()

        if 'null' in r:  # Success
            return 0

        if r'""' in r:  # Success
            return 0

        print(f"Error: {r}")  # Format output message
        return -1

    def __set_cmd(self, cmd: str, value: str) -> int:
        """
        Run a set command with CameraControlRemoteCmd.exe
        :param cmd: Command to run on digiCamControl
        :param value: Value to set the command to
        :return: Value indicating the success of the operation
        """
        r = subprocess.check_output(f"cd {self.exe_dir} && CameraControlRemoteCmd.exe /c set {cmd} {value}",
                                    shell=True).decode()
        if 'null' in r:  # Success
            print(f"Set the {cmd} to {value}.")
            return 0

        return_value = r[109:]
        print(f"Error: {return_value}")
        return -1

    def __get_cmd(self, cmd: str) -> int | str:
        """
        Run a get command with CameraControlRemoteCmd.exe
        :param cmd: Command to run on digiCamControl
        :return: Value indicating the success of the operation
        """
        r = subprocess.check_output(
            f"cd {self.exe_dir} && CameraControlRemoteCmd.exe /c get {cmd}", shell=True).decode()

        if 'Unknown parameter' in r:  # Error
            return_value = r[109:]
            print(f"Error: {return_value}")  # Format output message
            return -1

        return_value = r[96:-6]
        print(f"Current {cmd}: {return_value}")  # Format output message
        return return_value

    def __list_cmd(self, cmd: str) -> int | list[str]:
        """
        Run a list command with CameraControlRemoteCmd.exe
        :param cmd: Command to run on digiCamControl
        :return: Value indicating the success of the operation
        """
        r = subprocess.check_output(f"cd {self.exe_dir} && CameraControlRemoteCmd.exe /c list {cmd}",
                                    shell=True).decode()
        if 'Unknown parameter' in r:  # Error
            return_value = r[109:]
            print(f"Error: {return_value}")  # Format output message
            return -1

        # Format response and turn into a list
        return_list = r[96:-6].split(",")
        return_list = [e[1:-1] for e in return_list]  # Remove "" from string

        # Format output message
        print(f"List of all possible {cmd}s: {return_list}")
        return return_list


# %% Unittests
if __name__ == '__main__':
    # TODO: Coverage for whole document

    print("Beginning unit tests:")

    camera = Camera()
    assert isinstance(camera, Camera)

    assert (isinstance(camera.list_shutterspeed(), list))
    temp = camera.list_shutterspeed()[0]
    assert camera.set_shutterspeed(temp) == 0
    assert camera.get_shutterspeed() == temp

    assert (isinstance(camera.list_iso(), list))
    temp = camera.list_iso()[0]
    assert camera.set_iso(temp) == 0
    assert camera.get_iso() == temp

    assert (isinstance(camera.list_aperture(), list))
    temp = camera.list_aperture()[0]
    assert camera.set_aperture(temp) == 0
    assert camera.get_aperture() == temp

    assert isinstance(camera.list_exposure_comp(), list)
    temp = camera.list_exposure_comp()[0]
    assert camera.set_exposure_comp(temp) == 0
    assert camera.get_exposure_comp() == temp

    assert (isinstance(camera.list_compression(), list))
    temp = camera.list_compression()[0]
    assert camera.set_compression(temp) == 0
    assert camera.get_compression() == temp

    assert (isinstance(camera.list_whitebalance(), list))
    temp = camera.list_whitebalance()[0]
    assert camera.set_whitebalance(temp) == 0
    assert camera.get_whitebalance() == temp

    print("End unit tests.")
