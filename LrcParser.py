#!/usr/bin/env python3
from os.path import join, exists

class LrcParser:
    @staticmethod 
    def load(file):
        with open(file) as f:
            lines = f.readlines()
            
        output = []
        offset = int(lines[0].split(":")[1][:-2])
        print(lines[0])
        print(offset)
        for line in lines[1:]:
            tokens = line.split("]")
            timePart = tokens[0][1:]
            headTokens = timePart.split(":")
            headTokens2 = headTokens[1].split(".")
            minutes = int(headTokens[0])
            seconds = int(headTokens2[0])
            milliseconds = int(headTokens2[1])
            time = (minutes * 60 + seconds) * 1000 + milliseconds + offset
            line = tokens[1]
            if len(line) == 0 or line == "\n":
                line = " "
            output.append((time / 1000.0, line))
        return output
