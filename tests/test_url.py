import pytest

from chkapi.api_reader import URL
from chkapi.exceptions import BadUrlException


def test_not_valid_url_addrress_should_raise_bad_url_error():
    with pytest.raises(BadUrlException):
        URL("blablabla")
