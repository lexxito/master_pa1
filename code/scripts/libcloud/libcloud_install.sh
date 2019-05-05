#!/usr/bin/env bash

cd $1
source "$2/bin/activate"
pip install apache-libcloud

