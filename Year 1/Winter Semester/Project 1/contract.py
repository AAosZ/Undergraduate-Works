import datetime
from math import ceil
from typing import Optional
from bill import Bill
from call import Call


# Constants for the month-to-month contract monthly fee and term deposit
MTM_MONTHLY_FEE = 50.00
TERM_MONTHLY_FEE = 20.00
TERM_DEPOSIT = 300.00

# Constants for the included minutes and SMSs in the term contracts (per month)
TERM_MINS = 100

# Cost per minute and per SMS in the month-to-month contract
MTM_MINS_COST = 0.05

# Cost per minute and per SMS in the term contract
TERM_MINS_COST = 0.1

# Cost per minute and per SMS in the prepaid contract
PREPAID_MINS_COST = 0.025


class Contract:
    start: datetime.date
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        self.start = start
        self.bill = None

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        raise NotImplementedError

    def bill_call(self, call: Call) -> None:
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        self.start = None
        return self.bill.get_cost()


class TermContract(Contract):
    # attribute types
    start: datetime.datetime
    end: datetime.datetime
    bill: Optional[Bill]
    _return_deposit: bool

    def __init__(self, start: datetime.datetime,
                 end: datetime.datetime) -> None:
        Contract.__init__(self, start)
        self.end = end
        self._return_deposit = False

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        bill.add_fixed_cost(TERM_MONTHLY_FEE)
        bill.set_rates("TERM", TERM_MINS_COST)
        bill.add_free_minutes(TERM_MINS)

        # prevents adding more than one term deposit in one contract
        if self.start.month == month and self.start.year == year:
            bill.add_fixed_cost(TERM_DEPOSIT)

        # checks whether term deposit can be returned
        if (self.end.month < month and self.end.year == year) or \
                self.end.year < year:
            self.return_deposit = True

        self.bill = bill

    def bill_call(self, call: Call) -> None:
        used_mins = self.bill.free_min - ceil(call.duration / 60.0)
        if used_mins >= 0:
            self.bill.add_free_minutes(-used_mins)

        else:
            self.bill.add_billed_minutes(-1 * used_mins)
            self.bill.free_min = 0

    def cancel_contract(self) -> float:
        self.start = None
        if self._return_deposit:
            self.bill.add_fixed_cost(-TERM_DEPOSIT)

        return self.bill.get_cost()


class MTMContract(Contract):

    def __init__(self, start: datetime.datetime) -> None:
        Contract.__init__(self, start)

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        bill.add_fixed_cost(MTM_MONTHLY_FEE)
        bill.set_rates("MTM", MTM_MINS_COST)
        self.bill = bill


class PrepaidContract(Contract):
    start: datetime.datetime
    bill: Optional[Bill]
    balance: int

    def __init__(self, start: datetime.date, balance: int) -> None:
        Contract.__init__(self, start)
        self.balance = -1 * balance

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        # the initial amount of money is added to bill
        if self.start.month == month and self.start.year == year:
            bill.add_fixed_cost(self.balance)
        else:
            bill.add_fixed_cost(self.balance)

        # if the initial balance deposit or the balance is less than 10, add 25
        if self.balance >= -10:
            self.balance += -25

        bill.set_rates("PREPAID", PREPAID_MINS_COST)
        self.bill = bill

    def cancel_contract(self) -> float:
        self.start = None
        if self.balance >= 0:
            self.bill.add_fixed_cost(self.balance)
        return self.bill.get_cost()


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'datetime', 'bill', 'call', 'math'
        ],
        'disable': ['R0902', 'R0913'],
        'generated-members': 'pygame.*'
    })
