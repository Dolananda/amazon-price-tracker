from unittest.mock import patch

import notifications


def test_send_telegram_noop_when_not_configured(monkeypatch):
    monkeypatch.setattr(notifications, "TELEGRAM_BOT_TOKEN", None)
    monkeypatch.setattr(notifications, "TELEGRAM_CHAT_ID", None)

    with patch("notifications.requests.post") as mock_post:
        notifications.send_telegram("test")
        mock_post.assert_not_called()


def test_send_telegram_posts_when_configured(monkeypatch):
    monkeypatch.setattr(notifications, "TELEGRAM_BOT_TOKEN", "fake-token")
    monkeypatch.setattr(notifications, "TELEGRAM_CHAT_ID", "12345")

    with patch("notifications.requests.post") as mock_post:
        notifications.send_telegram("hello")

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert "fake-token" in args[0]
        assert kwargs["json"] == {"chat_id": "12345", "text": "hello"}


def test_send_discord_noop_when_not_configured(monkeypatch):
    monkeypatch.setattr(notifications, "DISCORD_WEBHOOK_URL", None)

    with patch("notifications.requests.post") as mock_post:
        notifications.send_discord("test")
        mock_post.assert_not_called()


def test_send_discord_posts_when_configured(monkeypatch):
    monkeypatch.setattr(notifications, "DISCORD_WEBHOOK_URL", "https://discord.example/webhook")

    with patch("notifications.requests.post") as mock_post:
        notifications.send_discord("hello")

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://discord.example/webhook"
        assert kwargs["json"] == {"content": "hello"}


def test_send_email_noop_when_not_configured(monkeypatch):
    monkeypatch.setattr(notifications, "EMAIL", None)
    monkeypatch.setattr(notifications, "EMAIL_PASSWORD", None)

    with patch("notifications.smtplib.SMTP") as mock_smtp:
        notifications.send_email("subject", "body")
        mock_smtp.assert_not_called()


def test_notify_fans_out_to_every_channel(monkeypatch):
    calls = []
    monkeypatch.setattr(notifications, "send_email", lambda subject, body: calls.append("email"))
    monkeypatch.setattr(notifications, "send_telegram", lambda message: calls.append("telegram"))
    monkeypatch.setattr(notifications, "send_discord", lambda message: calls.append("discord"))

    notifications.notify("Subject", "Body")

    assert calls == ["email", "telegram", "discord"]
