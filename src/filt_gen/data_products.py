#!/usr/bin/env python3

import sys
import os

class DataProducts:

    def __init__(self, name, requires_file=False):
        self.name = name
        self.requires_file = requires_file

    def get_name(self):
        return self.name


def create_data_products():
    dp_list = []
    #Sites
    dp_sites = DataProducts('Sites', False)
    dp_list.append(dp_sites)
    return dp_list