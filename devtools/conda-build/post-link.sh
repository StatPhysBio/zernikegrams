#!/bin/bash

set -e

mkdir -p $PREFIX
touch $PREFIX/.messages.txt

echo "PREFIX is $PREFIX"

# install reduce -- only available from source
echo "installing Reduce"  
[ -d "reduce" ] && rm -rf reduce
git clone https://github.com/rlabduke/reduce.git
[ -d "$PREFIX/reduce" ] && rm -rf reduce || mv reduce $PREFIX

mkdir -p $PREFIX/build/reduce
cd $PREFIX/build/reduce
cmake $PREFIX/reduce -DCMAKE_INSTALL_PREFIX=$HOME/local
make 
make install