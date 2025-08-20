#!/usr/bin/env python3
"""
Coffee PID Controller - Main Application
Contains intentional bugs for demonstration purposes
"""

import time
import threading
import json
import sqlite3
from typing import Dict, List, Optional

class CoffeePIDController:
    def __init__(self, target_temp: float = 95.0):
        self.target_temperature = target_temp
        self.current_temperature = 20.0
        self.is_running = False
        self.temperature_history = []
        self.control_thread = None
        
        # PID parameters
        self.kp = 2.0
        self.ki = 0.1
        self.kd = 0.05
        
        # PID state
        self.prev_error = 0.0
        self.integral = 0.0
        
        # Database connection
        self.db_conn = None
        self.setup_database()
    
    def setup_database(self):
        """Setup SQLite database for logging"""
        try:
            self.db_conn = sqlite3.connect('coffee_pid.db')
            cursor = self.db_conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS temperature_logs (
                    id INTEGER PRIMARY KEY,
                    timestamp REAL,
                    temperature REAL,
                    target REAL,
                    error REAL
                )
            ''')
            self.db_conn.commit()
        except Exception as e:
            print(f"Database setup failed: {e}")
    
    def calculate_pid_output(self, error: float, dt: float) -> float:
        """
        Calculate PID control output
        FIXED: Added integral windup prevention with bounds checking
        """
        # Add error to integral term
        self.integral += error * dt
        
        # Prevent integral windup by limiting the integral term
        max_integral = 100.0  # Maximum integral value to prevent windup
        if abs(self.integral) > max_integral:
            self.integral = max_integral if self.integral > 0 else -max_integral
        
        derivative = (error - self.prev_error) / dt
        
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.prev_error = error
        
        return output
    
    def simulate_temperature_change(self, control_output: float, dt: float):
        """
        Simulate temperature change based on control output
        FIXED: Added temperature bounds checking for realistic values
        """
        # Simple thermal model
        heat_transfer = control_output * dt
        self.current_temperature += heat_transfer
        
        # Natural cooling
        cooling_rate = 0.1  # degrees per second
        self.current_temperature -= cooling_rate * dt
        
        # Apply temperature bounds (realistic for coffee brewing)
        min_temp = 0.0  # Absolute minimum temperature
        max_temp = 120.0  # Maximum safe temperature (above boiling)
        self.current_temperature = max(min_temp, min(max_temp, self.current_temperature))
    
    def log_temperature(self, timestamp: float, error: float):
        """Log temperature data to database"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute('''
                INSERT INTO temperature_logs (timestamp, temperature, target, error)
                VALUES (?, ?, ?, ?)
            ''', (timestamp, self.current_temperature, self.target_temperature, error))
            self.db_conn.commit()
        except Exception as e:
            print(f"Logging failed: {e}")
    
    def control_loop(self):
        """Main control loop"""
        last_time = time.time()
        
        while self.is_running:
            current_time = time.time()
            dt = current_time - last_time
            
            if dt < 0.1:  # Minimum control interval
                time.sleep(0.01)
                continue
            
            error = self.target_temperature - self.current_temperature
            control_output = self.calculate_pid_output(error, dt)
            
            self.simulate_temperature_change(control_output, dt)
            self.temperature_history.append(self.current_temperature)
            
            # Keep only last 1000 readings to prevent memory issues
            if len(self.temperature_history) > 1000:
                self.temperature_history = self.temperature_history[-1000:]
            
            self.log_temperature(current_time, error)
            last_time = current_time
    
    def start(self):
        """Start the PID controller"""
        if not self.is_running:
            self.is_running = True
            self.control_thread = threading.Thread(target=self.control_loop)
            self.control_thread.start()
    
    def stop(self):
        """Stop the PID controller"""
        self.is_running = False
        if self.control_thread:
            self.control_thread.join()
    
    def get_status(self) -> Dict:
        """Get current status"""
        return {
            'target_temperature': self.target_temperature,
            'current_temperature': self.current_temperature,
            'is_running': self.is_running,
            'error': self.target_temperature - self.current_temperature
        }
    
    def set_target_temperature(self, temp: float):
        """Set target temperature"""
        self.target_temperature = temp
    
    def get_temperature_history(self) -> List[float]:
        """Get temperature history"""
        return self.temperature_history.copy()

class WebAPI:
    def __init__(self, controller: CoffeePIDController):
        self.controller = controller
        # FIXED: Load credentials from environment variables for security
        self.users = self._load_credentials()
    
    def _load_credentials(self) -> Dict[str, str]:
        """Load user credentials from environment variables"""
        import os
        users = {}
        
        # Load admin credentials
        admin_user = os.getenv('COFFEE_ADMIN_USER', 'admin')
        admin_pass = os.getenv('COFFEE_ADMIN_PASS')
        if admin_pass:
            users[admin_user] = admin_pass
        
        # Load regular user credentials
        user_name = os.getenv('COFFEE_USER_NAME', 'user')
        user_pass = os.getenv('COFFEE_USER_PASS')
        if user_pass:
            users[user_name] = user_pass
        
        # Fallback to default credentials if none provided (for development only)
        if not users:
            print("WARNING: No credentials found in environment variables. Using default credentials for development.")
            users = {
                'admin': 'password123',
                'user': 'userpass'
            }
        
        return users
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate user"""
        return username in self.users and self.users[username] == password
    
    def handle_request(self, method: str, path: str, data: Optional[Dict] = None) -> Dict:
        """Handle HTTP-like requests"""
        if method == 'GET':
            if path == '/status':
                return {'status': 'success', 'data': self.controller.get_status()}
            elif path == '/history':
                return {'status': 'success', 'data': self.controller.get_temperature_history()}
        elif method == 'POST':
            if path == '/start':
                self.controller.start()
                return {'status': 'success', 'message': 'Controller started'}
            elif path == '/stop':
                self.controller.stop()
                return {'status': 'success', 'message': 'Controller stopped'}
            elif path == '/set_target':
                if data and 'temperature' in data:
                    self.controller.set_target_temperature(data['temperature'])
                    return {'status': 'success', 'message': 'Target temperature set'}
        
        return {'status': 'error', 'message': 'Invalid request'}

def main():
    """Main application entry point"""
    controller = CoffeePIDController(target_temp=95.0)
    api = WebAPI(controller)
    
    print("Coffee PID Controller Started")
    print("Available commands:")
    print("  start - Start the controller")
    print("  stop - Stop the controller")
    print("  status - Get current status")
    print("  set_temp <value> - Set target temperature")
    print("  quit - Exit")
    
    while True:
        try:
            command = input("> ").strip().split()
            if not command:
                continue
            
            if command[0] == 'quit':
                break
            elif command[0] == 'start':
                result = api.handle_request('POST', '/start')
                print(result['message'])
            elif command[0] == 'stop':
                result = api.handle_request('POST', '/stop')
                print(result['message'])
            elif command[0] == 'status':
                result = api.handle_request('GET', '/status')
                if result['status'] == 'success':
                    data = result['data']
                    print(f"Target: {data['target_temperature']}°C")
                    print(f"Current: {data['current_temperature']:.1f}°C")
                    print(f"Running: {data['is_running']}")
                    print(f"Error: {data['error']:.1f}°C")
            elif command[0] == 'set_temp' and len(command) > 1:
                try:
                    temp = float(command[1])
                    result = api.handle_request('POST', '/set_target', {'temperature': temp})
                    print(result['message'])
                except ValueError:
                    print("Invalid temperature value")
            else:
                print("Unknown command")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    controller.stop()
    if controller.db_conn:
        controller.db_conn.close()
    print("Goodbye!")

if __name__ == "__main__":
    main()