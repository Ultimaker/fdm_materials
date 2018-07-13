#!/usr/bin/env python
import os
import sys


if __name__ == '__main__':
    for filename in sys.argv[1:]:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if "<version>" in line.strip() and "</version>" in line.strip():
                idx = line.find("<version>") + len("<version>")
                idx2 = line.find("</version>")
                num = int(line[idx:idx2])
                num += 1
                new_line = line[:idx] + str(num) + line[idx2:]
                lines[i] = new_line
                break
        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(lines)

