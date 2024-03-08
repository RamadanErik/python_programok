import os
import sys
import time
import clr

sys.path.append(r"C:\Users\IDQ\PycharmProjects\K10CR1")

clr.AddReference("Thorlabs.MotionControl.DeviceManagerCLI")
clr.AddReference("Thorlabs.MotionControl.GenericMotorCLI")
clr.AddReference("Thorlabs.MotionControl.IntegratedStepperMotorsCLI")

from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import *
from System import Decimal


def forgato_csatlakozas(serial_n1,serial_n2):
    
    try:
        #print(GenericMotorCLI.ControlParameters.JogParametersBase.JogModes.SingleStep)
        # Create new device
        serial_no_1 = str(serial_n1)
        serial_no_2 = str(serial_n2)

        DeviceManagerCLI.BuildDeviceList()

        device_1 = CageRotator.CreateCageRotator(serial_no_1)
        device_2 = CageRotator.CreateCageRotator(serial_no_2)
        print(DeviceManagerCLI.GetDeviceList())
        # Connect, begin polling, and enable
        device_1.Connect(serial_no_1)
        device_2.Connect(serial_no_2)
        time.sleep(0.25)
        device_1.StartPolling(250)
        device_2.StartPolling(250)
        time.sleep(0.25)  # wait statements are important to allow settings to be sent to the device

        device_1.EnableDevice()
        device_2.EnableDevice()
        time.sleep(0.25)  # Wait for device to enable
        # Get Device information

        device_info = device_1.GetDeviceInfo()
        print(device_info.Description)
        device_info = device_2.GetDeviceInfo()
        print(device_info.Description)

        # Wait for Settings to Initialise
        if not device_1.IsSettingsInitialized():
            device_1.WaitForSettingsInitialized(10000)  # 10 second timeout
            assert device_1.IsSettingsInitialized() is True

        # Before homing or moving device, ensure the motor's configuration is loaded
        m_config = device_1.LoadMotorConfiguration(serial_no_1,
                                                DeviceConfiguration.DeviceSettingsUseOptionType.UseFileSettings)

        m_config.DeviceSettingsName = "K10CR1"

        m_config.UpdateCurrentConfiguration()

        device_1.SetSettings(device_1.MotorDeviceSettings, True, False)

                # Wait for Settings to Initialise
        if not device_2.IsSettingsInitialized():
            device_2.WaitForSettingsInitialized(10000)  # 10 second timeout
            assert device_2.IsSettingsInitialized() is True

        # Before homing or moving device, ensure the motor's configuration is loaded
        m_config = device_2.LoadMotorConfiguration(serial_no_2,
                                                DeviceConfiguration.DeviceSettingsUseOptionType.UseFileSettings)

        m_config.DeviceSettingsName = "K10CR1"

        m_config.UpdateCurrentConfiguration()

        device_2.SetSettings(device_2.MotorDeviceSettings, True, False)


        return [device_1,device_2]

    except Exception as e:
        print(e)

def move_forgato(device,fok):
    d = Decimal(fok)
    print(f'Moving to position {fok}')
    device.MoveTo(d, 60000)  # 10s timeout again
    time.sleep(1)
    return

def home_forgato(device):
    print("Home")
    device.Home(60000)  # 10s timeout, blocking call
    return

def forgato_disconnect(device_1,device_2):
    device_1.Disconnect()
    device_2.Disconnect()
    print("Devices disconnected")
    return