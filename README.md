# keyword-generator
Allows the creation of BIP39 seeds from a custom set of words or passphrase

This program allows the creation of a mnemonic based on the BIP39 dictionary
using any arbitrary words. It should be used with caution as a simple word 
would be too weak. A minimum of 12 words should be provided, but more can 
be supplied.

For example, you could use all the words from a paragraph of a book
(minus punctuation) to which you could add a specific word of you choice.
Anything goes and go as wild as you can.

The purpose is for you to have the ability to recreate your wallet entirely
from memory using a set of words you could get from a known source or
from a set you are familiar with. However, it is recommended you take
note of the mnemonic generated using the BIP39 dictionary as another
backup. 


keywords.py uses Electrum wallet's libraries, and the file should be placed
in the lib directory of Electrum. From there, execute it using:

`./keywords.py <insert your words, one space in between>`

Example:

`./keywords.py my dog ate my homework and I love pizza`

