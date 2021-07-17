from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.behaviors import DragBehavior
from kivy.lang import Builder

import json


def print_tree(root, indent=0):
    print(f'{" "*indent}{root}')
    for c in root.children:
        print_tree(c, indent=indent+2)


class Rule:
    def __init__(self, content):
        self.content = content


class Chain:
    def __init__(self, name, rules):
        self.name = name
        self.rules = rules


class RuleWidget(Widget):
    def __init__(self, rule):
        self.rule = rule
        super().__init__()


class ChainWidget(DragBehavior, Widget):
    def __init__(self, chain):
        self.chain = chain
        super().__init__()
        self.populate_rules()

    def populate_rules(self):
        layout = self.children[0]
        for rule in self.chain.rules:
            r = RuleWidget(rule)
            layout.add_widget(r)


class MyApp(App):
    def __init__(self):
        self.chains = [Chain('chain-name', [Rule('rule1'), Rule('rule2')])]
        super().__init__()

    def build(self):
        root = Builder.load_file('root.kv')
        pos = [10, 500]
        for c in self.chains:
            w = ChainWidget(c)
            w.pos = pos
            root.add_widget(w)
            pos[1] -= 250
        return root


if __name__ == '__main__':
    MyApp().run()

