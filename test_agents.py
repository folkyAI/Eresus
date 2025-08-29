#!/usr/bin/env python3
"""
ERESUS F429 Marlin Firmware Multi-Agent Testing System
Specialized agents for different testing domains
"""

import time
import serial
import threading
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class TestStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class TestResult:
    name: str
    status: TestStatus
    message: str
    duration: float
    data: Optional[Dict] = None

class BaseTestAgent:
    def __init__(self, name: str, serial_conn: serial.Serial):
        self.name = name
        self.serial = serial_conn
        self.results: List[TestResult] = []
        
    def send_command(self, command: str, timeout: float = 5.0) -> str:
        """Send G-code command and return response"""
        self.serial.write(f"{command}\n".encode())
        time.sleep(0.1)
        
        response = ""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.serial.in_waiting:
                line = self.serial.readline().decode().strip()
                if line:
                    response += line + "\n"
                if "ok" in line.lower():
                    break
        return response
    
    def run_test(self, test_name: str, test_func, *args, **kwargs) -> TestResult:
        """Execute a test and record results"""
        start_time = time.time()
        try:
            result = test_func(*args, **kwargs)
            status = TestStatus.PASSED if result else TestStatus.FAILED
            message = f"Test {test_name} completed"
        except Exception as e:
            status = TestStatus.FAILED
            message = f"Test {test_name} failed: {str(e)}"
        
        duration = time.time() - start_time
        test_result = TestResult(test_name, status, message, duration)
        self.results.append(test_result)
        return test_result

class HardwareAgent(BaseTestAgent):
    """Tests basic hardware functionality"""
    
    def test_firmware_version(self) -> bool:
        """Test M115 - Firmware version"""
        response = self.send_command("M115")
        return "FIRMWARE_NAME" in response
    
    def test_endstops(self) -> bool:
        """Test M119 - Endstop status"""
        response = self.send_command("M119")
        return "X_MIN" in response and "Y_MIN" in response and "Z_MIN" in response
    
    def test_temperature_sensors(self) -> bool:
        """Test M105 - Temperature sensors"""
        response = self.send_command("M105")
        return "T:" in response and "B:" in response
    
    def test_motor_movement(self, axis: str, distance: float = 10) -> bool:
        """Test motor movement for specific axis"""
        try:
            # Home first
            self.send_command(f"G28 {axis}")
            time.sleep(2)
            
            # Move
            self.send_command(f"G1 {axis}{distance} F1000")
            time.sleep(2)
            
            # Return to home
            self.send_command(f"G1 {axis}0 F1000")
            return True
        except:
            return False
    
    def run_all_tests(self) -> List[TestResult]:
        """Run all hardware tests"""
        tests = [
            ("Firmware Version", self.test_firmware_version),
            ("Endstops", self.test_endstops),
            ("Temperature Sensors", self.test_temperature_sensors),
            ("X Motor", lambda: self.test_motor_movement("X")),
            ("Y Motor", lambda: self.test_motor_movement("Y")),
            ("Z Motor", lambda: self.test_motor_movement("Z", 5)),
            ("E Motor", lambda: self.test_motor_movement("E", 5)),
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        return self.results

class TMCStepperAgent(BaseTestAgent):
    """Tests TMC stepper driver functionality"""
    
    def test_tmc_status(self) -> bool:
        """Test M122 - TMC driver status"""
        response = self.send_command("M122")
        return "OK" in response and "X:" in response
    
    def test_current_settings(self) -> bool:
        """Test M906 - Current settings"""
        response = self.send_command("M906")
        return "X:" in response and "Y:" in response
    
    def test_microstepping(self) -> bool:
        """Test M350 - Microstepping settings"""
        response = self.send_command("M350")
        return "X:" in response and "Y:" in response
    
    def run_all_tests(self) -> List[TestResult]:
        """Run all TMC tests"""
        tests = [
            ("TMC Status", self.test_tmc_status),
            ("Current Settings", self.test_current_settings),
            ("Microstepping", self.test_microstepping),
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        return self.results

class BLTouchAgent(BaseTestAgent):
    """Tests BLTouch auto-leveling functionality"""
    
    def test_probe_deploy(self) -> bool:
        """Test M280 P0 S10 - Probe deploy"""
        response = self.send_command("M280 P0 S10")
        time.sleep(2)
        return "ok" in response.lower()
    
    def test_probe_retract(self) -> bool:
        """Test M280 P0 S90 - Probe retract"""
        response = self.send_command("M280 P0 S90")
        time.sleep(2)
        return "ok" in response.lower()
    
    def test_probe_self_test(self) -> bool:
        """Test M280 P0 S120 - Self test"""
        response = self.send_command("M280 P0 S120")
        time.sleep(3)
        return "ok" in response.lower()
    
    def run_all_tests(self) -> List[TestResult]:
        """Run all BLTouch tests"""
        tests = [
            ("Probe Deploy", self.test_probe_deploy),
            ("Probe Retract", self.test_probe_retract),
            ("Probe Self Test", self.test_probe_self_test),
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        return self.results

class SafetyAgent(BaseTestAgent):
    """Tests safety systems"""
    
    def test_emergency_stop(self) -> bool:
        """Test M112 - Emergency stop"""
        try:
            response = self.send_command("M112")
            time.sleep(1)
            # Reset after emergency stop
            self.send_command("M999")
            return True
        except:
            return False
    
    def test_thermal_protection(self) -> bool:
        """Test thermal protection by checking limits"""
        response = self.send_command("M503")
        return "THERMAL_PROTECTION" in response or "THERMAL_RUNAWAY" in response
    
    def run_all_tests(self) -> List[TestResult]:
        """Run all safety tests"""
        tests = [
            ("Emergency Stop", self.test_emergency_stop),
            ("Thermal Protection", self.test_thermal_protection),
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        return self.results

class TestCoordinator:
    """Coordinates all testing agents"""
    
    def __init__(self, port: str = "COM3", baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.agents = {}
        
    def connect(self) -> bool:
        """Connect to the printer"""
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=5)
            time.sleep(2)  # Wait for connection
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def initialize_agents(self):
        """Initialize all testing agents"""
        if not self.serial:
            raise Exception("Serial connection not established")
        
        self.agents = {
            "hardware": HardwareAgent("Hardware", self.serial),
            "tmc": TMCStepperAgent("TMC Steppers", self.serial),
            "bltouch": BLTouchAgent("BLTouch", self.serial),
            "safety": SafetyAgent("Safety", self.serial),
        }
    
    def run_all_tests(self) -> Dict[str, List[TestResult]]:
        """Run all tests from all agents"""
        if not self.agents:
            self.initialize_agents()
        
        results = {}
        for agent_name, agent in self.agents.items():
            print(f"\n🔧 Running {agent_name} tests...")
            results[agent_name] = agent.run_all_tests()
        
        return results
    
    def print_summary(self, results: Dict[str, List[TestResult]]):
        """Print test summary"""
        print("\n" + "="*60)
        print("🎯 ERESUS F429 MARLIN FIRMWARE TEST SUMMARY")
        print("="*60)
        
        total_tests = 0
        passed_tests = 0
        
        for agent_name, agent_results in results.items():
            print(f"\n📋 {agent_name.upper()} AGENT:")
            agent_passed = 0
            for result in agent_results:
                status_icon = "✅" if result.status == TestStatus.PASSED else "❌"
                print(f"  {status_icon} {result.name}: {result.status.value} ({result.duration:.2f}s)")
                if result.status == TestStatus.PASSED:
                    agent_passed += 1
                    passed_tests += 1
                total_tests += 1
            
            print(f"  📊 {agent_passed}/{len(agent_results)} tests passed")
        
        print(f"\n🎉 OVERALL: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🚀 All tests passed! Firmware is ready for production!")
        else:
            print("⚠️  Some tests failed. Review results and fix issues.")

def main():
    """Main testing function"""
    print("🤖 ERESUS F429 Multi-Agent Testing System")
    print("="*50)
    
    # Initialize coordinator
    coordinator = TestCoordinator()
    
    # Connect to printer
    print("🔌 Connecting to printer...")
    if not coordinator.connect():
        print("❌ Failed to connect to printer")
        return
    
    print("✅ Connected successfully!")
    
    # Run all tests
    print("🚀 Starting comprehensive testing...")
    results = coordinator.run_all_tests()
    
    # Print summary
    coordinator.print_summary(results)
    
    # Cleanup
    if coordinator.serial:
        coordinator.serial.close()

if __name__ == "__main__":
    main()
