#!/bin/bash

set -e

echo "PREFIX is $PREFIX" >> $PREFIX/.messages.txt

# install reduce -- only available from source
echo "installing Reduce" >> $PREFIX/.messages.txt 
git clone https://github.com/rlabduke/reduce.git
mv reduce $PREFIX

mkdir -p $PREFIX/build/reduce
cd $PREFIX/build/reduce
cmake $PREFIX/reduce -DCMAKE_INSTALL_PREFIX=$HOME/local >> $PREFIX/.messages.txt
make >> $PREFIX/.messages.txt
make install >> $PREFIX/.messages.txt

rm -rf $PREFIX/reduce
rm -rf $PREFIX/build/reduce
rm $PREFIX/reduce_wwPDB_het_dict.txt
