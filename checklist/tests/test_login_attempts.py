import pytest

from checklist.login_attempts import get_login_attempt_state


@pytest.mark.django_db
def test_auth_login_blocks_after_max_failed_attempts(client, rf):
    for _ in range(5):
        client.post(
            "/gerenciador/login/",
            {"usuario": "usuario.teste", "senha": "senha-invalida"},
        )

    request = rf.post(
        "/gerenciador/login/",
        {"usuario": "usuario.teste", "senha": "senha-invalida"},
    )
    request.META["REMOTE_ADDR"] = "127.0.0.1"

    state = get_login_attempt_state(request, "usuario.teste")

    assert state["is_blocked"] is True
