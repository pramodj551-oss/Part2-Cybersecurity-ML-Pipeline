from src.production_intelligence import HealthSnapshot, automated_action, classify, resilience_plan

def test_healthy_snapshot():
    s=HealthSnapshot(.999,120,.002,.05)
    assert classify(s)=="healthy"
    assert automated_action(s)["action"]=="observe"

def test_degraded_holds_promotion():
    s=HealthSnapshot(.993,450,.012,.25)
    assert classify(s)=="degraded"
    assert "hold_promotion" in resilience_plan("degraded")["actions"]

def test_critical_rolls_back():
    s=HealthSnapshot(.97,1400,.08,.10)
    assert automated_action(s)["action"]=="rollback_and_page"
    assert "rollback" in resilience_plan("critical")["actions"]
