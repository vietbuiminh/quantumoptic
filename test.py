"""
kpz101_pythonnet
==================

An example of using the .NET API with the pythonnet package for controlling a KPZ101
"""
import os
import time
import sys
import clr
import instruments as ik
import pandas as pd

clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.KCube.PiezoCLI.dll")
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.KCube.PiezoCLI import *
from System import Decimal  # necessary for real world units

STEP = 0.2 # voltage step for the piezo controller
DELAY_S = 2 # in seconds
INITIAL_VOLT = 40
TARGET_VOLT = 50.00

KPZ_SERIAL_NO = "29501769"
CC_PORT = 'COM3'
BAUD_RATE = 19200
TIMEOUT = 1

df = pd.DataFrame(columns=['Voltage', 'CH1', 'CH2', 'CC'])

def main():
    """The main entry point for the application"""

    # Uncomment this line if you are using
    # SimulationManager.Instance.InitializeSimulations()

    try:
        # Connection with the Qubitekk CC
        #-------------------------------
        cc1 = ik.qubitekk.CC1.open_serial(CC_PORT, BAUD_RATE)
        firmware_version = cc1.firmware
        print(f"Firmware of CC1: {firmware_version}")
        cc1.dwell_time = 0.1
        cc1.gate = False
        cc1.subtract = False
        cc1.trigger_mode = "continuous"
        # cc1.window(8)
        time.sleep(60)
        # print(f"Channel 1 count: {cc1.channel[0].count}")
        

        # Connection with the Piezo Motor
        #------------------------------
        DeviceManagerCLI.BuildDeviceList()      

        # create new device
        serial_no = KPZ_SERIAL_NO  # Replace this line with your device's serial number

        # Connect, begin polling, and enable
        device = KCubePiezo.CreateKCubePiezo(serial_no)

        device.Connect(serial_no)

        # Get Device Information and display description
        device_info = device.GetDeviceInfo()
        # print(device_info.Description)

        # Start polling and enable
        device.StartPolling(250)  #250ms polling rate
        # time.sleep(25)
        device.EnableDevice()
        time.sleep(0.25)  # Wait for device to enable

        if not device.IsSettingsInitialized():
            device.WaitForSettingsInitialized(10000)  # 10 second timeout
            assert device.IsSettingsInitialized() is True

        # Load the device configuration
        device_config = device.GetPiezoConfiguration(serial_no)

        # This shows how to obtain the device settings
        device_settings = device.PiezoDeviceSettings

        # Set the Zero point of the device
        # print("Setting Zero Point")
        device.SetZero()

        # Get the maximum voltage output of the KPZ
        max_voltage = device.GetMaxOutputVoltage()  # This is stored as a .NET decimal
        # print(max_voltage)
        # Go to a voltage
        dev_voltage = Decimal(INITIAL_VOLT)
        # print(f'Going to voltage {dev_voltage}')

        if dev_voltage != Decimal(0) and dev_voltage <= max_voltage:                
            device.SetOutputVoltage(dev_voltage)
            time.sleep(DELAY_S)

            # print(f'Moved to Voltage {device.GetOutputVoltage()}')
        else:
            pass
            # print(f'Voltage must be between 0 and {max_voltage}')
        # print(f"Loop about to start")
        # loop function to run until reaching desire voltage
        target_voltage = Decimal(TARGET_VOLT)
        print(f'Going to target voltage {target_voltage}')
        while dev_voltage <= max_voltage and dev_voltage < target_voltage:
            device.SetOutputVoltage(dev_voltage + Decimal(STEP))
            time.sleep(DELAY_S)
            dev_voltage = device.GetOutputVoltage()
            cc1.clear_counts()
            time.sleep(2)
            ch1 = cc1.channel[0].count
            ch2 = cc1.channel[1].count
            cc = cc1.channel[2].count

            print(f"Channel 1 count: {ch1}")
            print(f"Channel 2 count: {ch2}")
            print(f"Channel CC count: {cc}")
            print(f'Moved to Voltage {dev_voltage}')
            # df2 = pd.DataFrame({"Voltage": dev_voltage, "CH1": ch1, 'CH2': ch2, 'CC': cc})
            # df.append(df2)
            cc1.clear_counts()


        # Stop Polling and Disconnect
        device.StopPolling()
        device.Disconnect()
        cc1.close()
        display(df)
    except Exception as e:
        print(e)

    # Uncomment this line if you are using Simulations
    # SimulationManager.Instance.UninitializeSimulations()
    ...


if __name__ == "__main__":
    main()