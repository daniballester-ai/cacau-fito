"""Unit tests for compute_uncertainty() (see openspec/changes/add-uncertain-diagnosis-flag)."""
from src.inference_service.model import compute_uncertainty


def test_high_confidence_single_winner_is_not_uncertain():
    is_uncertain, reason = compute_uncertainty({"healthy": 0.9, "cssvd": 0.06, "anthracnose": 0.04})
    assert is_uncertain is False
    assert reason is None


def test_low_top_confidence_is_uncertain_low_confidence():
    is_uncertain, reason = compute_uncertainty({"healthy": 0.5, "cssvd": 0.3, "anthracnose": 0.2})
    assert is_uncertain is True
    assert reason == "low_confidence"


def test_close_race_between_top_two_is_uncertain_close_call():
    # top confidence (0.62) clears the 0.6 threshold, but margin to runner-up (0.62 - 0.55 = 0.07) is below 0.1
    is_uncertain, reason = compute_uncertainty({"healthy": 0.62, "cssvd": 0.55, "anthracnose": 0.0})
    assert is_uncertain is True
    assert reason == "close_call"


def test_low_confidence_and_close_call_reports_low_confidence():
    # top prob 0.4 is below threshold AND margin to runner-up (0.02) is below close-call margin
    is_uncertain, reason = compute_uncertainty({"healthy": 0.4, "cssvd": 0.38, "anthracnose": 0.22})
    assert is_uncertain is True
    assert reason == "low_confidence"
