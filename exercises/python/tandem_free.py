"""Generate a toy string over ABCD with no adjacent repeated blocks."""

import argparse
from random import Random


def generate(length, seed=None):
    if length < 0:
        raise ValueError("length must be nonnegative")

    random = Random(seed)
    result = []
    while len(result) < length:
        result.append(random.choice("ABCD"))
        # A new repeated block can only end at the new character.
        for width in range(1, len(result) // 2 + 1):
            if result[-width:] == result[-2 * width:-width]:
                del result[-width:]
                break
    return "".join(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("length", type=int)
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()

    if args.length < 0:
        parser.error("length must be nonnegative")
    print(generate(args.length, args.seed))


if __name__ == "__main__":
    main()
