from app.settings import Settings


def test_phase15_boundary_is_post_mvp_for_nz_tiny_pilot():
    settings = Settings(testing=True)
    assert settings.phase15_boundary_status == "POST_MVP_SCALE_NOT_REQUIRED_FOR_NZ_TINY_PILOT"
