#!/usr/bin/env python
#
# Helper for keys
# Keep in lib directory
# Copyright (C) 2015 Phil Champagne, bookofsatoshi.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

#
# This allows the creation of a mnemonic based on the BIP39 dictionary
# from any arbitrary words. It should be used with caution. 
# A minimum of 12 words should be provided, but more can be supplied.
# For example, you could use all the words from a paragraph of a book 
# (minus punctuation) to which you could add a specific word of you choice.
# Anything goes and go as wild as you can.
# The purpose is for you to have the ability to recreate your wallet entirely 
# from memory using a set of words you could get from a known source or 
# from a set you are familiar with. However, it is recommended you take 
# note of the mnemonic generated using the BIP39 dictionary as another
# backup. 
#

import os
import sys

script_dir = os.path.dirname(os.path.realpath(__file__))
is_bundle = getattr(sys, 'frozen', False)
is_local = not is_bundle and os.path.exists(os.path.join(script_dir, "setup-release.py"))

sys.path.insert(0, os.path.join(script_dir, 'packages'))
sys.path.insert(0, os.path.join(script_dir, 'lib'))

def check_imports():
    # pure-python dependencies need to be imported here for pyinstaller
    try:
        import dns
        import pyaes
        import ecdsa
        import requests
        import six
        import qrcode
        import pbkdf2
        import google.protobuf
        import jsonrpclib
    except ImportError as e:
        sys.exit("Error: %s. Try 'sudo pip install <module-name>'"%e.message)
    # the following imports are for pyinstaller
    from google.protobuf import descriptor
    from google.protobuf import message
    from google.protobuf import reflection
    from google.protobuf import descriptor_pb2
    from jsonrpclib import SimpleJSONRPCServer
    # check that we have the correct version of ecdsa
    try:
        from ecdsa.ecdsa import curve_secp256k1, generator_secp256k1
    except Exception:
        sys.exit("cannot import ecdsa.curve_secp256k1. You probably need to upgrade ecdsa.\nTry: sudo pip install --upgrade ecdsa")
    # make sure that certificates are here
    assert os.path.exists(requests.utils.DEFAULT_CA_BUNDLE_PATH)


check_imports()

# load local module as electrum
import imp
imp.load_module('electrum', *imp.find_module('lib'))
imp.load_module('electrum_gui', *imp.find_module('gui'))


from electrum import bitcoin, network
from electrum import SimpleConfig, Network
from electrum.wallet import Wallet, Imported_Wallet
from electrum.storage import WalletStorage
from electrum.util import print_msg, print_stderr, json_encode, json_decode
from electrum.util import set_verbosity, InvalidPassword, check_www_dir
from electrum.commands import get_parser, known_commands, Commands, config_variables
from electrum import daemon
from electrum import keystore
from electrum.mnemonic import Mnemonic

import version
from bitcoin import is_old_seed, is_new_seed

import hashlib
import base64
import re
import hmac

import ecdsa
import pyaes

numargs = len(sys.argv)
cmdargs = str(sys.argv)

if numargs < 2:
    print "Missing arguments. Need at least 1 word, but more is better"
    sys.exit(1)

if numargs < 12:
    print "Warning: you should consider providing at least 12 words"

words = ""
i = 1

while True:
    words += str(sys.argv[i])
    i += 1
    if i >= numargs:
        break;
    words += " "

print "words supplied: " + words

#
# The resulting words must fit the criteria of generating a hash
# that starts with the SEED_PREFIX (01)
# We will add a number to this list of words that was supplied and 
# we will keep incrementing it until the criteria is satisfied.
#

mnemo = Mnemonic('en')

nonce = 0
while True:
    # Add the nonce if non zero
    if nonce == 0:
        words_to_hash = words
    else:
    	words_to_hash = words + " " + str(nonce)
    #
    # Generate the hash and take the first half of the hash since
    # mnemonic_encode expects 16 bytes seed
    #
    hash_obj = hashlib.sha256(words_to_hash)
    seed1 = hash_obj.hexdigest()
    seed2 = int(seed1[:34], 16)
    #
    # Get back the mnemonic based on the words of dictionary
    # Check if fits criteria, if so stop, otherwise keep incrementing
    # the nounce
    #    mwords = Mnemonic().mnemonic_encode(seed2)
    mwords = mnemo.mnemonic_encode(seed2)
    if is_new_seed(mwords, version.SEED_PREFIX):
	break
    nonce += 1

seed = seed2    

print "==========================="
print "========= RESULT =========="
print "==========================="
print "mnemonic phrase to use to generate back your wallet:"
print str(mwords)
print "==========================="
print "==========================="
print "seed used " + hex(seed)
print "Final phrase used was: "
print words_to_hash
print "==========================="
