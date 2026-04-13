from call import Call


class CallHistory:
    incoming_calls: dict[tuple[int, int], list[Call]]
    outgoing_calls: dict[tuple[int, int], list[Call]]

    def __init__(self) -> None:
        self.outgoing_calls = {}
        self.incoming_calls = {}

    def register_outgoing_call(self, call: Call) -> None:
        date = (call.time.month, call.time.year)
        if date not in self.outgoing_calls:
            self.outgoing_calls[date] = [call]
        else:
            self.outgoing_calls[date].append(call)

    def register_incoming_call(self, call: Call) -> None:
        date = (call.time.month, call.time.year)
        if date not in self.incoming_calls:
            self.incoming_calls[date] = [call]
        else:
            self.incoming_calls[date].append(call)

    def get_monthly_history(self, month: int = None, year: int = None) -> \
            tuple[list[Call], list[Call]]:
        monthly_history = ([], [])
        if month is not None and year is not None:
            if (month, year) in self.outgoing_calls:
                for call in self.outgoing_calls[(month, year)]:
                    monthly_history[0].append(call)

            if (month, year) in self.incoming_calls:
                for call in self.incoming_calls[(month, year)]:
                    monthly_history[1].append(call)
        else:
            for entry in self.outgoing_calls:
                for call in self.outgoing_calls[entry]:
                    monthly_history[0].append(call)
            for entry in self.incoming_calls:
                for call in self.incoming_calls[entry]:
                    monthly_history[1].append(call)
        return monthly_history


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'datetime', 'call'
            ''
        ],
        'disable': ['R0902', 'R0913'],
        'generated-members': 'pygame.*'
    })
