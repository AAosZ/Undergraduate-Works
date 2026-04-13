from typing import Union
from phoneline import PhoneLine
from callhistory import CallHistory
from call import Call


class Customer:
    # === Private Attributes ===
    # _id:
    #     this customer's 4 digit Customer id
    # _phone_lines:
    #     this customer's phone lines
    _id: int
    _phone_lines: list[PhoneLine]

    def __init__(self, cid: int) -> None:
        self._id = cid
        self._phone_lines = []

    def new_month(self, month: int, year: int) -> None:
        for line in self._phone_lines:
            line.new_month(month, year)

    def make_call(self, call: Call) -> None:
        for phoneline in self._phone_lines:
            if phoneline.number == call.src_number:
                phoneline.make_call(call)

    def receive_call(self, call: Call) -> None:
        for phoneline in self._phone_lines:
            if phoneline.number == call.dst_number:
                phoneline.receive_call(call)

    def cancel_phone_line(self, number: str) -> Union[float, None]:
        fee = None
        for pl in self._phone_lines:
            if pl.get_number() == number:
                self._phone_lines.remove(pl)
                fee = pl.cancel_line()
        return fee

    def add_phone_line(self, pline: PhoneLine) -> None:
        self._phone_lines.append(pline)

    def get_phone_numbers(self) -> list[str]:
        numbers = []
        for line in self._phone_lines:
            numbers.append(line.get_number())
        return numbers

    def get_id(self) -> int:
        return self._id

    def __contains__(self, item: str) -> bool:
        contains = False
        for line in self._phone_lines:
            if line.get_number() == item:
                contains = True
        return contains

    def generate_bill(self, month: int, year: int) \
            -> tuple[int, float, list[dict]]:
        bills = []
        total = 0
        for line in self._phone_lines:
            line_bill = line.get_bill(month, year)
            if line_bill is not None:
                bills.append(line_bill)
                total += line_bill['total']
        return self._id, total, bills

    def print_bill(self, month: int, year: int) -> None:
        bill_data = self.generate_bill(month, year)
        print("========= BILL ===========")
        print("Customer id: " + str(self._id) + " month: "
              + str(month) + "/" + str(year))
        print(f'Total due this month: {bill_data[1]:.2f}')
        for line in bill_data[2]:
            print("\tnumber: " + line['number'] + "  type: " + line['type'])
        print("==========================")

    def get_history(self) \
            -> tuple[list[Call], list[Call]]:
        history = ([], [])
        for line in self._phone_lines:
            line_history = line.get_monthly_history()
            history[0].extend(line_history[0])
            history[1].extend(line_history[1])
        return history

    def get_call_history(self, number: str = None) -> list[CallHistory]:
        history = []
        for line in self._phone_lines:
            if number is not None:
                if line.get_number() == number:
                    history.append(line.get_call_history())
            else:
                history.append(line.get_call_history())
        return history


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'phoneline', 'call', 'callhistory'
        ],
        'allowed-io': ['print_bill'],
        'disable': ['R0902', 'R0913'],
        'generated-members': 'pygame.*'
    })
