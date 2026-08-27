import csv
from typing import List, Dict
from tm_trees import TMTree

# Filename for the dataset
DATA_FILE = '../../../cs1_papers.csv'


class PaperTree(TMTree):
    _authors: str
    _doi: str

    def __init__(self, name: str, subtrees: List[TMTree], authors: str = '',
                 doi: str = '', citations: int = 0, by_year: bool = True,
                 all_papers: bool = False) -> None:
        self._doi = doi
        self._authors = authors

        if all_papers:
            if by_year:
                temp_dict = _load_papers_to_dict(by_year)
                temp_subtrees = _build_tree_from_dict(temp_dict)
                TMTree.__init__(self, name, temp_subtrees, citations)

            else:
                temp_dict = _build_tree_from_dict(False)
                TMTree.__init__(self, name, temp_dict, citations)

        else:
            TMTree.__init__(self, name, subtrees, citations)

    def get_separator(self) -> str:
        return ':'

    def get_suffix(self) -> str:
        if not self._subtrees:
            return ' (Paper)'

        else:
            return ' (Category)'


def _load_papers_to_dict(by_year: bool = True) -> Dict:
    result = {}

    with open(DATA_FILE, 'r') as data:
        data.readline()
        file = csv.reader(data)

        for row in file:
            authors, name, year, temp_categories, doi, citations = row
            categories = temp_categories.split(':')

            if by_year:
                categories.insert(0, year)

            working_dict = result
            for category in categories:
                # the line below was if category in working_dict.keys():
                if category in working_dict:
                    working_dict = working_dict[category]
                else:
                    working_dict[category] = {}
                    working_dict = working_dict[category]

            working_dict[name] = {}
            working_dict = working_dict[name]

            working_dict['authors'] = authors
            working_dict['name'] = name
            working_dict['doi'] = doi
            working_dict['citations'] = int(citations)

    return result


def _build_tree_from_dict(nested_dict: Dict) -> List[PaperTree]:
    ans = []
    if nested_dict == {}:
        return ans

    elif 'authors' in nested_dict.keys():
        ans.append(PaperTree(nested_dict['name'], [], nested_dict['authors'],
                             nested_dict['doi'], nested_dict['citations']))

    else:
        for name, yep in nested_dict.items():
            ans.append(PaperTree(name, _build_tree_from_dict(yep)))

    return ans


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': ['python_ta', 'typing', 'csv', 'tm_trees'],
        'allowed-io': ['_load_papers_to_dict'],
        'max-args': 8
    })
