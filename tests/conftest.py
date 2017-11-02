import pytest
import os


@pytest.fixture(scope='session')
def test_dir():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, 'data')


@pytest.fixture(scope='session')
def short_format_file(test_dir):
    return os.path.join(test_dir, 'short_format.TextGrid')


@pytest.fixture(scope='session')
def long_format_file(test_dir):
    return os.path.join(test_dir, 'long_format.TextGrid')
