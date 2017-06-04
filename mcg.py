#!/usr/bin/env python3

"""
Simple Markov chain text generator written in Python 3. (Tested on 3.5.2)

    usage: mcg.py [-h] [-i words] [-l number] [-n number] [-s] [-c] [file]

    Create similar texts using Markov processes.

    positional arguments:
      file        input file

    optional arguments:
      -h, --help  show this help message and exit
      -i word(s)  initial words of the generated text
      -l number   length of the produced text in words
      -n number   order of the Markov chain
      -s          show the tranisition table and exit
      -c          read the source as a cyclic sequence
"""

import argparse
import itertools
import pprint
import random
import sys
import textwrap

def cascade(iterable, n):
    clones = list(itertools.tee(iterable, n))

    offset = 0
    for it in clones:
        for i in range(offset):
            next(it, None)
        offset += 1
    return zip(*clones)

def weighted_choice(choices):
    total = sum(w for c, w in choices)
    r = random.uniform(0, total)
    upto = 0

    for c, w in choices:
        if upto + w >= r:
            return c

        upto += w

    assert False, "Out of probability distribution!"

def positive(value):
    ivalue = int(value)

    if ivalue <= 0:
        raise argparse.ArgumentTypeError("{} is not a positive integer".format(
            value))

    return ivalue

class Chain(object):
    def __init__(self, source, order, cyclic=False):
        self.source = source
        self.order = order
        self.cyclic = cyclic

        if order == 1:
            self.table_key_type = str
        else:
            self.table_key_type = tuple

    def process_source(self):
        self.compute_transition_counts()
        self.normalize_transitions()

    def compute_transition_counts(self):
        self.transition_dict = {}
        last_word = None

        self.words = self.source.split()

        if len(self.words) == 0:
            raise Exception("No words encountered in input.")

        first_word = self.words[0]

        if len(self.words) == 1:
            self.transition_dict[first_word] = {first_word: 1}

            return

        if len(self.words) <= self.order:
            raise Exception("Not enough words to create a higher order" \
                    " Markov chain.")

        for word_tpl in cascade(self.words, self.order + 1):
            if self.table_key_type == str:
                first_words = word_tpl[0]
                next_word = last_words = last_word = word_tpl[1]
            else:
                first_words = word_tpl[:-1]
                last_words = word_tpl[1:]
                next_word = last_word = word_tpl[-1]

            if first_words not in self.transition_dict:
                self.transition_dict[first_words] = {}

            if next_word not in self.transition_dict[first_words]:
                self.transition_dict[first_words][next_word] = 1
            else:
                self.transition_dict[first_words][next_word] += 1

        if self.cyclic:
            if last_words not in self.transition_dict:
                self.transition_dict[last_words] = {first_word: 1}
            else:
                if first_word not in self.transition_dict[last_words]:
                    self.transition_dict[last_words][first_word] = 1
                else:
                    self.transition_dict[last_words][first_word] += 1
        else:
            if last_words not in self.transition_dict:
                self.transition_dict[last_words] = {last_word: 1}

    def normalize_transitions(self):
        for key in self.transition_dict:
            total_transitions = 0
 
            for word in self.transition_dict[key]:
                total_transitions += self.transition_dict[key][word]
      
            for word in self.transition_dict[key]:
                self.transition_dict[key][word] /= total_transitions
 
    def _next_word(self, word):
      if word not in self.transition_dict:
            raise Exception("Malformed transition dictionary.")
 
      return weighted_choice(self.transition_dict[word].items())
 
    def generate(self, initial_string, num_words):
        if initial_string is None:
            initial_words = random.choice(list(self.transition_dict))
        else:
            if self.table_key_type == str:
                initial_words = initial_string
            else:
                initial_words = tuple(initial_string.split())

            if initial_words not in self.transition_dict:
                raise Exception("Initial words are not present in the source" \
                        " text.")

        if self.table_key_type == str:
            result = [initial_words]
        else:
            result = list(initial_words)

        current_words = initial_words
 
        for i in range(num_words - 1):
           next_word = self._next_word(current_words)
           result.append(next_word)

           if self.table_key_type == str:
               current_words = next_word
           else:
               current_words = current_words[1:] + (next_word,)
 
        return " ".join(result)

def parse_args():
    parser = argparse.ArgumentParser(
            description="Create similar texts using Markov processes.")

    parser.add_argument(
            type=argparse.FileType('r'),
            dest="file",
            metavar="file",
            default=sys.stdin,
            nargs='?',
            help="input file")

    parser.add_argument("-i",
            type=str,
            dest="initial_string",
            metavar="word(s)",
            default=None,
            help="initial words of the generated text")

    parser.add_argument("-l",
            type=positive,
            dest="num_words",
            metavar="number",
            default=30,
            help="length of the produced text in words")

    parser.add_argument("-n",
            type=positive,
            dest="order",
            metavar="number",
            default=1,
            help="order of the Markov chain")

    parser.add_argument("-s",
            action="store_true",
            dest="show_table",
            help="show the tranisition table and exit")

    parser.add_argument("-c",
            action="store_true",
            dest="cyclic",
            help="read the source as a cyclic sequence")

    return parser.parse_args()

def main():
    args = parse_args()

    source = str()
    try:
        with args.file as f:
            for line in f:
                source += line
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully.
        print()
        sys.exit(0)

    chain = Chain(source, args.order, args.cyclic)
    chain.process_source()
    
    if args.show_table:
        pprint.pprint(chain.transition_dict)
        sys.exit(0)
    else:
        result = chain.generate(args.initial_string, args.num_words)

        for line in textwrap.wrap(result, width=79):
            print(line)

if __name__ == "__main__":
    main()
