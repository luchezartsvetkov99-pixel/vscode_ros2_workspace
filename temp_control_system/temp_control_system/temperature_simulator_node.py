import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Temperature
from std_msgs.msg import Bool  # Нов тип съобщение за статус на вентилатора
import random

class TemperatureSimulator(Node):
    def __init__(self):
        super().__init__('temperature_simulator')
        self.publisher_ = self.create_publisher(Temperature, '/sensor/temperature', 10)
        
        # Абонираме се за командата от контролера
        self.subscription = self.create_subscription(
            Bool,
            '/sensor/cooling_actuator',
            self.cooling_callback,
            10)
            
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.base_temperature = 30.0
        self.cooling_on = False  # Флаг за състоянието на вентилатора
        self.get_logger().info('Обновеният температурен симулатор е ОНЛАЙН!')

    def cooling_callback(self, msg):
        self.cooling_on = msg.data

    def timer_callback(self):
        msg = Temperature()
        
        # Динамична физика на симулацията
        if self.cooling_on:
            # Ако вентилаторът работи, температурата пада бързо
            self.base_temperature -= 1.5
            status_text = "ОХЛАЖДАНЕ"
        else:
            # Ако не работи, машината се нагрява бавно
            self.base_temperature += 0.8
            status_text = "НАГРЯВАНЕ"
            
        # Добавяме малко случаен шум
        noise = random.uniform(-0.3, 0.3)
        current_temp = self.base_temperature + noise
        
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'temp_sensor_link'
        msg.temperature = current_temp
        msg.variance = 0.05
        
        self.publisher_.publish(msg)
        self.get_logger().info(f'[{status_text}] Температура: {current_temp:.2f}°C')

def main(args=None):
    rclpy.init(args=args)
    node = TemperatureSimulator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
