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
#     display_name: Python 3.8.0 32-bit
#     language: python
#     name: python38032bit6948bcf2bd1d495c8d3b7cfa49a7d542
# ---

# ##############################################################################################################
#
# YAML Part
#
#     Misc tests
#

import yaml

# +
with open(r'2019.yaml') as profile_file:
    profile = yaml.load(profile_file, Loader=yaml.FullLoader)
    profile_file.close()

print (profile)
type(profile)
# -

for k, v in profile.items():
    print(k, "->", v)
    print(type(k))

# +
FormList = []
VarDict = {}
FieldDict = {}
for i, val in enumerate(profile["Forms"]):
    for k, v in val.items():
        if k.lower() == "form":
            FormList.append(v)
            curform="F"+str(v)
        if k.lower() == "sections":
            for ii, vval in enumerate(v):
                for kk, vv in vval.items():
                    if kk.lower() == "section":
                        cursection="S"+str(vv)
                    elif kk.lower() == "fields":
                        for iii, vvval in enumerate(vv):
                            for kkk, vvv in vvval.items():
                                fieldname = curform + cursection + kkk
                                FieldDict[fieldname]=vvv
                                print (f'Field {fieldname}: {vvv}')
                    else:
                        VarDict[kk]=vv
                        print (f'Variable {kk}: {vv}')

print (FormList)
print (VarDict)
print (FieldDict)
# -

print(yaml.dump(profile))

# +
with open(r'.\\TaxDefinition.yaml') as TaxDef_file:
    TaxDefRaw = yaml.load(TaxDef_file, Loader=yaml.FullLoader)
    TaxDef_file.close()

print (TaxDefRaw)
type(TaxDefRaw)
# -

TaxDefRaw["Tax"]

# +
StepperDict={}
GVarTaxDefDict={}
stepperseq=0

for k in TaxDefRaw["Tax"]:
        if k.lower() != "forms":
            keyname=f'TDV_G_{k.lower()}'
            GVarTaxDefDict[keyname]=TaxDefRaw["Tax"][k]

for i, val in enumerate(TaxDefRaw["Tax"]["Forms"]):
    for k, v in val.items():
        if k.lower() == "form":
            curform="F"+str(v)
        if k.lower() == "sections":
            for ii, vval in enumerate(v):
                for kk, vv in vval.items():
                    if kk.lower() == "section":
                        cursection="S"+str(vv)
                        stepperseq=0
                    else:
                        keyname=f'TDS_{curform}{cursection}_S{stepperseq}_{kk.lower()}'
                        StepperDict[keyname]=vv
                        stepperseq+=1

print (GVarTaxDefDict)
print ()
print (StepperDict)

# +
import pandas as pd

FormsName=2074
steps = pd.DataFrame.from_dict(StepperDict,orient='index')
steps.reset_index(level=0, inplace=True)
steps.rename(columns={'index': 'StepName', 0: 'Step'}, inplace=True)
steps["Section"]="Section"
search_string=f'TDS_F{FormsName}'
StepsFor=steps[steps['StepName'].str.contains(search_string)]
#StepsFor.loc[11,"Section"]="Test"
if not StepsFor[StepsFor['Section']=="Section"].empty:
    dfb = StepsFor[StepsFor['Section']=="Section"].index.values.astype(int)[0]
    print (dfb)

print(StepsFor.loc[dfb,"Step"])
print(StepsFor.head())
# -

dlg = StepsFor.groupby('StepName')
print (type(dlg))
sdlg = sorted(dlg.groups.keys())
for i in sdlg:
    print (i)

# +
#Field propagation in local
print (FieldDict.keys())
print (FieldDict['F2044S2F211_Avignon'])

exec("F2044S2F210_Avignon = 7000")
del F2044S2F210_Avignon

exec("if 'F2044S2F210_Avignon' not in globals():\n    F2044S2F210_Avignon = 6900")

if 'F2044S2F210_Avignon' in globals():
    print ("Var present in Globals")
else:
    print ("var absent in Globals")

if 'F2044S2F210_Avignon' in locals():
    print ("Var present in Locals")
else:
    print ("var absent in Locals")

gl=locals()
print (gl['F2044S2F210_Avignon'])
print (F2044S2F210_Avignon)
print ("F2042S1AJ".split('_')[0][7:])
# -

print ("F2042S1_AJ".split('_')[1])

F2042=None
for f in profile["Forms"]:
    if '2042' in f.values():
        F2042=f
if None != F2042:
    for k, v in F2042.items():
        print(k, "->", v)


# +
SectionsIn2042=profile["Forms"][0]["Sections"]

for Section in SectionsIn2042:
    print(Section)
    if ((isinstance(Section, dict)) and ("Fields" in Section)):
        for Field in Section["Fields"]:
            print (Field)


# +
#Work with TaxeGrid
import datetime 

year = 2019
Rev = 18650
print (datetime.datetime.now().year)

Grids = TaxDefRaw["Tax"]["RangeGrids"]
print (Grids)
for g in Grids:
    if g["Grid"] == year:
        RL = g["Ranges"]

Amount=0
        
while (Rev > 0):
    for i,r in enumerate(RL):
        a,b,c = r[f'R{i+1}']
        if a <= Rev <= b:
            irv = Rev - (a + 1)
            print (f'Applied range {i+1} at {c}% for {irv} Euro')
            Amount = Amount + irv*(c/100)
            print (f'Added {irv*(c/100)} to Amount')
            Rev = a
            print (f'New Rev amount {Rev}')

print (f'Final Taxe : {round(Amount,0)}')
# -

# ##############################################################################################################
#
# YAML + Pandas Part
#
#     Misc tests
#

import pandas as pd
StepperDict
print (type(StepperDict))

steps = pd.DataFrame.from_dict(StepperDict,orient='index')
steps

steps.reset_index(level=0, inplace=True)
steps.columns
steps.rename(columns={'index': 'StepName', 0: 'Step'}, inplace=True)
steps

StepsFor=steps[steps['StepName'].str.contains('TDS_F2074')]
StepsFor
StepsForDict=StepsFor.to_dict()
StepsForDict['StepName']

StepsFor

Forms = pd.DataFrame.from_dict(profile["Forms"][0])
Forms

print(type(profile["Forms"][0]))
CurSection = pd.DataFrame.from_dict(Forms["Sections"][1])
CurSection

print(type(CurSection["Fields"][0]))
CurFields = pd.DataFrame.from_dict(CurSection["Fields"][0],orient='index')
CurFields

print (CurSection["Fields"][0]["DC_CE"])

# ##############################################################################################################
#
# Currency Part
#
#     Misc tests
#

from currency_converter import CurrencyConverter
from datetime import date
c = CurrencyConverter()

c.convert(1, 'USD', 'EUR', date=date(2019, 12, 31))

# ##############################################################################################################
#
# Dynamic code Part
#
#     Misc tests
#

llist=["DC","TR","BH","CK"]
exec('DC=3')
exec('TR=20')
exec('BH=23')
exec('CK=2')
Sum=0
print(eval("DC"))
exec('for i in llist: Sum=Sum+eval(i)')
print(Sum)

# ##############################################################################################################
#
#     Misc tests
#

from datetime import datetime, timedelta
s = '2020/12/23'
Debut = datetime.strptime(s, "%Y/%m/%d")
print (Debut.strftime('%Y-%m-%d'))
Switch = Debut + timedelta(days=182)
print (Switch.strftime('%Y-%m-%d'))
Fin = Debut + timedelta(days=1095)
print (Fin.strftime('%Y-%m-%d'))

# +

if 'a' in globals() and a == 1: print ("ok")
# -

l = [835,3246,4642,5579,7194,4589]
if 'l' in globals(): F651 = sum(l)
print (F651)
print (l[0])

# +
amount = 1
amountlist = [835,3246,4642,5579,7194,4589]

repartlist = []
newamountlist = []
remains = amount

for a in amountlist:
    remains = amount - a
    if remains <= 0:
        newamountlist.append(abs(remains))
        repartlist.append(amount)
        remains = 0
        amount = 0
    else:
        newamountlist.append(0)
        repartlist.append(a)
        amount = remains
        
print (f'repart list {repartlist}')
print (f'new amount list {newamountlist}')
print (f'remain {remains}')

# -

def ExecStr(string, loc = locals()):
    
    print (string)
#    print ("Locals Before")
#    print (locals())
    try:
        result = exec(string, globals(), loc)
    except:
        result=False
    print ('F215' in globals().keys())
#    print ("Locals after")
#    print (locals())
    return result



d={'GF215': 3}
print ('F215' in locals().keys())
bef = locals().copy()
stringexec = f'F215 = d["GF215"]'
stringexec = 'F215 = "Sale Stock Award Msft"'
#stringexec = "F211=1\nRecettes = F211\nif 'F212' in locals(): Recettes = Recettes + F212\nif 'F213' in locals(): Recettes = Recettes + F213\nF215 = Recettes"
#stringexec = "Print a"
r = ExecStr(stringexec)
#r = ExecStr(stringexec, loc = locals())
aft= locals().copy()
print ('F215' in locals().keys())

del F215

for k in aft.keys():
    if k not in bef.keys():
        print (k)

#  Section 7
F215 = 15934
F250 = 6046
F240 = 8074
F630 = 0
F651 = 24271
F702 = F215
F703 = F250
F704 = F240
F706 = F702 - F703 - F704
Case7A = abs(F706)
if F703 < F702: F708 = F702 - F703 - F704
Case7C = 0
Case7E = 0
if 'F708' in globals() and F708 < 0: Case7C = max(abs(F708),10700)
if 'F708' in globals() and F708 < 0: Case7E = max(abs(F708)-10700,0)
if 'F708' in globals() and F708 > 0: Case7E = F706
if F703 > F702: F712 = F702 - F703
Case7B = 0
Case7D = 0
if 'F712' in globals(): Case7C = max(abs(F704),10700)
if 'F712' in globals() and F704 > 10700: Case7B = max(abs(F704)-10700,0)
Case7I = Case7B + Case7D
Case7J = Case7C + Case7E
Case7H = Case7A
DeficitRevFon = 0
DeficitRevGlo = 0
if Case7I > Case7H: DeficitRevFon = Case7I - Case7J
if Case7I > Case7H: DeficitRevGlo = Case7I - Case7J
if Case7I <= Case7H: DeficitRevGlo = Case7J - Case7H + Case7I
print ("Case7A =",Case7A)
print ("Case7B =",Case7B)
print ("Case7C =",Case7C)
print ("Case7D =",Case7D)
print ("Case7E =",Case7E)
print ("Case7H =",Case7H)
print ("Case7I =",Case7I)
print ("Case7J =",Case7J)

Relicat = 0
F12 = -Relicat

F630 = -1
eval ('F630 < 0')

a = round(327 * 12.8 / 100)
a


