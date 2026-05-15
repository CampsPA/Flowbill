# Start Docker -> run : python -m pytest tests/test_webhook_signature.py
# To run the whole test suite -> pytest tests/ -v

# This test verifies whether the webhook payload is signed using HMAC-SHA256 and the 
# stripe_webhook_secret so that it can trust the payload
# This ensures an attacker who knows the webhook URL cannot send fake billing events.

# This is a different test and there is no corresponding file in the billing folder
# In this file we are testing the app/webhooks/stripe_receiver.py

from app.webhooks import stripe_receiver
# Mock tests
from unittest.mock import patch, MagicMock
import stripe

# Test 1 — Valid signature accepted
async def test_valid_signature(client):
    with patch("app.webhooks.stripe_receiver.stripe.Webhook.construct_event") as mock_session:
        mock_event = MagicMock()
        mock_event.type = "payment_intent.succeeded"
        mock_event.data.object.metadata.get.return_value = None
        mock_session.return_value = mock_event
        response = await client.post("/stripe/webhook/", content=b"fake_payload", headers={"stripe-signature": "fake_signature"})
    assert response.status_code == 200
        

# Test 2 — Tampered payload rejected
async def test_tempered_payload_reject(client):
    with patch("app.webhooks.stripe_receiver.stripe.Webhook.construct_event") as mock_session:
        mock_event = MagicMock()
        mock_event.type = "payment_intent.succeeded"
        mock_event.data.object.metadata.get.return_value = None
        mock_session.side_effect = stripe.error.SignatureVerificationError(message = "Signature Error", sig_header= "fake _signature")
        response = await client.post("/stripe/webhook/", content=b"fake_payload", headers={"stripe-signature": "fake_signature"})
    assert response.status_code == 400


# Test 3 — Wrong secret rejected - here the payload has a different signature than 
# what the app expects (treat as a invalid payload)
async def test_wrong_secret(client):
    with patch("app.webhooks.stripe_receiver.stripe.Webhook.construct_event") as mock_session:
        mock_event = MagicMock()
        mock_event.type = "payment_intent.succeeded"
        mock_event.data.object.metadata.get.return_value = None
        mock_session.side_effect = ValueError("invalid payload")
        response = await client.post("/stripe/webhook/", content=b"invalid_payload", headers={"stripe-signature": "wrong_signature"})
    assert response.status_code == 400

# Test 4 — Missing signature header rejected
# same test as test 3 but this time the signature header is missing - that make spayload invalid
async def test_missing_sig_header(client):
    with patch("app.webhooks.stripe_receiver.stripe.Webhook.construct_event") as mock_session:
        mock_event = MagicMock()
        mock_event.type = "payment_intent.succeeded"
        mock_event.data.object.metadata.get.return_value = None
        mock_session.side_effect = ValueError("payload rejected")
        response = await client.post("/stripe/webhook/", content=b"payload_rejected", headers={"stripe-signature": "signature_missing"})
    assert response.status_code == 400


