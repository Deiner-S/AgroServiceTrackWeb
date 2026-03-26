import pytest

from checklist.repository.base_repository import BaseRepository


def test_get_queryset_raises_when_model_is_not_configured():
    repository = BaseRepository()

    with pytest.raises(ValueError, match="Repository model is not configured."):
        repository.get_queryset()
