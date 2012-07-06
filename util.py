# check if list2 is suffix of list1
def is_suffix(list1, list2):
    if len(list2) > len(list1):
        return False
    for (n2, n1) in zip(reversed(list2), reversed(list1)):
        if n2 != n1:
            return False
    return True

