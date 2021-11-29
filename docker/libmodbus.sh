#!/bin/bash
cd $HOME
git clone git://github.com/stephane/libmodbus
cd libmodbus
./autogen.sh
./configure && make install
## Can change installization directory with prefix w/ `./configure --prefix=/path/you/want


