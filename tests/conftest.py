import pytest
from src.data_package import validate

@pytest.fixture(scope='session')
def package():return validate()
