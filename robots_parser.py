from typing import Optional, NamedTuple
import re

class Rule(NamedTuple):
    key: str
    value: str

class RobotsRuleParser:
    delimiter: str = ''
    def __init__(self, delimiter: str = ': ') -> None:
        self.delimiter = delimiter

    def parse(self, line: str, ) -> Rule:
        idx = line.find(self.delimiter)
        return Rule(line[0:idx], line[idx+2:])
        

class RobotsParser:
    text: list[str]
    _disallowed: list[str] = []
    my_user_agent: Optional[str]
    rule_parser: RobotsRuleParser = RobotsRuleParser()
    current_index: int
    rule_index: int


    def __init__(self, text: list[str], my_user_agent: Optional[str] = None) -> None:
        self.text = text
        self.my_user_agent = my_user_agent
        self.current_index = 0
        self.rule_index = 0


    def user_agent_relevant(self) -> bool:
        user_agent: str = self.rule_parser.parse(self.text[self.current_index]).value
        if user_agent == self.my_user_agent:
            return True
        if user_agent == '*\n':
            return True
        return False


    def another_rule_for_agent(self) -> bool:
        if self.current_index + self.rule_index == len(self.text)-1:
            return False

        if self.text[self.current_index + self.rule_index + 1].startswith('User-agent'):
            return False

        self.rule_index += 1
        if self.text[self.current_index + self.rule_index] == '\n':
            return self.another_rule_for_agent()

        return True


    def append_rule(self) -> None:
        line = self.text[self.current_index + self.rule_index]
        rule: Rule = self.rule_parser.parse(line)
        if rule.key != 'Disallow':
            raise NotImplementedError("andere rule als Disallow")
        self._disallowed.append(rule.value.rstrip())



    def parse(self) -> None:
        if len(self.text) == 0:
            return
        self.clean_comments()
        self.clean_newlines()
        while self.more_rules_exist():
            if not self.user_agent_relevant():
                self.current_index +=1
                continue

            while self.another_rule_for_agent():
                self.append_rule()

            self.rule_index = 0
            self.current_index += 1


    @property
    def disallowed(self) -> list[str]:
        return self._disallowed


    def clean_comments(self) -> None:
        for idx, line in enumerate(self.text):
            if line[0] =='#':
                self.text.pop(idx)
            new_val = re.sub('#.*$', '', line)
            new_val.strip()
            new_val.rstrip()
            self.text[idx] = new_val


    def clean_newlines(self) -> None:
        if self.text[0] == '\n':
            self.text.pop(0)
        for idx, _ in enumerate(self.text):
            if idx == 0:
                if self.text[idx] == '\n':
                    self.text.pop(idx)
                pass
            if self.text[idx] == '\n' and self.text[idx-1] == '\n':
                self.text.pop(idx)


    def more_rules_exist(self) -> bool:
        for idx, line in enumerate(self.text[self.current_index:]):
            if line.startswith('User-agent'):
                self.current_index += idx
                return True

        return False
    

# example usage
if __name__ == '__main__':

    robots_txt = open(file='robots.txt')
    robots_parser: RobotsParser = RobotsParser([], None)#robots_txt.readlines(), None)
    robots_parser.parse()
    print(robots_parser.disallowed)
