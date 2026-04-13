from call import Call
from customer import Customer


class Filter:
    def __init__(self) -> None:
        pass

    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError


class ResetFilter(Filter):
    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        filtered_calls = []
        for c in customers:
            customer_history = c.get_history()
            # only take outgoing calls, we don't want to include calls twice
            filtered_calls.extend(customer_history[0])
        return filtered_calls

    def __str__(self) -> str:
        return "Reset all of the filters applied so far, if any"


class CustomerFilter(Filter):
    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        filtered_calls = []

        try:
            customer_id = int(filter_string)
            for customer in customers:
                if customer.get_id() == customer_id:
                    phonelines = customer.get_phone_numbers()
                    break
            # catches customer id mismatch
            else:
                return data

            # check for non-empty phoneline
            if phonelines:
                for call in data:
                    if call.src_number in phonelines:
                        filtered_calls.append(call)
                    elif call.dst_number in phonelines:
                        filtered_calls.append(call)
                return filtered_calls

        except (IndexError, ValueError):
            return data

        return data

    def __str__(self) -> str:
        return "Filter events based on customer ID"


class DurationFilter(Filter):
    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        filtered_calls = set()

        try:

            filter_type = filter_string[0]
            duration_filter = int(filter_string[1:])

            if filter_type not in ('L', 'G'):
                for call in data:
                    if call.duration:
                        filtered_calls.add(call)

            if filter_type == 'L':
                for call in data:
                    if call.duration < duration_filter:
                        filtered_calls.add(call)

            else:
                for call in data:
                    if call.duration > duration_filter:
                        filtered_calls.add(call)

            return filtered_calls

        except (IndexError, ValueError):
            return data

    def __str__(self) -> str:
        return "Filter calls based on duration; " \
               "L### returns calls less than specified length, G### for greater"


class LocationFilter(Filter):
    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        filtered_calls = []

        try:
            lower_long, lower_lat, \
                upper_long, upper_lat = filter_string.split(', ')

            lower_long, lower_lat = float(lower_long), float(lower_lat)
            upper_long, upper_lat = float(upper_long), float(upper_lat)

            for call in data:
                src_long, src_lat = call.src_loc
                dst_long, dst_lat = call.dst_loc

                if (lower_long <= src_long <= upper_long) and \
                        (lower_lat <= src_lat <= upper_lat):
                    filtered_calls.append(call)

                elif (lower_long <= dst_long <= upper_long) and \
                        (lower_lat <= dst_lat <= upper_lat):
                    filtered_calls.append(call)

            return filtered_calls

        except (IndexError, ValueError):
            return data

    def __str__(self) -> str:
        return "Filter calls made or received in a given rectangular area. " \
               "Format: \"lowerLong, lowerLat, " \
               "upperLong, upperLat\" (e.g., -79.6, 43.6, -79.3, 43.7)"


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'time', 'datetime', 'call', 'customer'
        ],
        'max-nested-blocks': 4,
        'allowed-io': ['apply', '__str__'],
        'disable': ['W0611', 'W0703'],
        'generated-members': 'pygame.*'
    })
