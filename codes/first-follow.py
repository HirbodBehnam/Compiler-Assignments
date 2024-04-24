# Mostly from https://github.com/PranayT17/Finding-FIRST-and-FOLLOW-of-given-grammar/blob/master/first_follow.py
import copy

EPSILON = "ϵ"
EOF = "$"

def is_terminal(input: str) -> bool:
    return input == EPSILON or input[0].islower()

class Rule:
    def __init__(self, left: str, rights: list[list[str]]):
        self.left = left
        self.rights = rights

    def __str__(self) -> str:
        result = self.left + " -> "
        for right in self.rights:
            result += " ".join(right)
            result += " | "
        return result[:-3]

class Rules:
    def __init__(self, starting_symbol: str, rules: list[Rule]):
        self.starting_symbol = starting_symbol
        self.rules = rules
        self.firsts: dict[str, set[str]] = {}
        self.follows: dict[str, set[str]] = {}
    
    def read_from_file(filename: str):
        rules: list[Rule] = []
        starting_symbol = None
        with open(filename, encoding="utf-8") as file:
            for line in file:
                left_side, right_side = line.split("->")
                left_side = left_side.strip()
                rights: list[list[str]] = []
                for rule in right_side.strip().split("|"):
                    rights.append(rule.strip().split())
                if starting_symbol == None:
                    starting_symbol = left_side
                rules.append(Rule(left_side, rights))
        assert starting_symbol
        return Rules(starting_symbol, rules)
    
    def calculate_firsts(self):
        # Clear firsts
        self.firsts.clear()
        # For each left hand side run first
        for rule in self.rules:
            self.firsts[rule.left] = self.first([rule.left])

    def calculate_follows(self):
        # Pre computation stuff
        self.follows.clear()
        self.calculate_firsts()
        # Add all non terminals to follow
        for rule in self.rules:
            self.follows[rule.left] = set()
        # Add $ to starting symbol
        self.follows[self.starting_symbol] = set([EOF])
        # Now for each rule calculate the follow of each non terminal 
        while True:
            changed = False
            # Loop on each rule
            for rule in self.rules:
                for right in rule.rights:
                    for index, symbol in enumerate(right):
                        if not is_terminal(symbol):
                            # Is this the last symbol of this rule?
                            if index == len(right) - 1:
                                # Add follow of left side to this follow
                                new_follows = self.follows[symbol].union(self.follows[rule.left])
                                changed = changed or (new_follows != self.follows[symbol])
                                self.follows[symbol] = new_follows
                            else:
                                # Create beta from whatever is in the right hand side of this symbol
                                beta = right[index + 1:]
                                assert len(beta) != 0
                                first_of_beta = self.first(beta)
                                has_epsilon = EPSILON in first_of_beta
                                if has_epsilon:
                                    first_of_beta.remove(EPSILON)
                                # Add the first of beta to follows
                                new_follows = self.follows[symbol].union(first_of_beta)
                                changed = changed or (new_follows != self.follows[symbol])
                                self.follows[symbol] = new_follows
                                # If first of beta had epsilon, add follow of left hand side as well
                                new_follows = self.follows[symbol].union(self.follows[rule.left])
                                changed = changed or (new_follows != self.follows[symbol])
                                self.follows[symbol] = new_follows

            # Check if everything is stable or not
            if not changed:
                break

    def first(self, symbols: list[str]) -> set[str]:
        assert len(symbols) != 0
        # Check multi char symbols
        if len(symbols) != 1:
            result: set[str] = set()
            for symbol in symbols:
                symbol_first = self.first(symbol)
                has_epsilon = EPSILON in symbol_first
                if has_epsilon:
                    symbol_first.remove(EPSILON)
                result = result.union(symbol_first)
                if not has_epsilon:
                    break
            return result
        # Single symbol
        if symbols[0] in self.firsts:
            return self.firsts[symbols[0]]
        if is_terminal(symbols):
            return set([symbols])
        # Check all right hand sides of this non terminal
        result: set[str] = set()
        for rule in self.rules:
            if rule.left != symbols[0]:
                continue
            # Add firsts of each char in string
            for right in rule.rights:
                last_symbol_had_epsilon = False
                for symbol in right:
                    last_symbol_had_epsilon = False
                    if symbol == EPSILON:
                        result.add(EPSILON)
                        break
                    assert symbol != symbols[0], "We don't support left recursion"
                    symbol_first = self.first(symbol)
                    has_epsilon = EPSILON in symbol_first
                    if has_epsilon:
                        symbol_first.remove(EPSILON)
                        last_symbol_had_epsilon = True
                    result = result.union(symbol_first)
                    if not has_epsilon:
                        break
                if last_symbol_had_epsilon:
                    result.add(EPSILON)
        if len(result) == 0:
            raise Exception(f"FUCKUP on {symbols}")
        return result
    
    def __str__(self) -> str:
        result = ""
        for rule in self.rules:
            result += str(rule) + "\n"
        return result

def left_factor(rules: Rules) -> Rules:
    rules = copy.deepcopy(rules)
    rules.follows.clear()
    rules.firsts.clear()
    for rule in rules.rules:
        # TODO
        pass
    return rules

rules = Rules.read_from_file("5-grammar.txt")
rules.calculate_follows()
print(rules.firsts)
print(rules.follows)