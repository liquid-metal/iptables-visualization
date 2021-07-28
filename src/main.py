from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.behaviors import DragBehavior
from kivy.uix.image import Image
from kivy.lang import Builder

import json
import sys

import iptables_parser
import model


def print_tree(root, indent=0):
    print(f'{" "*indent}{root}')
    for c in root.children:
        print_tree(c, indent=indent+2)


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


class OverviewWidget(Image):
    pass


class NodeViewWidget(Widget):
    def __init__(self, *args, **kwargs):
        self.title = 'No table selected'
        self.chains = None
        super().__init__(*args, **kwargs)
        self.bind(size=self.relocate_chains)

    def relocate_chains(self, instance, value):
        pos = [10, self.height - 10]
        max_row = 0
        for c in self.children:
            c.pos = (pos[0], pos[1] - c.height)
            max_row = max(max_row, c.height)
            pos[0] += 380
            if pos[0] + 350 > self.width:
                pos[0] = 10
                pos[1] = max_row + 30
                max_row = 0

    def set_chains(self, title, chains):
        self.title = title
        self.chains = chains

        self.clear_widgets()

        for c in self.chains:
            w = ChainWidget(c)
            self.add_widget(w)


class MyApp(App):
    def __init__(self, tables):
        self.tables = tables
        super().__init__()

    def build(self):
        root = Builder.load_file('kv/root.kv')
        node_view = Builder.load_file('kv/node_view.kv')
        node_view.children[0].set_chains('chains title', self.tables[1].chains)
        
        root.children[0].add_widget(node_view)
        return root


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <path-to-saved-iptables>')
        sys.exit(1)

    tables = iptables_parser.parse_iptables_save(sys.argv[1], '4')
    
    app = MyApp(tables)
    app.run()

