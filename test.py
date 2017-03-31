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
            # [01:44.53]When I take a step into the darkness　
            tokens = line.split("]")
            timePart = tokens[0][1:]
            headTokens = timePart.split(":")
            print(headTokens)
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

from urllib.parse import unquote 
if __name__ == "__main__":
    testFile = "file:///home/user/Music/KOTOKO/KOTOKO%20-%20wind%20of%20memory%20~%E8%A8%98%E6%86%B6%E3%81%AE%E9%A2%A8~.lrc"
    testFile = "file:///home/user/Music/StylipS/StylipS%20-%20TSU%E3%83%BBBA%E3%83%BBSA.lrc"
    testFile = testFile[len("file://"):]
    testFile = unquote(testFile)
    print(testFile)
    lines = LrcParser.load(testFile)
    for line in lines:
        print(line)
