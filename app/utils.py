from typing import Dict


def validate_message(message: Dict):
    assert set(message.keys()) == {'action', 'channel'}
