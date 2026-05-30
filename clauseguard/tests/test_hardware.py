import pytest
from backend.hardware.fingerprint import ProfileType, detect_profile
from backend.hardware.registry import ModelRegistry

def test_hardware_profile_registry():
    registry = ModelRegistry()
    config = registry.get_reasoning_config()
    
    assert config.profile_name is not None
    assert config.pair_limit in [15, 30, 50]
    assert config.confidence_threshold in [0.65, 0.70, 0.75]
    
    # Check initial active states
    assert not registry.fallback_active
    assert config.primary_model is not None

def test_hardware_model_switching_runtime():
    registry = ModelRegistry()
    config = registry.get_reasoning_config()
    
    # Trigger dynamic override switch
    switched = registry.switch_to_fallback()
    assert switched
    assert registry.fallback_active
    
    # Restore primary
    restored = registry.restore_primary()
    assert restored
    assert not registry.fallback_active
