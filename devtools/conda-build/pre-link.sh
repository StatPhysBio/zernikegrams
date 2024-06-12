#!/bin/bash

set -e

echo "PREFIX is $PREFIX" >> $PREFIX/.messages.txt

# install reduce -- only available from source
echo "installing Reduce" >> $PREFIX/.messages.txt
export CMAKE_INSTALL_PREFIX=$HOME/local
git clone https://github.com/rlabduke/reduce.git
mv reduce $PREFIX

echo "we are in $(pwd)" >> $PREFIX/.messages.txt

mkdir -p $PREFIX/build/reduce
cd $PREFIX/build/reduce
cmake $PREFIX/reduce
make
make install

echo "now we are in $(pwd)" >> $PREFIX/.messages.txt

