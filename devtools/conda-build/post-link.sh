#!/bin/bash

set -e

mkdir -p $PREFIX
touch $PREFIX/.messages.txt

echo "PREFIX is $PREFIX" >> $PREFIX/.messages.txt

# install reduce -- only available from source
echo "installing Reduce"  >> $PREFIX/.messages.txt
[ -d "reduce" ] && rm -rf reduce
git clone https://github.com/rlabduke/reduce.git >> $PREFIX/.messages.txt
[ -d "$PREFIX/reduce" ] && rm -rf reduce || mv reduce $PREFIX

mkdir -p $PREFIX/build/reduce
cd $PREFIX/build/reduce
cmake $PREFIX/reduce -DCMAKE_INSTALL_PREFIX=$HOME/local >> $PREFIX/.messages.txt
make >> $PREFIX/.messages.txt
make install >> $PREFIX/.messages.txt