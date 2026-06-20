import pytest

from subscriber import entrepot_id_from_topic


@pytest.mark.parametrize(
    "topic, expected",
    [
        ("bresil/entrepot1/mesures", "entrepot-bresil-1"),
        ("equateur/entrepot1/mesures", "entrepot-equateur-1"),
        ("colombie/entrepot2/mesures", "entrepot-colombie-2"),
        ("bresil/entrepot1", "entrepot-bresil-1"),  # robuste à un topic plus court
    ],
)
def test_entrepot_id_from_topic_pays_valide(topic, expected):
    assert entrepot_id_from_topic(topic) == expected


def test_entrepot_id_from_topic_pays_inconnu():
    assert entrepot_id_from_topic("france/entrepot1/mesures") is None


def test_entrepot_id_from_topic_topic_trop_court():
    assert entrepot_id_from_topic("bresil") is None
