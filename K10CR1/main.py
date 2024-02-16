# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import os
import sys
import time
import clr

#sys.path.append("C:\\Users\\KNL2022\\Documents\\Entangled souurce\\scpi_idq900\\python_programok\\K10CR1")

# clr.AddReference("Thorlabs.MotionControl.DeviceManagerCLI")
# clr.AddReference("Thorlabs.MotionControl.GenericMotorCLI")
# clr.AddReference("Thorlabs.MotionControl.IntegratedStepperMotorsCLI")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.IntegratedStepperMotorsCLI.dll")
#clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.KCube.DCServoCLI.dll")
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import *
from System import Decimal


def main():
    """The main entry point for the application"""

    # Uncomment this line if you are using
    SimulationManager.Instance.InitializeSimulations()

    try:
        #print(GenericMotorCLI.ControlParameters.JogParametersBase.JogModes.SingleStep)
        # Create new device
        #serial_no_1 = str("55290814")
        serial_no_2 = str("55290504")

        DeviceManagerCLI.BuildDeviceList()

        #device_1 = CageRotator.CreateCageRotator(serial_no_1)
        device_2 = CageRotator.CreateCageRotator(serial_no_2)
        print(DeviceManagerCLI.GetDeviceList())
        # Connect, begin polling, and enable
        #device_1.Connect(serial_no_1)
        device_2.Connect(serial_no_2)
        time.sleep(0.25)
        #device_1.StartPolling(250)
        device_2.StartPolling(250)
        time.sleep(0.25)  # wait statements are important to allow settings to be sent to the device

        #device_1.EnableDevice()
        device_2.EnableDevice()
        time.sleep(0.25)  # Wait for device to enable

        # Get Device information

        #device_info = device_1.GetDeviceInfo()
        #print(device_info.Description)
        device_info = device_2.GetDeviceInfo()
        print(device_info.Description)

        device = device_2
        serial_no = serial_no_2

        # Wait for Settings to Initialise
        if not device.IsSettingsInitialized():
            device.WaitForSettingsInitialized(10000)  # 10 second timeout
            assert device.IsSettingsInitialized() is True

        # Before homing or moving device, ensure the motor's configuration is loaded
        m_config = device.LoadMotorConfiguration(serial_no,
                                                DeviceConfiguration.DeviceSettingsUseOptionType.UseFileSettings)

        m_config.DeviceSettingsName = "K10CR1"

        m_config.UpdateCurrentConfiguration()

        device.SetSettings(device.MotorDeviceSettings, True, False)

        print("Homing Actuator")
        device.Home(60000)  # 10s timeout, blocking call

        f = 181.0
        d = Decimal(f)
        print(f'Device Homed. Moving to position {f}')
        device.MoveTo(d, 60000)  # 10s timeout again
        time.sleep(1)

        print(f'Device now at position {device.Position}')
        time.sleep(1)

        device.Disconnect()
    except Exception as e:
        print(e)

    SimulationManager.Instance.UninitializeSimulations()
    return None


if __name__ == "__main__":
    main()
