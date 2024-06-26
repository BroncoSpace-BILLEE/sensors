import rclpy
from rclpy.node import Node
import math

from std_msgs.msg import Float64

import time
import board
import adafruit_bno055

class ImuPublisher(Node):

    def __init__(self):
        super().__init__('imu_publisher')
        self.publisher = self.create_publisher(Float64, '/movement/Imu', 1)

        i2c = board.I2C()
        self.sensor = adafruit_bno055.BNO055_I2C(i2c)
        
        timer_period = 1/100

        path = '/home/billee/billee_ws/src/sensors/resource/imu_calibration.dat'

        with open(path, 'r') as file:
            magnetometer = file.readline().strip().split(',')
            self.magnetometer = (int(magnetometer[0]), int(magnetometer[1]), int(magnetometer[2]))

            gyro = file.readline().strip().split(',')
            self.gyro = (int(gyro[0]), int(gyro[1]), int(gyro[2]))

            acceleration = file.readline().strip().split(',')
            self.acceleration = (int(acceleration[0]), int(acceleration[1]), int(acceleration[2]))

        
        self.sensor.offsets_accelerometer = self.acceleration
        self.sensor.offsets_magnetometer = self.magnetometer
        self.sensor.offsets_gyroscope = self.gyro


        self.timer = self.create_timer(timer_period, self.timer_callback)

    def _write_register_data(self, register, data):
        write_buffer = bytearray(1)
        write_buffer[0] = register & 0xFF
        write_buffer[1:len(data)+1]=data
        with self.sensor.i2c_device as i2c:
            i2c.write(write_buffer, start=0, end=len(write_buffer))

    def _read_registers(self, register, length):
        read_buffer = bytearray(23)
        read_buffer[0] = register & 0xFF
        with self.sensor.i2c_device as i2c:
            i2c.write(read_buffer, start=0, end=1)
            i2c.readinto(read_buffer, start=0, end=length)
            return read_buffer[0:length]

    def timer_callback(self):
        OFFSET = 1.0

        msg = Float64()
        yaw = (-self.sensor.euler[0] + OFFSET + 360) % 360
        #yaw = self.sensor.quaternion
        print(yaw)
        yaw = yaw * (math.pi / 180)
        msg.data = yaw 
        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    imu_publisher = ImuPublisher()
    try:
        rclpy.spin(imu_publisher)
    except KeyboardInterrupt:
        imu_publisher.destroy_node()

if __name__ == '__main__':
    main()
