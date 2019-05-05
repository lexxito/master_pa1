#!/usr/bin/env bash

cd $1
virtualenv $2
source "$2/bin/activate"
pip download apache-libcloud