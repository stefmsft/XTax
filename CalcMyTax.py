# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

from XTax import Tax
import os.path

# +
Profile = "MyTax.yaml"

MyTax = Tax()

if os.path.isfile(Profile):

    print ('Loading the Tax profile file')
    MyTax.LoadProfile(Profile)
    
    print ('Calculating your Tax')
    MyTax.Calculate()
# -


