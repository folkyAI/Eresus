# 🤖 ERESUS F429 Multi-Agent Testing System

**Streamlined, automated testing for your Marlin firmware**

## 🚀 Quick Start

1. **Upload firmware** to your ERESUS F429 board
2. **Connect USB** to your computer
3. **Run tests** with one command:

```bash
python run_tests.py
```

## 🎯 What It Tests

### 🔧 Hardware Agent
- Firmware version (M115)
- Endstop status (M119)
- Temperature sensors (M105)
- Motor movement (X, Y, Z, E)

### ⚡ TMC Stepper Agent
- TMC driver status (M122)
- Current settings (M906)
- Microstepping (M350)

### 📏 BLTouch Agent
- Probe deploy/retract (M280)
- Self-test functionality
- Auto-leveling readiness

### 🛡️ Safety Agent
- Emergency stop (M112)
- Thermal protection
- Safety systems

## 📊 Sample Output

```
🤖 ERESUS F429 Multi-Agent Testing System
==================================================
🔌 Connecting to printer...
✅ Connected successfully!

🔧 Running hardware tests...
🔧 Running tmc tests...
🔧 Running bltouch tests...
🔧 Running safety tests...

============================================================
🎯 ERESUS F429 MARLIN FIRMWARE TEST SUMMARY
============================================================

📋 HARDWARE AGENT:
  ✅ Firmware Version: passed (0.15s)
  ✅ Endstops: passed (0.12s)
  ✅ Temperature Sensors: passed (0.10s)
  ✅ X Motor: passed (4.23s)
  ✅ Y Motor: passed (4.18s)
  ✅ Z Motor: passed (3.45s)
  ✅ E Motor: passed (3.67s)
  📊 7/7 tests passed

📋 TMC AGENT:
  ✅ TMC Status: passed (0.08s)
  ✅ Current Settings: passed (0.05s)
  ✅ Microstepping: passed (0.06s)
  📊 3/3 tests passed

🎉 OVERALL: 12/12 tests passed
🚀 All tests passed! Firmware is ready for production!
```

## 🔧 Customization

Edit `test_agents.py` to:
- Add new test agents
- Modify test parameters
- Change COM port settings
- Add custom test cases

## 📁 Files

- `test_agents.py` - Main testing system
- `run_tests.py` - Simple launcher
- `requirements.txt` - Dependencies
- `README_Testing.md` - This file

## 🎯 Benefits

✅ **Automated** - No manual G-code typing
✅ **Comprehensive** - Tests all major systems
✅ **Fast** - Complete test suite in ~30 seconds
✅ **Reliable** - Consistent test results
✅ **Extensible** - Easy to add new tests

## 🚨 Troubleshooting

**Connection Failed:**
- Check USB cable
- Try different COM port
- Verify board is powered on

**Tests Failing:**
- Check firmware upload
- Verify hardware connections
- Review error messages

---

**Your ERESUS F429 firmware is ready for automated testing!** 🚀
