import importlib
import pathlib
import sys
import types

# Provide a fake RPi.GPIO module so driver imports work on non-RPi platforms
fake_rpi = types.ModuleType("RPi")
fake_gpio = types.ModuleType("GPIO")
fake_rpi.GPIO = fake_gpio
sys.modules.setdefault("RPi", fake_rpi)
sys.modules.setdefault("RPi.GPIO", fake_gpio)

# The vendored DFRobot_BloodOxygen_S driver cannot be imported on non-RPi
# platforms. Provide a minimal stub so other modules can be imported.
stub_bo = types.ModuleType("DFRobot_BloodOxygen_S")
stub_bo.DFRobot_BloodOxygen_S_i2c = object
sys.modules.setdefault("DFRobot_BloodOxygen_S", stub_bo)

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

MODULES = [p.stem for p in ROOT.glob('*.py') if p.is_file()]


def test_imports():
    for name in MODULES:
        importlib.import_module(name)
