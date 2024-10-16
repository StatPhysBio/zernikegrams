#!/usr/bin/env bash

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


# install DSSP -- easiest to build from source
echo "installing DSSP" >> $PREFIX/.messages.txt
[ -d "dssp" ] && rm -rf dssp
git clone https://github.com/PDB-REDO/dssp.git >> $PREFIX/.messages.txt
[ -d "$PREFIX/dssp" ] && rm -rf dssp || mv dssp $PREFIX
cd "$PREFIX/dssp"
cmake -DCMAKE_INSTALL_PREFIX=$HOME/local -S . -B build >> $PREFIX/.messages.txt
cmake --build build >> $PREFIX/.messages.txt
cmake --install build >> $PREFIX/.messages.txt

curl -o "$HOME/local/share/libcifpp/components.cif" https://files.wwpdb.org/pub/pdb/data/monomers/components.cif
curl -o "$HOME/local/share/libcifpp/mmcif_pdbx.dic" https://mmcif.wwpdb.org/dictionaries/ascii/mmcif_pdbx_v50.dic
curl -o "$HOME/local/share/libcifpp/mmcif_ma.dic" https://github.com/ihmwg/ModelCIF/raw/master/dist/mmcif_ma.dic