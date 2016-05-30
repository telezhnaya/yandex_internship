import pytest


class Node:
    id = 0

    def __init__(self, value, father=None):
        self.value = value  # numerical
        self.father = father  # Node
        self.sons = []
        self.height = 0 if not father else father.height + 1
        self.id = Node.id
        Node.id += 1

        if father:
            father.sons.append(self)

    def __hash__(self):
        return self.id.__hash__()

    def __eq__(self, other):
        return self.id == other.id


def search(son1, son2):
    while son1.height > son2.height:
        son1 = son1.father
    while son2.height > son1.height:
        son2 = son2.father
    while son1 != son2:
        son1 = son1.father
        son2 = son2.father
    return son1


# def dfs(root, cur_height=0):
#     for son in root.sons:
#         dfs(son, cur_height + 1)


root = Node(4)

l11 = Node(3, root)
l12 = Node(5, root)

l21 = Node(11, l11)
l22 = Node(7, l11)

l23 = Node(5, l12)
l24 = Node(8, l12)
l25 = Node(11, l12)


@pytest.mark.parametrize("son1, son2, result", [
    (l21, l23, root),
    (l11, l22, l11)])
def test_lca(son1, son2, result):
    assert search(son1, son2) == result

# yurakura@yandex-team.ru
