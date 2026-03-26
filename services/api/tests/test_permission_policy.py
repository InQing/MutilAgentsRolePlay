from app.director.models import VisibilityMode
from app.director.policies.member_director_hybrid import MemberDirectorHybridPolicy


def test_hybrid_policy_uses_delayed_visibility_for_sensitive_views() -> None:
    policy = MemberDirectorHybridPolicy(director_delay_seconds=300)

    view = policy.describe_view()

    assert view.private_chat_visibility == VisibilityMode.DELAYED
    assert view.plan_visibility == VisibilityMode.DELAYED
    assert view.relationship_visibility == VisibilityMode.DELAYED
    assert view.can_inject_events is True
    assert view.can_control_world is True
