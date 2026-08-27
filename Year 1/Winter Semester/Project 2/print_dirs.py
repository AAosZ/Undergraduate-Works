import os


def print_items(d: str, indentation: str) -> None:
    print(indentation + d + ':')
    for filename in os.listdir(d):
        print(indentation + filename)
        subitem = os.path.join(d, filename)
        if os.path.isdir(subitem):
            print_items(subitem, indentation + ' -> ')


if __name__ == '__main__':
    # Put in a path like
    # 'C:\\Users\\user\\Documents\\csc148\\assignments' (Windows) or
    # '/Users/user/Documents/courses/csc148/assignments' (OSX)
    # to print the contents of that folder.
    PATH_TO_PRINT = ''  # enter the path to print here
    print_items(PATH_TO_PRINT or os.getcwd(), '')
