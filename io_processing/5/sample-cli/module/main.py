#!/usr/bin/env python
# -*- coding:utf-8 -*-
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--args1', type=int, default=1 )
    parser.add_argument('--args2', type=int, default=2 )
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))

    print("Hello World!")
    