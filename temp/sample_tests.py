
import datetime

import pytest

from application import default1, process_event_history
from contract import TermContract, MTMContract, PrepaidContract
from customer import Customer
from filter import DurationFilter, CustomerFilter, ResetFilter
from phoneline import PhoneLine


def create_single_customer_with_all_lines() -> Customer:
    contracts = [
        TermContract(start=datetime.date(year=2017, month=12, day=25),
                     end=datetime.date(year=2019, month=6, day=25)),
        MTMContract(start=datetime.date(year=2017, month=12, day=25)),
        PrepaidContract(start=datetime.date(year=2017, month=12, day=25),
                        balance=100)
    ]
    numbers = ['867-5309', '273-8255', '649-2568']
    customer = Customer(cid=7777)

    for i in range(len(contracts)):
        customer.add_phone_line(PhoneLine(numbers[i], contracts[i]))

    customer.new_month(12, 2017)
    return customer


test_dict = {'events': [
    {"type": "sms",
     "src_number": "867-5309",
     "dst_number": "273-8255",
     "time": "2018-01-01 01:01:01",
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]},
    {"type": "sms",
     "src_number": "273-8255",
     "dst_number": "649-2568",
     "time": "2018-01-01 01:01:02",
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]},
    {"type": "sms",
     "src_number": "649-2568",
     "dst_number": "867-5309",
     "time": "2018-01-01 01:01:03",
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]},
    {"type": "call",
     "src_number": "273-8255",
     "dst_number": "867-5309",
     "time": "2018-01-01 01:01:04",
     "duration": 10,
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]},
    {"type": "call",
     "src_number": "867-5309",
     "dst_number": "649-2568",
     "time": "2018-01-01 01:01:05",
     "duration": 50,
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]},
    {"type": "call",
     "src_number": "649-2568",
     "dst_number": "273-8255",
     "time": "2018-01-01 01:01:06",
     "duration": 50,
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]}
],
    'customers': [
        {'lines': [
            {'number': '867-5309',
             'contract': 'term'},
            {'number': '273-8255',
             'contract': 'mtm'},
            {'number': '649-2568',
             'contract': 'prepaid'}
        ],
            'id': 7777}
    ]
}

test_dict2 = {'events': [
    {"type": "call",
     "src_number": "696-4364",
     "dst_number": "592-4790",
     "time": "2018-02-25 03:02:04",
     "duration": 37,
     "src_loc": [-79.58565450923764, 43.680553650437815],
     "dst_loc": [-79.352774872513, 43.634805526615786]},
    {"type": "call",
     "src_number": "744-6324",
     "dst_number": "592-4790",
     "time": "2018-03-29 08:27:16",
     "duration": 317,
     "src_loc": [-79.58279034496788, 43.73002429774064],
     "dst_loc": [-79.65428007612073, 43.77110998138148]},
    {"type": "call",
     "src_number": "202-2830",
     "dst_number": "592-4790",
     "time": "2018-08-25 03:34:52",
     "duration": 275,
     "src_loc": [-79.45388033068112, 43.747092601717185],
     "dst_loc": [-79.43946589050805, 43.69111281375242]},
    {"type": "call",
     "src_number": "862-3646",
     "dst_number": "628-1219",
     "time": "2018-01-03 16:22:33",
     "duration": 270,
     "src_loc": [-79.2019388259489, 43.730170367672045],
     "dst_loc": [-79.62013525898622, 43.705310955370436]},
    {"type": "call",
     "src_number": "862-3646",
     "dst_number": "542-4197",
     "time": "2018-01-25 11:21:47",
     "duration": 251,
     "src_loc": [-79.29629777119764, 43.7268925653678],
     "dst_loc": [-79.48324834916122, 43.660938107792646]},
    {"type": "call",
     "src_number":"839-0275",
     "dst_number": "862-3646",
     "time": "2018-01-30 14:47:48",
     "duration": 95,
     "src_loc": [-79.5148500774525, 43.653098347822],
     "dst_loc": [-79.48599863925298, 43.69974524409387]},
    {"type": "call",
     "src_number": "862-3646",
     "dst_number": "134-5517",
     "time": "2018-03-11 06:54:38",
     "duration": 273,
     "src_loc": [-79.5503100443234, 43.620156132695854],
     "dst_loc": [-79.32302115583347, 43.73885584548211]},
    {"type": "call",
     "src_number": "862-3646",
     "dst_number": "839-7840",
     "time": "2018-04-22 15:51:15",
     "duration": 162,
     "src_loc": [-79.67924810498752, 43.76810031486083],
     "dst_loc": [-79.30914197270702, 43.783149269733286]},
    {"type": "call",
     "src_number": "444-0066",
     "dst_number": "862-3646",
     "time": "2018-06-24 02:36:57",
     "duration": 102,
     "src_loc": [-79.5574618529075, 43.6240591014208],
     "dst_loc": [-79.35440787053383, 43.70393819567041]},
    {"type": "call",
     "src_number": "862-3646",
     "dst_number": "496-5543",
     "time": "2018-07-14 20:18:51",
     "duration": 169,
     "src_loc": [-79.23400512557193, 43.6574047093065],
     "dst_loc": [-79.51090348936778, 43.79224376437641]},
    {"type": "call",
     "src_number": "010-3671",
     "dst_number": "003-3751",
     "time": "2018-01-08 13:50:47",
     "duration": 228,
     "src_loc": [-79.65427688179467, 43.57970398268384],
     "dst_loc": [-79.52734620498566, 43.755670347103724]},
    {"type": "call",
     "src_number": "003-3751",
     "dst_number": "961-3055",
     "time": "2018-01-19 06:50:23",
     "duration": 218,
     "src_loc": [-79.57741542341567, 43.66439888968034],
     "dst_loc": [-79.38994237591073, 43.71080098517488]},
    {"type": "call",
     "src_number": "056-7577",
     "dst_number": "003-3751",
     "time": "2018-03-07 16:11:25",
     "duration": 34,
     "src_loc": [-79.42605240288763, 43.76563017175154],
     "dst_loc": [-79.59582423729837, 43.693817432193896]},
    {"type": "call",
     "src_number": "003-3751",
     "dst_number": "126-2700",
     "time": "2018-03-08 15:50:00",
     "duration": 10,
     "src_loc": [-79.29465697649661, 43.75573716774675],
     "dst_loc": [-79.57868528648063, 43.71363881475937]},
    {"type": "call",
     "src_number": "003-3751",
     "dst_number": "261-2835",
     "time": "2018-03-13 02:19:05",
     "duration": 308,
     "src_loc": [-79.51645152082071, 43.73770304909404],
     "dst_loc": [-79.20408049896304, 43.75376148124834]},
    {"type": "call",
     "src_number": "161-4158",
     "dst_number": "003-3751",
     "time": "2018-04-27 18:33:59",
     "duration": 112,
     "src_loc": [-79.50109837473786, 43.649128460189495],
     "dst_loc": [-79.58035367528683, 43.72024781991437]},
    {"type": "call",
     "src_number": "845-3937",
     "dst_number": "003-3751",
     "time": "2018-05-03 15:32:58",
     "duration": 229,
     "src_loc": [-79.64583780838244, 43.79767218382863],
     "dst_loc": [-79.67637854200359, 43.75329407345544]},
    {"type": "call",
     "src_number": "482-2360",
     "dst_number": "003-3751",
     "time": "2018-05-22 08:13:53",
     "duration": 21,
     "src_loc": [-79.61334449803512, 43.67042755464903],
     "dst_loc": [-79.2539991543507, 43.71180872865551]},
    {"type": "call",
     "src_number": "942-5962",
     "dst_number": "003-3751",
     "time": "2018-07-05 16:01:44",
     "duration": 119,
     "src_loc": [-79.442882987505, 43.7829393296225],
     "dst_loc": [-79.38449286485941, 43.609144373119896]},
    {"type": "call",
     "src_number": "003-3751",
     "dst_number": "839-0275",
     "time": "2018-08-12 18:04:04",
     "duration": 334,
     "src_loc": [-79.53925432225459, 43.71965154000142],
     "dst_loc": [-79.2848731038022, 43.65892245751433]},
    {"type": "call",
     "src_number": "003-3751",
     "dst_number": "649-2182",
     "time": "2018-08-23 08:39:27",
     "duration": 303,
     "src_loc": [-79.62590929339632, 43.62284774311088],
     "dst_loc": [-79.20561410877215, 43.70139608562909]}
],
    'customers': [
        {"lines": [
            {"number": "592-4790",
             "contract": "term"},
            {"number": "862-3646",
             "contract": "prepaid"},
            {"number": "003-3751",
             "contract": "prepaid"}
        ], 
            "id": 7930}
    ]
}

def test_wah() -> None:
    """
    """
    customers = default1(test_dict2)
    customers[0].new_month(7, 2018)

    process_event_history(test_dict2, customers)

    bill = customers[0].generate_bill(7, 2018)
    assert bill[0] == 7930
    # assert bill[1] == pytest.approx(-29.925)
    assert bill[2][0]['total'] == pytest.approx(20)
    assert bill[2][0]['free_mins'] == 1
    assert bill[2][1]['total'] == pytest.approx(50.05)
    assert bill[2][1]['billed_mins'] == 1
    assert bill[2][2]['total'] == pytest.approx(-99.975)
    assert bill[2][2]['billed_mins'] == 1

def test_customer_creation() -> None:
    """ Test for the correct creation of Customer, PhoneLine, and Contract
    classes
    """
    customer = create_single_customer_with_all_lines()
    bill = customer.generate_bill(12, 2017)

    assert len(customer.get_phone_numbers()) == 3
    assert len(bill) == 3
    assert bill[0] == 7777 
    assert bill[1] == 270.0
    assert len(bill[2]) == 3
    assert bill[2][0]['total'] == 320
    assert bill[2][1]['total'] == 50
    assert bill[2][2]['total'] == -100

    # Check for the customer creation in application.py
    customer = default1(test_dict)[0]
    customer.new_month(12, 2017)
    bill = customer.generate_bill(12, 2017)

    assert len(customer.get_phone_numbers()) == 3
    assert len(bill) == 3
    assert bill[0] == 7777
    assert bill[1] == 270.0
    assert len(bill[2]) == 3
    assert bill[2][0]['total'] == 320
    assert bill[2][1]['total'] == 50
    assert bill[2][2]['total'] == -100


def test_events() -> None:
    """ Test the ability to make calls, and ensure that the CallHistory objects
    are populated
    """
    customers = default1(test_dict)
    customers[0].new_month(1, 2018)

    process_event_history(test_dict, customers)

    # Check the bill has been computed correctly
    bill = customers[0].generate_bill(1, 2018)
    assert bill[0] == 7777
    assert bill[1] == pytest.approx(-29.925)
    assert bill[2][0]['total'] == pytest.approx(20)
    assert bill[2][0]['free_mins'] == 1
    assert bill[2][1]['total'] == pytest.approx(50.05)
    assert bill[2][1]['billed_mins'] == 1
    assert bill[2][2]['total'] == pytest.approx(-99.975)
    assert bill[2][2]['billed_mins'] == 1

    # Check the CallHistory objects are populated
    history = customers[0].get_call_history('867-5309')
    assert len(history) == 1
    assert len(history[0].incoming_calls) == 1
    assert len(history[0].outgoing_calls) == 1

    history = customers[0].get_call_history()
    assert len(history) == 3
    assert len(history[0].incoming_calls) == 1
    assert len(history[0].outgoing_calls) == 1


def test_contract_start_dates() -> None:
    """ Test the start dates of the contracts.

    Ensure that the start dates are the correct dates as specified in the given
    starter code.
    """
    customers = default1(test_dict)
    for c in customers:
        for pl in c._phone_lines:
            assert pl.contract.start == datetime.date(
                year=2017, month=12, day=25)
            if hasattr(pl.contract, 'end'):  # only check if there is an end date (TermContract)
                assert pl.contract.end == datetime.date(
                    year=2019, month=6, day=25)


def test_filters() -> None:
    """ Test the functionality of the filters.

    We are only giving you a couple of tests here, you should expand both the
    dataset and the tests for the different types of applicable filters
    """
    customers = default1(test_dict)
    process_event_history(test_dict, customers)

    # Populate the list of calls:
    calls = []
    hist = customers[0].get_history()
    # only consider outgoing calls, we don't want to duplicate calls in the test
    calls.extend(hist[0])

    # The different filters we are testing
    filters = [
        DurationFilter(),
        CustomerFilter(),
        ResetFilter()
    ]

    # These are the inputs to each of the above filters in order.
    # Each list is a test for this input to the filter
    filter_strings = [
        ["L050", "G010", "L000", "50", "AA", ""],
        ["7777", "1111", "9999", "aaaaaaaa", ""],
        ["rrrr", ""]
    ]

    # These are the expected outputs from the above filter application
    # onto the full list of calls
    expected_return_lengths = [
        [1, 2, 0, 3, 3, 3],
        [3, 3, 3, 3, 3],
        [3, 3]
    ]

    for i in range(len(filters)):
        for j in range(len(filter_strings[i])):
            result = filters[i].apply(customers, calls, filter_strings[i][j])
            assert len(result) == expected_return_lengths[i][j]


if __name__ == '__main__':
    pytest.main(['sample_tests.py'])
