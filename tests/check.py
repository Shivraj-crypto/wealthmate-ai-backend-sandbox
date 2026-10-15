


def cardsway(cards):

    max_cards_needed = float('inf')

    for i in range(2, max(cards) + 2):

        extra_cards_needed = 0

        for card in cards:

            while card % i != 0:
                card += 1
                extra_cards_needed += 1

        max_cards_needed = min(max_cards_needed, extra_cards_needed)

    return max_cards_needed



print(cardsway([4,7,5,11,15]))