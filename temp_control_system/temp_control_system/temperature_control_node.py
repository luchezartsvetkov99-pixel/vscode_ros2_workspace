import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Temperature
from std_msgs.msg import Bool  # Пакети за управление на актуатора

class TemperatureControl(Node):
    def __init__(self):
        super().__init__('temperature_control')
        self.subscription = self.create_subscription(
            Temperature,
            '/sensor/temperature',
            self.listener_callback,
            10)
            
        # Публикатор, който контролира вентилатора в симулатора
        self.actuator_publisher = self.create_publisher(Bool, '/sensor/cooling_actuator', 10)
        
        # Дефиниране на граници (Хистерезис)
        self.UPPER_THRESHOLD = 17.0  # Кога се включва
        self.LOWER_THRESHOLD = 5.0  # Кога се изключва
        self.is_cooling_active = False
        
        self.get_logger().info('Контролерът с автоматичен термостат следи системата...')

    def listener_callback(self, msg):
        current_temp = msg.temperature
        actuator_msg = Bool()

        # Логика на двупозиционен регулатор (On-Off Controller)
        if current_temp > self.UPPER_THRESHOLD and not self.is_cooling_active:
            self.is_cooling_active = True
            self.get_logger().warn(f'ПОКАЧВАНЕ: {current_temp:.2f}°C > {self.UPPER_THRESHOLD}°C. Включвам вентилатора!')
            
        elif current_temp < self.LOWER_THRESHOLD and self.is_cooling_active:
            self.is_cooling_active = False
            self.get_logger().info(f'ОХЛАДЕНО: {current_temp:.2f}°C < {self.LOWER_THRESHOLD}°C. Изключвам вентилатора.')

        # Изпращаме текущата команда към симулатора
        actuator_msg.data = self.is_cooling_active
        self.actuator_publisher.publish(actuator_msg)

def main(args=None):
    rclpy.init(args=args)
    node = TemperatureControl()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
