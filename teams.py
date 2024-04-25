def transpose(array):
    return [[array[j][i] for j in range(0, len(array))] for i in range(0, len(array))]

# Exiles Prime vs Exiles Alpha
# Column 0: Tom, Stormcast
# Column 1: Jasper, OBR
# Column 2: Steve, Soulblight
# Column 3: Brad, Gitz
payoffs = [
    # Row 0: Miles, Cities
    [-1, 1, 1, 2],
    # Row 1: Louis, Sylvaneth
    [-2, -2, -2, 5],
    # Row 2: Luis, STD
    [-2, -2, -2, 5],
    # Row 3: Michael, Big Waaagh
    [1, 1, 1, 1]
]
# payoffs = transpose(payoffs)

def matchup_payoff(matches: [(int, int)]) -> int:
    return sum(payoffs[p1][p2] for (p1, p2) in matches)

def choose1(players) -> [(int, [int])]:
    results = []
    for player in players:
        remaining = players.copy()
        remaining.remove(player)
        results.append((player, remaining))
    return results

# Sixth last step: p2 selects p2's first defender
def max_p1_choose_p1_defender(p1_remaining, p2_remaining, min_f=min) -> ([(int, int)], int):
    options = [
        min_p2_choose_p2_defender(p1_d1, p1_remaining2, p2_remaining, min_f)
        for (p1_d1, p1_remaining2) in choose1(p1_remaining)
    ]
    return max(options, key=lambda x: x[1])

# Fifth last step: p2 selects p2's first defender
def min_p2_choose_p2_defender(p1_d1, p1_remaining, p2_remaining, min_f=min) -> ([(int, int)], int):
    options = [
        max_p1_choose_p1_attackers(p1_d1, p1_remaining, p2_d1, p2_remaining2, min_f)
        for (p2_d1, p2_remaining2) in choose1(p2_remaining)
    ]
    return min_f(options, key=lambda x: x[1])

# Fourth last step: p1 selects p1 attackers for p2's defender 1
def max_p1_choose_p1_attackers(p1_d1, p1_remaining, p2_d1, p2_remaining, min_f=min) -> ([(int, int)], int):
    options = [
        min_p2_choose_p2_attackers(p1_d1, p1_a1, p1_a2, p1_d2, p2_d1, p2_remaining, min_f)
        for (p1_d2, [p1_a1, p1_a2]) in choose1(p1_remaining)
    ]
    return max(options, key=lambda x: x[1])

# Third last step: p2 selects p2 attackers for p1's defender 1
# This implicitly determines p2_d2
def min_p2_choose_p2_attackers(p1_d1, p1_a1, p1_a2, p1_d2, p2_d1, p2_remaining, min_f=min) -> ([(int, int)], int):
    options = [
        max_p1_choose_p2_attackers(p1_d1, p1_a1, p1_a2, p1_d2, p2_d1, p2_a1, p2_a2, p2_d2, min_f)
        for (p2_d2, [p2_a1, p2_a2]) in choose1(p2_remaining)
    ]
    return min_f(options, key=lambda x: x[1])

# Second last step: p1 chooses from p2's attackers for p1's defender 1
def max_p1_choose_p2_attackers(p1_d1, p1_a1, p1_a2, p1_d2, p2_d1, p2_a1, p2_a2, p2_d2, min_f=min) -> ([(int, int)], int):
    options = [
        # Choose p1_d1<>p2_a1 and p2_d2<>p2_a2
        min_p2_choose_p1_attackers(p1_d1, p1_a1, p1_a2, p1_d2, p2_d1, p2_a1, p2_a2, p2_d2, min_f),
        # Choose p1_d1<>p2_a2 and p2_d2<>p1_a2
        min_p2_choose_p1_attackers(p1_d1, p1_a1, p1_a2, p1_d2, p2_d1, p2_a2, p2_a1, p2_d2, min_f),
    ]
    return max(options, key=lambda x: x[1])

# Last step: p2 chooses from p1's attackers for p2's defender 1
# Assume without loss of generality that p1 has selected p1_d1<>p2_a1 and p1_d2<>p2_a2.
# We need to choose either:
# - p2_d1 <> p1_a1 and p2_d2 <> p1_a2 or
# - p2_d1 <> p1_a2 and p2_d2 <> p1_a1
def min_p2_choose_p1_attackers(p1_d1, p1_a1, p1_a2, p1_d2, p2_d1, p2_a1, p2_a2, p2_d2, min_f=min) -> ([(int, int)], int):
    matchups = [
        [(p1_d1, p2_a1), (p1_d2, p2_a2), (p1_a1, p2_d1), (p1_a2, p2_d2)],
        [(p1_d1, p2_a1), (p1_d2, p2_a2), (p1_a2, p2_d1), (p1_a1, p2_d2)]
    ]
    options = [(matchup, matchup_payoff(matchup)) for matchup in matchups]
    return min_f(options, key=lambda x: x[1])

if __name__ == "__main__":
    all_players = list(range(0, len(payoffs)))
    optimal_matchups, payoff = max_p1_choose_p1_defender(all_players, all_players, min_f=min)

    print(f"payoff: {payoff}, matchups: {optimal_matchups}")

    [p1_defender1, p1_attacker1, p1_attacker2, p1_defender2] = [p1 for (p1, _) in optimal_matchups]
    [p2_attacker1, p2_attacker2, p2_defender1, p2_defender2] = [p2 for (_, p2) in optimal_matchups]

    print("optimal strategy:")
    print(f"us: choose {p1_defender1} as defender")
    print(f"us: choose {p1_attacker1}, {p1_attacker2} as attackers")
    print(f"us: keep {p1_defender2} as second defender")

    print("opponent response:")
    print(f"them: choose {p1_defender1} as defender")
    print(f"them: choose {p1_attacker1}, {p1_attacker2} as attackers")
    print(f"them: keep {p1_defender2} as second defender")
