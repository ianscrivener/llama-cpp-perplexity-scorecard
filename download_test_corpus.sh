#!/bin/bash

force=false

for arg in "$@"
do
    if [ "$arg" == "--force" ]
    then
        force=true
    fi
done

if [ $force = false ] && [ -f "test_corpus/wiki.test.raw.406" ] && [ -f "test_corpus/wiki.test.raw.103" ]; then
  echo "Files wiki.test.raw.406 and wiki.test.raw.103 exist. Skipping download."
  exit 0
fi

mkdir -p test_corpus
cd test_corpus || exit
curl https://s3.amazonaws.com/research.metamind.io/wikitext/wikitext-2-raw-v1.zip --output wikitext-2-raw-v1.zip
unzip -o wikitext-2-raw-v1.zip
rm wikitext-2-raw-v1.zip
head -n406 wikitext-2-raw/wiki.test.raw > wiki.test.raw.406
head -n103 wikitext-2-raw/wiki.test.raw > wiki.test.raw.103

