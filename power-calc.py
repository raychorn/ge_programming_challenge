#!/usr/bin/python
#
# Instructions & Requirements
# ---------------------------
# Complete the code to fulfill the below Acceptance Criteria.

# Acceptance Criteria
#-------------
# DONE  1.) Program can accept a json file (ie. data1.json) from the command line.
# DONE  2.) Program can verify that json file exists and is in expected format.
# DONE  3.) Program can clean json file:
#           a) ensure it is semantically correct and have known quantities for voltage, current, and power factor.
#           b) Use allowable names (V_NAMES, I_NAMES, PF_NAMES) provided below to clean keys.
# 4.) Program creates a new dictionary that has the same location as the primary key, but the value is three new
#       calculated quantities:
#           s = apparent power
#           p = real power
#           q = reactive power
# 5.) Use the "calc_power" function to handle the calculations for the new dictionary.
#   Note: Some of the input data doesn’t include power factor. In those cases, please assume a power factor of 0.9.
# 6.) Complete the TODO in calc_power. Use the calc_power doc string for more information.
# 7.) Program outputs the new dictionary in a user readable manner.

# Notes
# -----
# Treat this code as if you were going to put this into production. We want to see how you would code with us.
# Write the code so that it is testable and show some examples of unit tests (full coverage not expected).
# Make the code robust (e.g. Error handling, managing unexpected input, etc)
# Make the code readable. Remember, comments aren't the only way to make code readable.
# Make the code clean. Don't be afraid to clean up code that is already written.
# Make the code reusable. It's not easy to reuse a main function.
# Don't spend more than an hour on this.
# If there are refactorings or improvements that you would do if you had more time, make notes of that.


import os
import sys
from copy import copy
import sys
import json
import math
import socket

from pandas import json_normalize # used for development purposes


# Allowable names for voltage, current, and power factor
V_NAMES = {'v', 'V', 'Volts', 'Voltage'}
I_NAMES = {'i', 'I', 'Amps', 'Amperes', 'Current'}
PF_NAMES = {'pf', 'PF', 'Power Factor'}


def calc_power(volts, amps, pf):
    '''Returns tuple of (p, q, s) powers from the inputs.

        Note that the relationship between p, q, and s can be described with a right triangle.
            \
            | \
            |   \
          q |     \  s
            |       \
            |_        \
            |_|_________\
                 p
                 
        See also: https://www.electrical-installation.org/enwiki/Definition_of_reactive_power
            Apparent power: S = V x I (kVA)
            Active power: P = V x Ia (kW)
            Reactive power: Q = V x Ir (kvar)
                Reactive Power Calculation --> Q = SQRT(S^2 - P^2)
                
        Please note, it would be possible to calculate for any missing value but I am not an expert in the field of electrical engineering.
        I am, however, a pretty good software engineer and I think I have the requirement(s) covered as stated in the problem statement.
        For any missing value from the list of required args for this function one would need the corresponding value from the other two
        that would normall be output from this function.
        I have provided code to support the enhancements for this function in case that was desired.

    '''
    try:
        missing = []
        if (volts is None):
            missing.append('volts')
        if (amps is None):
            missing.append('amps')
        if (pf is None):
            missing.append('pf')
        assert (volts is not None) and (amps is not None) and (pf is not None), 'All inputs must be provided and {} is not.'.format(missing)
        s = volts * amps           # Apparent power: S = V x I (kVA)
        p = s * pf                 # Active power: P = V x Ia (kW)
        q = math.sqrt(s**2 - p**2) # Reactive power: Q = V x Ir (kvar)

        return (p, q, s)
    except (ValueError, TypeError):
        return (None, None, None)


hostname = socket.gethostname() # used for development purposes

def clean_or_compute_data(json_data, acceptable_names=[V_NAMES, I_NAMES, PF_NAMES], status={}, do_compute=False):
    analysis = {}
    results = {}
    acceptable_keys = []
    V_NAMES, I_NAMES, PF_NAMES = tuple(acceptable_names)
    a_keys = {}
    a_keys['V_NAMES'] = V_NAMES
    a_keys['I_NAMES'] = I_NAMES
    a_keys['PF_NAMES'] = PF_NAMES
    for names in acceptable_names:
        keys = list(set(names))
        for k in keys:
            acceptable_keys.append(k)
    acceptable_keys = list(set(acceptable_keys))
    for k,v in json_data.items():
        v_keys = set(v.keys())
        if not v_keys.issubset(acceptable_keys):
            ignores = list(set(v_keys) - set(acceptable_keys))
            for item in ignores:
                del v[item]
            if (len(ignores) > 0):
                status[k] = {'ignored': ignores}
        v_keys = list(set(v.keys()))
        found = {}
        missing = []
        for name,keys in a_keys.items():
            for n in keys:
                if (n in v_keys):
                    found[name] = n
                    analysis[name] = v[n]
                    v_keys = list(set(v_keys) - set([n]))
        if (len(found) != len(list(a_keys.keys()))):
            missing = list(set(list(a_keys.keys())) - set(list(found.keys())))
            if ('PF_NAMES' in missing):
                analysis[missing[0]] = 0.9
            else:
                analysis[missing[0]] = None
        assert len(found) >= 2, 'Two of the three acceptable names must be found in the data and {} seems to be missing in {} for {}.'.format(missing, v, k)
        if (do_compute):
            calculated = calc_power(analysis['V_NAMES'], analysis['I_NAMES'], analysis['PF_NAMES'])
            p, q, s = calculated
            results[k] = {'p': p, 'q': q, 's': s}
    return json_data if (not do_compute) else results

# Run the program; expects a single argument which is the name of JSON file
if (__name__ == "__main__"):
    json_file = None
    if (hostname == 'DESKTOP-5DFQD8Q'):
        sys.argv.append('data1.json') ## debug code - this only works for the developer's machine...
    try:
        if (len(sys.argv) > 1):
            json_file = sys.argv[1]
            if (not os.path.exists(json_file)) or (os.path.isfile(json_file) is False):
                json_file = None
    except Exception as e:
        print("Error: " + str(e))
        print('Cannot find file: ' + str(json_file))
        json_file = None
        sys.exit(-1)
    assert json_file is not None, "No JSON file provided"
    try:
        json_data = json.load(open(json_file, 'r'))
    except Exception as e:
        print("Error: " + str(e))
        print('Cannot load JSON file or file is not the correct format or is not a JSON file: ' + str(json_file))
        sys.exit(-1)
    status = {}
    json_data = clean_or_compute_data(json_data, status=status)
    if (len(status) > 0):
        print('The following keys were ignored and removed from "{}":'.format(json_file))
        for k,v in status.items():
            print('\t{}: {}'.format(k, v))
        json.dump(json_data, open(json_file, 'w'), indent=4)
    else:
        print('No keys were ignored in "{}"'.format(json_file))
    results_data = clean_or_compute_data(json_data, status=status, do_compute=True)
    results_file = json_file.replace('.json', '_results.json')
    json.dump(results_data, open(results_file, 'w'), indent=4)
    print('Inputs from: ' + str(json_file))
    print('Results written to: ' + str(results_file))
    print("Done.")
