from typing import Optional, Union
from call import Call
from callhistory import CallHistory
from bill import Bill
from contract import Contract


class PhoneLine:
    number: str
    contract: Contract
    bills: dict[tuple[int, int], Bill]
    callhistory: CallHistory

    def __init__(self, number: str, contract: Contract) -> None:
        self.number = number
        self.contract = contract
        self.callhistory = CallHistory()
        self.bills = {}

    def new_month(self, month: int, year: int) -> None:
        if (month, year) not in self.bills:
            self.bills[(month, year)] = Bill()
            self.contract.new_month(month, year, self.bills[(month, year)])

    def make_call(self, call: Call) -> None:
        self.callhistory.register_outgoing_call(call)
        date = call.get_bill_date()
        if date not in self.bills:
            self.new_month(date[0], date[1])
        self.contract.bill_call(call)

    def receive_call(self, call: Call) -> None:
        self.callhistory.register_incoming_call(call)
        date = call.get_bill_date()
        if date not in self.bills:
            PhoneLine.new_month(self, date[0], date[1])

    def cancel_line(self) -> float:
        return self.contract.cancel_contract()

    def get_number(self) -> str:
        return self.number

    def get_call_history(self) -> CallHistory:
        return self.callhistory

    def get_monthly_history(self, month: int = None, year: int = None) -> \
            tuple[list[Call], list[Call]]:
        return self.callhistory.get_monthly_history(month, year)

    def get_bill(self, month: int, year: int) \
            -> Optional[dict[str, Union[float, int]]]:
        if (month, year) not in self.bills:
            return None

        bill_summary = self.bills[(month, year)].get_summary()
        bill_summary['number'] = self.number
        return bill_summary


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing',
            'call', 'callhistory', 'bill', 'contract'
        ],
        'generated-members': 'pygame.*'
    })
