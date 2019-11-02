#!/usr/bin/env python3
#-*- coding:utf-8 -*-

class TreeNode:
    def __init__(self, word=None, depth=0):
        self.template_id = None
        self.depth = depth
        self.word = word
        self.node_pool = dict()

class MatchTree:
    def __init__(self):
        self.root = TreeNode()
        self.template_map = dict()

    def templateNum(self):
        return len(self.template_map)

    # def checkfunc(self, i, j, strict=False):
    # # check a match of two words
    # # strict=True: match only if word_i == word_j
    # # strict=False: match if word_i contains word_j as a substring
    #     if strict:
    #         return i == j
    #     else:
    #         return not i.find(j) == -1

    def match_template(self, log):
        '''match the log with template

        Args:
        --------
        log: a list of words in the log

        Returns:
        --------
        template id and variables string if match successfully, otherwise None
        '''
        log_length = len(log)
        node_candidate = self.root
        queue = [(self.root, 0)]
        while queue:
            current_node, current_index = queue[0]
            queue = queue[1:]
            if current_node.template_id:
                node_candidate = current_node
            if current_index >= log_length: continue
            for template_word in current_node.node_pool.keys():
                try:
                    next_index = log[current_index:].index(template_word)+current_index+1
                    next_node = current_node.node_pool[template_word]
                    queue.append((next_node, next_index))
                except ValueError:
                    continue

        if node_candidate.template_id:
            template_id = node_candidate.template_id
            variables = [i for i in log if i not in set(self.template_map[template_id])]
            return template_id, " ".join(variables)
        return None
            

    def add_template(self, template, template_id=None):
        '''add template to MatchTree

        Args:
        --------
        template: a list of template words
        template_id: id of the template, default None

        Returns:
        --------
        template_id: id of the added template
        '''
        if not template_id:
            template_id = self.templateNum()+1
        else:
            template_id = int(template_id)
        self.template_map[template_id] = template
        current_node = self.root
        for word in template:
            if word == "*": continue
            if word in current_node.node_pool.keys():
                current_node = current_node.node_pool[word]
            else:
                current_node.node_pool[word] = TreeNode(word=word, depth=current_node.depth+1)
                current_node = current_node.node_pool[word]
        if current_node.template_id:
            print("template already exists")
            # print(self.template_map[current_node.template_id])
            # print(self.template_map[template_id])
        else:
            current_node.template_id = template_id
        return template_id


if __name__ == "__main__":
# run __main__ to test
    templates = [
        "a b c * e f",
        "* c * f",
        "* * c c",
    ]
    logs = [
        "a c b f",
        "a a a",
        "c d e",
        "c c c c",
    ]
    matcher = MatchTree()
    print("add templates")
    for t in templates:
        print(matcher.add_template(t.split(" ")))
    print("match logs")
    for l in logs:
        print(matcher.match_template(l.split(" ")))
    print("template map")
    print(matcher.template_map)
