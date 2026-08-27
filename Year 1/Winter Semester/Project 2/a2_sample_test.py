import os

from hypothesis import given
from hypothesis.strategies import integers

from tm_trees import TMTree, FileSystemTree
from papers import PaperTree

EXAMPLE_PATH = os.path.join(os.getcwd(), '../../../example-directory', 'workshop')

delete = True # must be False when submitting to CodeTierList

def remove_directory_contents(directory):
    """Recursively removes all contents of a directory."""
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            remove_directory_contents(item_path)
            os.rmdir(item_path)


# test FileSystemTree - task 1
# test FileSystemTree - task 1
# test FileSystemTree - task 1
# test FileSystemTree - task 1
# test FileSystemTree - task 1
# test FileSystemTree - task 1
# test FileSystemTree - task 1
# test FileSystemTree - task 1
# test FileSystemTree - task 1
# test FileSystemTree - task 1
# test FileSystemTree - task 1
# test FileSystemTree - task 1
# test FileSystemTree - task 1
# test FileSystemTree - task 1
# test FileSystemTree - task 1


def test_single_file() -> None:
    tree = FileSystemTree(os.path.join(EXAMPLE_PATH, 'draft.pptx'))
    assert tree._name == 'draft.pptx'
    assert tree._subtrees == []
    assert tree._parent_tree is None
    assert tree.data_size == 58
    assert is_valid_colour(tree._colour)
    assert not tree.is_empty()
    assert tree.data_size == os.path.getsize(os.path.join(EXAMPLE_PATH, 'draft.pptx'))
    assert tree.get_parent() is None


def test_tm_tree_init():
    tree = TMTree(name="test", subtrees=[], data_size=100)
    assert not tree.is_empty()
    assert tree.data_size == 100
    assert tree.get_parent() is None


def test_tm_tree_empty_init():
    tree = TMTree(name=None, subtrees=[], data_size=0)
    assert tree.is_empty()
    assert tree.data_size == 0
    assert tree._subtrees == []
    # assert tree.get_parent() is None


def test_example_data() -> None:
    tree = FileSystemTree(EXAMPLE_PATH)
    assert tree._name == 'workshop'
    assert tree._parent_tree is None
    assert tree.data_size == 151
    assert is_valid_colour(tree._colour)
    assert len(tree._subtrees) == 3
    for subtree in tree._subtrees:
        # Note the use of is rather than ==.
        # This checks ids rather than values.
        assert subtree._parent_tree is tree
    assert all(isinstance(sub, FileSystemTree) for sub in tree._subtrees)
    assert all(sub.data_size >= 0 for sub in tree._subtrees)


def test_empty_folderinside() -> None:
    empty_folder_path = os.path.join(EXAMPLE_PATH, 'empty folder')
    os.mkdir(empty_folder_path)
    empty_tree = FileSystemTree(empty_folder_path)

    assert empty_tree._name == 'empty folder'
    assert empty_tree.data_size == 0
    assert len(empty_tree._subtrees) == 0
    assert empty_tree._parent_tree is None

    if delete:
        os.rmdir(empty_folder_path)


def test_invalid_path() -> None:
    try:
        FileSystemTree(os.path.join(EXAMPLE_PATH, 'InVaLiD fOlDeR'))

    except FileNotFoundError:
        assert True

    else:
        assert False

# empty folder testing section

def test_single_empty_folder() -> None:
    test_dir = 'test_directory'
    os.mkdir(test_dir)
    empty_folder_path = os.path.join(test_dir, 'empty_folder')
    os.mkdir(empty_folder_path)
    tree = FileSystemTree(test_dir)

    assert tree._name == 'test_directory'
    assert tree.data_size == 0
    assert len(tree._subtrees) == 1
    assert tree._subtrees[0]._name == 'empty_folder'
    assert tree._subtrees[0].data_size == 0
    assert tree._parent_tree is None

    if delete:
        remove_directory_contents('test_directory')
        os.rmdir('test_directory')


def test_empty_folder() -> None:
    test_dir = 'test_directory1'
    os.mkdir(test_dir)
    tree = FileSystemTree(test_dir)

    assert tree._name == 'test_directory1'
    assert tree.data_size == 0
    assert len(tree._subtrees) == 0
    assert tree._parent_tree is None

    if delete:
        os.rmdir('test_directory1')


def test_double_empty_folder() -> None:
    test_dir = 'test_directory2'
    os.mkdir(test_dir)

    empty_folder_path = os.path.join(test_dir, 'empty_folder')
    os.mkdir(empty_folder_path)

    empty_folder_path2 = os.path.join(test_dir, 'empty_folder2')
    os.mkdir(empty_folder_path2)

    tree = FileSystemTree(test_dir)

    assert tree._name == 'test_directory2'
    assert tree.data_size == 0
    assert len(tree._subtrees) == 2
    assert tree._subtrees[0]._name == 'empty_folder'
    assert tree._subtrees[0].data_size == 0
    assert tree._subtrees[1]._name == 'empty_folder2'
    assert tree._subtrees[1].data_size == 0
    assert tree._parent_tree is None

    if delete:
        remove_directory_contents('test_directory2')
        os.rmdir('test_directory2')


def test_empty_folder_inception() -> None:
    test_dir = 'test_directory3'
    os.mkdir(test_dir)

    empty_folder_path = os.path.join(test_dir, 'empty_folder')
    os.mkdir(empty_folder_path)

    empty_folder_path2 = os.path.join(empty_folder_path, 'empty_folder2')
    os.mkdir(empty_folder_path2)

    tree = FileSystemTree(test_dir)

    assert tree._name == 'test_directory3'
    assert tree.data_size == 0
    assert tree._subtrees[0]._name == 'empty_folder'
    assert tree._subtrees[0].data_size == 0
    assert tree._parent_tree is None

    # assert os.path.getsize(os.path.join(os.getcwd(), tree._name)) == 4096

    if delete:
        remove_directory_contents('test_directory3')
        os.rmdir('test_directory3')

# file testing section

def test_file() -> None:
    with open('test_text', 'w') as f:
        f.write('hewwo')
    tree = FileSystemTree('test_text')
    file_size = os.path.getsize('test_text')

    assert tree._name == 'test_text'
    assert len(tree._subtrees) == 0
    assert file_size == 5
    assert tree._subtrees == []
    assert tree._parent_tree is None
    assert tree.data_size == 5
    assert is_valid_colour(tree._colour)

    if delete:
        os.remove('test_text')


def test_0_size_file() -> None:
    with open('size_zero', 'w') as f:
        f.write('')
    tree = FileSystemTree('size_zero')
    file_size = os.path.getsize('size_zero')
    
    assert tree._name == 'size_zero'
    assert len(tree._subtrees) == 0
    assert file_size == 0
    assert tree._subtrees == []
    assert tree._parent_tree is None
    assert tree.data_size == 0
    assert is_valid_colour(tree._colour)

    if delete:
        os.remove('size_zero')


def test_hidden_file() -> None:
    with open('.hidden_text', 'w') as f:
        f.write('hewwo1')
    tree = FileSystemTree('.hidden_text')
    file_size = os.path.getsize('.hidden_text')

    assert tree._name == '.hidden_text'
    assert len(tree._subtrees) == 0
    assert file_size == 6
    assert tree._subtrees == []
    assert tree._parent_tree is None
    assert tree.data_size == 6
    assert is_valid_colour(tree._colour)

    if delete:
        os.remove('.hidden_text')


# test task 2
# test task 2
# test task 2
# test task 2
# test task 2
# test task 2
# test task 2
# test task 2
# test task 2
# test task 2
# test task 2
# test task 2
# test task 2
# test task 2
# test task 2
# test task 2
# test task 2
# test task 2


@given(integers(min_value=100, max_value=1000),
       integers(min_value=100, max_value=1000),
       integers(min_value=100, max_value=1000),
       integers(min_value=100, max_value=1000))
def test_single_file_rectangles(x, y, width, height) -> None:
    tree = FileSystemTree(os.path.join(EXAMPLE_PATH, 'draft.pptx'))
    tree.update_rectangles((x, y, width, height))
    rects = tree.get_rectangles()

    # This should be just a single rectangle and colour returned.
    assert len(rects) == 1
    rect, colour = rects[0]
    assert rect == (x, y, width, height)
    assert is_valid_colour(colour)

def test_example_example() -> None:
    tree1 = TMTree("name1", subtrees=[], data_size=10)
    tree2 = TMTree("name2", subtrees=[], data_size=25)
    tree3 = TMTree("name3", subtrees=[], data_size=15)
    tree = TMTree("tree", subtrees=[tree1, tree2, tree3], data_size=0)
    _sort_subtrees(tree)
    tree.expand_all()

    rect = (0, 0, 200, 100)
    tree.update_rectangles(rect)
    rects = tree.get_rectangles()
    assert len(rects) == 3
    actual_rects = [r[0] for r in rects]
    expected_rects = [(0, 0, 40, 100), (40, 0, 100, 100), (140, 0, 60, 100)]

    assert len(actual_rects) == len(expected_rects)
    for i in range(len(actual_rects)):
        assert expected_rects[i] == actual_rects[i]


def test_activities_folder() -> None:
    tree = FileSystemTree(os.path.join(EXAMPLE_PATH, 'activities'))
    _sort_subtrees(tree)
    tree.expand_all()

    rect = (0, 0, 200, 100)
    
    tree.update_rectangles(rect)
    rectangles = tree.get_rectangles()
    assert len(rectangles) == 3
    actual_rects = [r[0] for r in rectangles]
    expected_rects = [(0, 0, 5, 100), (5, 0, 56, 100), (61, 0, 139, 100)]

    assert len(actual_rects) == len(expected_rects)
    for i in range(len(actual_rects)):
        assert expected_rects[i] == actual_rects[i]


def test_rect_one_large_other_small() -> None:
    subtree2 = TMTree("subtree1", [], 995)
    subtree5 = TMTree("subtree5", [], 5)
    subtree3 = TMTree("subtree3", [subtree5], 0)
    subtree1 = TMTree("subtree2", [subtree3], 0)
    tree = TMTree("root", [subtree1, subtree2], data_size=0)
    _sort_subtrees(tree)
    tree.expand_all()

    rect = (0, 0, 100, 100)

    tree.update_rectangles(rect)
    rects = tree.get_rectangles()

    assert len(rects) == 2
    actual_rects = [r[0] for r in rects]
    expected_rects = [(0, 0, 100, 99), (0, 99, 100, 1)]

    assert len(actual_rects) == len(expected_rects)
    for i in range(len(actual_rects)):
        assert expected_rects[i] == actual_rects[i]


def test_rect_single_leaf_0_size() -> None:
    tree = TMTree('test1', subtrees=[], data_size=0)
    _sort_subtrees(tree)
    tree.expand_all()

    rect = (0, 0, 200, 100)

    tree.update_rectangles(rect)
    rects = tree.get_rectangles()

    assert len(rects) == 0
    actual_rects = [r[0] for r in rects]
    expected_rects = []

    assert len(actual_rects) == len(expected_rects)
    for i in range(len(actual_rects)):
        assert expected_rects[i] == actual_rects[i]


def test_rect_tree_all_0_size() -> None:
    subtree10 = TMTree("subtree10", [], 0)
    subtree6 = TMTree("subtree6", [], 0)
    subtree7 = TMTree("subtree7", [subtree6], 0)
    subtree8 = TMTree("subtree8", [subtree7], 0)
    subtree9 = TMTree("subtree9", [subtree8], 0)
    subtree1 = TMTree("subtree1", [subtree10, subtree9], 0)
    subtree4 = TMTree("subtree4", [], 0)
    subtree5 = TMTree("subtree5", [], 0)
    subtree3 = TMTree("subtree3", [subtree5], 0)
    subtree2 = TMTree("subtree2", [subtree3, subtree4], 0)
    tree = TMTree("root", [subtree1, subtree2], data_size=0)
    _sort_subtrees(tree)
    tree.expand_all()

    rect = (0, 0, 200, 100)

    tree.update_rectangles(rect)
    rects = tree.get_rectangles()

    assert len(rects) == 0
    actual_rects = [r[0] for r in rects]
    expected_rects = []

    assert len(actual_rects) == len(expected_rects)
    for i in range(len(actual_rects)):
        assert expected_rects[i] == actual_rects[i]


def test_example_data_rectangles() -> None:
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)

    tree.expand_all()
    tree.update_rectangles((0, 0, 200, 100))
    rects = tree.get_rectangles()
    assert len(rects) == 6

    actual_rects = [r[0] for r in rects]
    expected_rects = [(0, 0, 94, 2), (0, 2, 94, 28), (0, 30, 94, 70),
                      (94, 0, 76, 100), (170, 0, 30, 72), (170, 72, 30, 28)]

    assert len(actual_rects) == len(expected_rects)
    for i in range(len(actual_rects)):
        assert expected_rects[i] == actual_rects[i]


# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing
# task 4 testing

# testing update_data_sizes()

def test_update_data_on_single_leaf() -> None:
    tree = TMTree(name="test", subtrees=[], data_size=100)
    assert tree.update_data_sizes() == 100
    assert tree._name == "test"
    assert tree.data_size == 100


def test_update_data_with_subtrees() -> None:
    subtree1 = TMTree("subtree1", [], 50)
    subtree2 = TMTree("subtree2", [], 70)
    tree = TMTree("root", [subtree1, subtree2], data_size=0)
    assert tree.update_data_sizes() == 120
    assert tree.data_size == 120


def test_update_data_on_empty_tree() -> None:
    tree = TMTree(name=None, subtrees=[], data_size=0)
    assert tree.update_data_sizes() == 0
    assert tree.data_size == 0


def test_update_data_on_unbalanced_tree() -> None:
    subtree10 = TMTree("subtree10", [], 50)
    subtree6 = TMTree("subtree6", [], 170)
    subtree7 = TMTree("subtree7", [subtree6], 0)
    subtree8 = TMTree("subtree8", [subtree7], 0)
    subtree9 = TMTree("subtree9", [subtree8], 0)
    subtree1 = TMTree("subtree1", [subtree10, subtree9], 0)
    subtree4 = TMTree("subtree4", [], 436)
    subtree5 = TMTree("subtree5", [], 10)
    subtree3 = TMTree("subtree3", [subtree5], 0)
    subtree2 = TMTree("subtree2", [subtree3, subtree4], 0)
    tree = TMTree("root", [subtree1, subtree2], data_size=0)
    assert tree.update_data_sizes() == 666
    assert tree.data_size == 666


def test_update_data_on_very_large_sizes() -> None:
    subtree1 = TMTree("subtree1", [], 18446744073109551615)
    subtree2 = TMTree("subtree2", [], 700000000)
    tree = TMTree("root", [subtree1, subtree2], data_size=0)
    assert tree.update_data_sizes() == 18446744073809551615
    assert tree.data_size == 18446744073809551615

# testing move()

def test_move_single_leaf_folder() -> None:
    subtree1 = TMTree('test2', subtrees=[], data_size=50)
    subtree2 = TMTree('test3', subtrees=[], data_size=50)
    tree = TMTree('test1', subtrees=[subtree1], data_size=0)
    tree2 = TMTree('test4', subtrees=[subtree2], data_size=0)

    tree2.expand()
    subtree2.move(tree)

    assert tree.data_size == 100
    assert tree2._subtrees == []
    assert tree._subtrees == [subtree1, subtree2]
    assert tree2.data_size == 0


def test_move_two_leaves() -> None:
    subtree1 = TMTree('test2', subtrees=[], data_size=50)
    subtree2 = TMTree('test3', subtrees=[], data_size=50)

    subtree1.expand()
    subtree2.expand()
    subtree2.move(subtree1)

    assert subtree1.data_size == 50
    assert subtree2.data_size == 50
    assert subtree1._subtrees == []
    assert subtree2._subtrees == []


def test_multiple_moves() -> None:
    subtree10 = TMTree("subtree10", [], 50)
    subtree6 = TMTree("subtree6", [], 170)
    subtree7 = TMTree("subtree7", [subtree6], 0)
    subtree8 = TMTree("subtree8", [subtree7], 0)
    subtree9 = TMTree("subtree9", [subtree8], 0)
    subtree1 = TMTree("subtree1", [subtree10, subtree9], 0)
    subtree4 = TMTree("subtree4", [], 436)
    subtree5 = TMTree("subtree5", [], 10)
    subtree3 = TMTree("subtree3", [subtree5], 0)
    subtree2 = TMTree("subtree2", [subtree3, subtree4], 0)
    tree = TMTree("root", [subtree1, subtree2], data_size=0)

    tree.expand()
    subtree6.move(subtree3)
    tree.update_data_sizes()

    assert len(subtree3._subtrees) == 2

    subtree4.move(tree)
    tree.update_data_sizes()

    assert len(tree._subtrees) == 3

    subtree3.move(tree)
    tree.update_data_sizes()

    assert len(tree._subtrees) == 3

# testing change_size()

def test_change_size():
    subtree1 = TMTree('test10', subtrees=[], data_size=50)
    subtree2 = TMTree('test11', subtrees=[], data_size=50)

    tree = TMTree('test', subtrees=[], data_size=500)
    tree2 = TMTree('test2', subtrees=[], data_size=10)
    tree3 = TMTree('test3', subtrees=[], data_size=0)
    tree4 = TMTree('test4', subtrees=[], data_size=1)
    tree5 = TMTree('test5', subtrees=[subtree1, subtree2], data_size=0)

    tree.expand()
    tree2.expand()
    tree3.expand()
    tree4.expand()
    tree5.expand()

    tree.change_size(0.01)
    tree.update_data_sizes()
    assert tree.data_size == 505
    tree.change_size(-0.01)
    tree.update_data_sizes()
    assert tree.data_size == 499
    tree.change_size(-0.01)
    tree.update_data_sizes()
    assert tree.data_size == 494

    tree2.change_size(0.01)
    tree2.update_data_sizes()
    assert tree2.data_size == 11
    tree2.change_size(-0.01)
    tree2.update_data_sizes()
    assert tree2.data_size == 10
    tree2.change_size(-0.01)
    tree2.update_data_sizes()
    assert tree2.data_size == 9

    tree3.change_size(0.01)
    tree3.update_data_sizes()
    assert tree3.data_size == 0
    tree3.change_size(-0.01)
    tree3.update_data_sizes()
    assert tree3.data_size == 0
    tree3.change_size(-0.01)
    tree3.update_data_sizes()
    assert tree3.data_size == 0

    tree4.change_size(0.01)
    tree4.update_data_sizes()
    assert tree4.data_size == 2
    tree4.change_size(-0.01)
    tree4.update_data_sizes()
    assert tree4.data_size == 1
    tree4.change_size(-0.01)
    tree4.update_data_sizes()
    assert tree4.data_size == 1

    tree5.change_size(0.01)
    tree5.update_data_sizes()
    assert tree5.data_size == 100
    tree5.change_size(-0.01)
    tree5.update_data_sizes()
    assert tree5.data_size == 100
    tree5.change_size(-0.01)
    tree5.update_data_sizes()
    assert tree5.data_size == 100


# testing delete_self()

def test_delete_regular_node() -> None:
    subtree1 = TMTree('test10', subtrees=[], data_size=50)
    subtree2 = TMTree('test11', subtrees=[], data_size=50)
    tree = TMTree('test5', subtrees=[subtree1, subtree2], data_size=0)

    tree.expand()
    subtree1.delete_self()
    tree.update_data_sizes()

    assert tree.data_size == 50
    assert len(tree._subtrees) == 1
    
    subtree2.delete_self()
    tree.update_data_sizes()

    assert tree.data_size == 0
    assert len(tree._subtrees) == 0


def test_delete_folder() -> None:
    subtree3 = TMTree('test1', subtrees=[], data_size=50)
    subtree1 = TMTree('test10', subtrees=[subtree3], data_size=0)
    subtree2 = TMTree('test11', subtrees=[], data_size=50)
    tree = TMTree('test5', subtrees=[subtree1, subtree2], data_size=0)

    tree.expand()
    subtree1.delete_self()
    tree.update_data_sizes()

    assert tree.data_size == 50
    assert len(tree._subtrees) == 1


def test_delete_root_folder() -> None:
    subtree1 = TMTree('test10', subtrees=[], data_size=50)
    subtree2 = TMTree('test11', subtrees=[], data_size=50)
    tree = TMTree('test5', subtrees=[subtree1, subtree2], data_size=0)

    tree.delete_self()
    tree.update_data_sizes()

    assert tree.data_size == 100
    assert len(tree._subtrees) == 2

# testing expand() and expand_all()

def test_expand_tree() -> None:
    subtree1 = TMTree('test10', subtrees=[], data_size=50)
    subtree2 = TMTree('test11', subtrees=[], data_size=50)
    tree = TMTree('test5', subtrees=[subtree1, subtree2], data_size=0)

    tree.expand()

    assert tree._expanded == True
    assert subtree1._expanded == False
    assert subtree2._expanded == False


def test_expand_leaf() -> None:
    subtree1 = TMTree('test10', subtrees=[], data_size=50)

    subtree1.expand()

    assert subtree1._expanded == False


def test_expand_all_tree() -> None:
    subtree1 = TMTree('test10', subtrees=[], data_size=50)
    subtree2 = TMTree('test11', subtrees=[], data_size=50)
    tree = TMTree('test5', subtrees=[subtree1, subtree2], data_size=0)
    
    tree.expand_all()

    assert tree._expanded == True
    assert subtree1._expanded == False
    assert subtree2._expanded == False


def test_expand_all_leaf() -> None:
    subtree1 = TMTree('test10', subtrees=[], data_size=50)

    subtree1.expand_all()

    assert subtree1._expanded == False


def test_expand_all_bigger_tree() -> None:
    subtree10 = TMTree("subtree10", [], 50)
    subtree6 = TMTree("subtree6", [], 170)
    subtree7 = TMTree("subtree7", [subtree6], 0)
    subtree8 = TMTree("subtree8", [subtree7], 0)
    subtree9 = TMTree("subtree9", [subtree8], 0)
    subtree1 = TMTree("subtree1", [subtree10, subtree9], 0)
    subtree4 = TMTree("subtree4", [], 436)
    subtree5 = TMTree("subtree5", [], 10)
    subtree3 = TMTree("subtree3", [subtree5], 0)
    subtree2 = TMTree("subtree2", [subtree3, subtree4], 0)
    tree = TMTree("root", [subtree1, subtree2], data_size=0)

    tree.expand_all()
    
    assert tree._expanded == True
    assert subtree1._expanded == True
    assert subtree2._expanded == True
    assert subtree3._expanded == True
    assert subtree4._expanded == False
    assert subtree5._expanded == False
    assert subtree6._expanded == False
    assert subtree7._expanded == True
    assert subtree8._expanded == True
    assert subtree9._expanded == True
    assert subtree10._expanded == False

# testing collapse() and collapse_all()

def test_collapse_tree() -> None:
    subtree1 = TMTree('test10', subtrees=[], data_size=50)
    subtree2 = TMTree('test11', subtrees=[], data_size=50)
    tree = TMTree('test5', subtrees=[subtree1, subtree2], data_size=0)

    tree.expand()
    tree.collapse()

    assert tree._expanded == False
    assert subtree1._expanded == False
    assert subtree2._expanded == False


def test_collapse_leaf() -> None:
    subtree1 = TMTree('test10', subtrees=[], data_size=50)

    subtree1.expand()
    subtree1.collapse()

    assert subtree1._expanded == False


def test_collapse_all_tree() -> None:
    subtree1 = TMTree('test10', subtrees=[], data_size=50)
    subtree2 = TMTree('test11', subtrees=[], data_size=50)
    tree = TMTree('test5', subtrees=[subtree1, subtree2], data_size=0)
    
    tree.expand_all()
    tree.collapse_all()

    assert tree._expanded == False
    assert subtree1._expanded == False
    assert subtree2._expanded == False


def test_collapse_all_leaf() -> None:
    subtree1 = TMTree('test10', subtrees=[], data_size=50)

    subtree1.expand_all()
    subtree1.collapse_all()

    assert subtree1._expanded == False


def test_collapse_all_bigger_tree() -> None:
    subtree10 = TMTree("subtree10", [], 50)
    subtree6 = TMTree("subtree6", [], 170)
    subtree7 = TMTree("subtree7", [subtree6], 0)
    subtree8 = TMTree("subtree8", [subtree7], 0)
    subtree9 = TMTree("subtree9", [subtree8], 0)
    subtree1 = TMTree("subtree1", [subtree10, subtree9], 0)
    subtree4 = TMTree("subtree4", [], 436)
    subtree5 = TMTree("subtree5", [], 10)
    subtree3 = TMTree("subtree3", [subtree5], 0)
    subtree2 = TMTree("subtree2", [subtree3, subtree4], 0)
    tree = TMTree("root", [subtree1, subtree2], data_size=0)

    tree.expand_all()
    tree.collapse_all()
    
    assert tree._expanded == False
    assert subtree1._expanded == False
    assert subtree2._expanded == False
    assert subtree3._expanded == False
    assert subtree4._expanded == False
    assert subtree5._expanded == False
    assert subtree6._expanded == False
    assert subtree7._expanded == False
    assert subtree8._expanded == False
    assert subtree9._expanded == False
    assert subtree10._expanded == False


# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py
# testing Papers.py

def test_papers_regular_init() -> None:
    papertree = PaperTree('test', subtrees=[], authors='testauthor', doi='http://doi.acm.org/10.1145/800010.808068,3', citations=5, by_year=True, all_papers=True)

    assert len(papertree._subtrees) == 45
    assert papertree._name == 'test'
    assert papertree._doi == 'http://doi.acm.org/10.1145/800010.808068,3'
    assert papertree._authors == 'testauthor'


##############################################################################
# Helpers
##############################################################################


def is_valid_colour(colour: tuple[int, int, int]) -> bool:
    for i in range(3):
        if not 0 <= colour[i] <= 255:
            return False
    return True


def _sort_subtrees(tree: TMTree) -> None:
    if not tree.is_empty():
        for subtree in tree._subtrees:
            _sort_subtrees(subtree)

        tree._subtrees.sort(key=lambda t: t._name)


if __name__ == '__main__':
    import pytest

    pytest.main(['a2_sample_test.py'])
