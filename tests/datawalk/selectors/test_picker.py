from datawalk.selectors.picker import Picker


def test_picker_repr():
    picker = Picker(('firstname', 'lastname'))
    assert repr(picker) == '{firstname,lastname}'


def test_picker_call():
    address = {'country': 'France', 'city': 'Rennes', 'zipcode': '35700'}
    picker = Picker(('city', 'zipcode'))
    assert picker(address) == {'city': 'Rennes', 'zipcode': '35700'}
