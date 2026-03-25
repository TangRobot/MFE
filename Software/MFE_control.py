"""
This file is part of the official implementation for the paper:
"MFE: A Multimodal Hand Exoskeleton With Interactive Force, Pressure and Thermo-Haptic Feedback".
DOI: 10.1109/LRA.2026.3662616

This script provides basic functionalities for communicating with Hand Exoskeleton,
including state reading and control command execution, and serves as a reference
implementation for the force feedback control in the MFE system.

The code is intended as a minimal and adaptable example. Users should modify and
extend it according to their specific hardware setup and experimental requirements.

Please adapt this code to your own device by following the TODO comments in the file.
In particular, make sure to configure parameters such as:
- Serial port name
- Baud rate
- Servo IDs
- Control mode and limits
- Dex hand control logic

Refer to the official Dynamixel SDK documentation for detailed usage instructions.

If you use this code in your research, please cite the corresponding paper.

This project is released under the MIT License.
"""

import os
import numpy as np
from pymodbus import FramerType
from pymodbus.client import ModbusSerialClient
from dynamixel_sdk import *

# ------------------- Configuration Section -------------------

ADDR_TORQUE_ENABLE          = 64
ADDR_GOAL_POSITION          = 116
ADDR_PRESENT_POSITION       = 132
ADDR_DRIVE_MODE             = 11
ADDR_GOAL_CURRENT           = 102
TORQUE_ENABLE               = 1
TORQUE_DISABLE              = 0
DRIVE_MODE_CURRENT          = 0

# TODO: Configure these parameters according to your Dynamixel servo setup.
DXL_ID = [1, 2, 3, 4, 5] #From thumb to little finger.
DEVICENAME = 'COM1'
BAUDRATE = 115200
PROTOCOL_VERSION = 2.0
# TODO: Configure these parameters according to your Inspire hand setup,
# or implement your own hand control logic if you are using a different dex hand.
HAND_PORT = 'COM2'
HAND_BAUDRATE = 115200

# ------------------- Utility Functions -------------------

def getch():
    if os.name == 'nt':
        import msvcrt
        return msvcrt.getch().decode()
    else:
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def check(dxl_comm_result, dxl_error, packetHandler):
    if dxl_comm_result != COMM_SUCCESS:
        print(packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print(packetHandler.getRxPacketError(dxl_error))

# ------------------- Inspire Hand Control -------------------
# TODO: Implement your own hand control logic if you are using a different dex hand.
def create_modbus_client():
    client = ModbusSerialClient(
        framer=FramerType.RTU,
        port=HAND_PORT,
        baudrate=HAND_BAUDRATE,
        timeout=1,
        stopbits=1,
        bytesize=8,
        parity='N'
    )
    if not client.connect():
        raise RuntimeError('Unable to connect to Modbus RTU server.')
    return client

def write_single_register(client, hand_id, reg_addr, regval_int16):
    result = client.write_register(reg_addr, regval_int16, device_id=hand_id)
    return result.isError(), result

def write_multiple_registers(client, hand_id, reg_addr, values):
    result = client.write_registers(reg_addr, values, device_id=hand_id)
    return result.isError(), result

def read_register(client, hand_id, reg_addr, num_int16_regs=6, dtype=np.int16):
    result = client.read_holding_registers(reg_addr, count=num_int16_regs, device_id=hand_id)
    if result.isError():
        return []
    registers = result.registers
    results = []
    for val in registers:
        if dtype in (np.int16, np.uint16):
            results.append(np.array(val))
        elif dtype in (np.int8, np.uint8):
            results.append(np.array(val & 0xff))
            results.append(np.array((val >> 8) & 0xff))
        else:
            results.append(np.array(val))
    return np.array(results).astype(dtype)

class InspireHand:
    def __init__(self, client, hand_id):
        self.client = client
        self.hand_id = hand_id
    def set_pos(self, pos, index=None):
        if index is not None:
            if not 0 <= index <= 5:
                return False, 'Index out of range'
            reg_addr = 0x05C2 + index * 2
            return write_single_register(self.client, self.hand_id, reg_addr, pos)
        if len(pos) != 6:
            return False, None
        reg_addr = 0x05C2
        return write_multiple_registers(self.client, self.hand_id, reg_addr, pos)
    def set_force(self, force, index=None):
        if index is not None:
            if not 0 <= index <= 5:
                return False, 'Index out of range'
            reg_addr = 0x05DA + index * 2
            return write_single_register(self.client, self.hand_id, reg_addr, force)
        if len(force) != 6:
            return False, None
        reg_addr = 0x05DA
        return write_multiple_registers(self.client, self.hand_id, reg_addr, force)
    def read_force(self):
        reg_addr = 0x062E
        return read_register(self.client, self.hand_id, reg_addr, num_int16_regs=6)

# ------------------- Dynamixel Servo Control -------------------

def setup_dynamixel():
    portHandler = PortHandler(DEVICENAME)
    packetHandler = PacketHandler(PROTOCOL_VERSION)
    if not portHandler.openPort():
        raise RuntimeError('Failed to open the port')
    if not portHandler.setBaudRate(BAUDRATE):
        raise RuntimeError('Failed to set baudrate')
    return portHandler, packetHandler

# ------------------- Main Control Logic -------------------

def main():
    # Initialize hardware
    # TODO: Implement your own initialization logic if you are using a different dex hand.
    client = create_modbus_client()
    hand = InspireHand(client, hand_id=0x01)
    portHandler, packetHandler = setup_dynamixel()
    initial_position = [0] * 5
    longest_position = [0] * 5
    finger_position = [0] * 5
    goal_current = [0] * 5
    # Disable torque for all servos
    for i in DXL_ID:
        dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, i, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
        check(dxl_comm_result, dxl_error, packetHandler)
    # Set initial positions based on user input
    print('Bend your thumb and press any key to set initial position.')
    getch()
    i = DXL_ID[0]
    longest_position[0], dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, i, ADDR_PRESENT_POSITION)
    check(dxl_comm_result, dxl_error, packetHandler)
    print('Extend your thumb straight and press any key to set initial position.')
    getch()
    initial_position[0], dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, i, ADDR_PRESENT_POSITION)
    check(dxl_comm_result, dxl_error, packetHandler)
    for cmd, val in [(ADDR_TORQUE_ENABLE, TORQUE_DISABLE), (ADDR_DRIVE_MODE, DRIVE_MODE_CURRENT), (ADDR_TORQUE_ENABLE, TORQUE_ENABLE)]:
        dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, i, cmd, val)
        check(dxl_comm_result, dxl_error, packetHandler)
    print('Make a fist and press any key to set initial position.')
    getch()
    for idx, i in enumerate(DXL_ID[1:], 1):
        longest_position[idx], dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, i, ADDR_PRESENT_POSITION)
        check(dxl_comm_result, dxl_error, packetHandler)
    print('Flat your hand and press any key to set initial position.')
    getch()
    for idx, i in enumerate(DXL_ID[1:], 1):
        initial_position[idx], dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, i, ADDR_PRESENT_POSITION)
        check(dxl_comm_result, dxl_error, packetHandler)
        for cmd, val in [(ADDR_TORQUE_ENABLE, TORQUE_DISABLE), (ADDR_DRIVE_MODE, DRIVE_MODE_CURRENT), (ADDR_TORQUE_ENABLE, TORQUE_ENABLE)]:
            dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, i, cmd, val)
            check(dxl_comm_result, dxl_error, packetHandler)
        dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, i, ADDR_GOAL_CURRENT, 0)
        check(dxl_comm_result, dxl_error, packetHandler)
    # Main control loop
    print('Press any key to continue! (or press ESC to quit!)')
    if getch() == chr(0x1b):
        return
    while True:
        # Read force from Inspire hand
        # TODO: Implement your own read force logic if you are using a different dex hand.
        present_force = hand.read_force()
        for idx, i in enumerate(DXL_ID):
            # Read present positions from Dynamixel servos and compute control commands
            present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, i, ADDR_PRESENT_POSITION)
            if present_position - initial_position[idx] >= 0:
                finger_position[idx] = int((present_position - initial_position[idx]) * 2000 // abs(longest_position[idx] - initial_position[idx]))
            else:
                finger_position[idx] = 0
            finger_position[idx] = min(finger_position[idx], 2000)
            # Compute goal current based on the force feedback from the Inspire hand
            force = present_force[4 - idx]
            goal_current[idx] = 0 if force <= 150 else max(-int(force / 6), -1749)
            # Send force feedback commands to Dynamixel servos
            dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, i, ADDR_GOAL_CURRENT, goal_current[idx])
        # Send position commands to the Inspire hand
        # TODO: Implement your own position control logic if you are using a different dex hand.
        finger_position[0] = min(finger_position[0], 1200)
        hand.set_pos([finger_position[4], finger_position[3], finger_position[2], finger_position[1], finger_position[0], 1750])
        hand.set_force([1000] * 6)

if __name__ == '__main__':
    main()
