import pytest

from app.services.customer_facing_boundary_service import CustomerFacingBoundaryService


def test_no_customer_facing_quote_generated():
    with pytest.raises(ValueError):
        CustomerFacingBoundaryService().assert_internal_only("customer_facing_quote")


def test_no_customer_facing_proposal_generated():
    with pytest.raises(ValueError):
        CustomerFacingBoundaryService().assert_internal_only("customer_facing_proposal")


def test_no_customer_facing_reply_generated():
    with pytest.raises(ValueError):
        CustomerFacingBoundaryService().assert_internal_only("customer_facing_reply")


def test_internal_guidance_only():
    assert CustomerFacingBoundaryService().internal_guidance("ask scope first") == "ask scope first"
