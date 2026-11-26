"""Compare recursive and iterative preorder traversal."""

from dataclasses import dataclass


@dataclass
class Node:
    value: int
    left: "Node | None" = None
    right: "Node | None" = None


def preorder(node):
    if node is not None:
        yield node.value
        yield from preorder(node.left)
        yield from preorder(node.right)


def preorder_iterative(root):
    stack = [root] if root is not None else []
    while stack:
        node = stack.pop()
        yield node.value
        if node.right is not None:
            stack.append(node.right)
        if node.left is not None:
            stack.append(node.left)


if __name__ == "__main__":
    tree = Node(1, Node(2, Node(4), Node(5, Node(8))), Node(3, Node(6, None, Node(9)), Node(7)))
    print("Recursive:", *preorder(tree))
    print("Iterative:", *preorder_iterative(tree))
