# Mostly from https://github.com/PranayT17/Finding-FIRST-and-FOLLOW-of-given-grammar/blob/master/first_follow.py
EPSILON = "ϵ"

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
            self.firsts[rule.left] = self.first(rule.left)

    def first(self, symbols: str) -> set[str]:
        if symbols in self.firsts:
            return self.firsts[symbols]
        if is_terminal(symbols):
            return set([symbols])
        # Check multi char strings
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
        # Check all right hand sides of this non terminal
        result: set[str] = set()
        for rule in self.rules:
            if rule.left != symbols:
                continue
            # Add firsts of each char in string
            for right in rule.rights:
                for symbol in right:
                    if symbol == EPSILON:
                        result.add(EPSILON)
                        break
                    symbol_first = self.first(symbol)
                    has_epsilon = EPSILON in symbol_first
                    if has_epsilon:
                        symbol_first.remove(EPSILON)
                    result = result.union(symbol_first)
                    if not has_epsilon:
                        break
        if len(result) == 0:
            raise Exception(f"FUCKUP on {symbols}")
        return result
    
    def follow(self, non_terminal: str) -> set[str]:
        assert not is_terminal(non_terminal)
        assert len(non_terminal) == 0
    
    def __str__(self) -> str:
        result = ""
        for rule in self.rules:
            result += str(rule) + "\n"
        return result
    
rules = Rules.read_from_file("2-grammar.txt")
rules.calculate_firsts()
print(rules)
print(rules.firsts)
print(rules.first("BbC"))