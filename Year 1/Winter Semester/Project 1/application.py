
import datetime
import json

from call import Call
from contract import TermContract, MTMContract, PrepaidContract
from customer import Customer
from phoneline import PhoneLine
from visualizer import Visualizer


def import_data() -> dict[str, list[dict]]:
    with open("../../../dataset.json") as o:
        log = json.load(o)
        return log


def default1(log: dict[str, list[dict]]) -> list[Customer]:
    customer_list = []
    for cust in log['customers']:
        customer = Customer(cust['id'])
        for line in cust['lines']:
            # contract = Contract(datetime.datetime.now())
            # contract.new_month = lambda *args: None
            # contract.bill_call = lambda *args: None

            contract = None
            if line['contract'] == 'prepaid':
                # start with $100 credit on the account
                contract = PrepaidContract(datetime.date(2017, 12, 25), 100)
            elif line['contract'] == 'mtm':
                contract = MTMContract(datetime.date(2017, 12, 25))
            elif line['contract'] == 'term':
                contract = TermContract(datetime.date(2017, 12, 25),
                                        datetime.date(2019, 6, 25))
            else:
                print("ERROR: unknown contract type")

            line = PhoneLine(line['number'], contract)
            customer.add_phone_line(line)
        customer_list.append(customer)
    return customer_list


def find_customer_by_number(number: str, customer_list: list[Customer]) \
        -> Customer:
    cust = None
    for customer in customer_list:
        if number in customer:
            cust = customer
    return cust


def new_month(customer_list: list[Customer], month: int, year: int) -> None:
    for cust in customer_list:
        cust.new_month(month, year)


def process_event_history(log: dict[str, list[dict]],
                          customer_list: list[Customer]) -> None:
    # (Based on Precondition) Initializes the first customers "time" and
    # start recording the bills from this date
    billing_date = datetime.datetime.strptime(log['events'][0]['time'],
                                              "%Y-%m-%d %H:%M:%S")

    current_month = billing_date.month
    current_year = billing_date.year

    # initialize a for loop that checks each customer
    for detail in log['events']:
        date = datetime.datetime.strptime(detail['time'],
                                          "%Y-%m-%d %H:%M:%S")

        # conditional check for a new month
        if billing_date.month != current_month or billing_date.year \
                != current_year:
            new_month(customer_list, billing_date.month, billing_date.year)
            current_month = date.month
            current_year = date.year

        # conditional check for customer call type
        if detail['type'] == 'call':
            srcnum = detail['src_number']
            dstnum = detail['dst_number']
            duration = detail['duration']
            call_loc = detail['src_loc']
            rec_loc = detail['dst_loc']

            # find caller and receiver in customer_list
            call_id = find_customer_by_number(srcnum, customer_list)
            rec_id = \
                find_customer_by_number(dstnum, customer_list)

            # add callers and receivers to record
            if call_id and rec_id:
                call = Call(srcnum, dstnum, date, duration, call_loc, rec_loc)
                call_id.make_call(call)
                rec_id.receive_call(call)


if __name__ == '__main__':
    v = Visualizer()
    print("Toronto map coordinates:")
    print("  Lower-left corner: -79.697878, 43.576959")
    print("  Upper-right corner: -79.196382, 43.799568")

    input_dictionary = import_data()
    customers = default1(input_dictionary)
    process_event_history(input_dictionary, customers)


    all_calls = []
    for c in customers:
        hist = c.get_history()
        all_calls.extend(hist[0])
    print("\n-----------------------------------------")
    print("Total Calls in the dataset:", len(all_calls))
    events = all_calls
    while not v.has_quit():
        events = v.handle_window_events(customers, events)

        connections = []
        drawables = []
        for event in events:
            connections.append(event.get_connection())
            drawables.extend(event.get_drawables())

        # Put the connections on top of the other sprites
        drawables.extend(connections)
        v.render_drawables(drawables)

    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'json', 'datetime',
            'visualizer', 'customer', 'call', 'contract', 'phoneline'
        ],
        'allowed-io': [
            'create_customers', 'import_data'
        ],
        'generated-members': 'pygame.*'
    })
