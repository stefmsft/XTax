# -*- coding: utf-8 -*-
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

# +
import yaml
import pandas as pd
import os
import datetime

class Tax:
    """Classs representing a spécific year of Tax"""    

    #
#  Function __init__
#
#  Params: year of tax
#
#  Description : Class initializer
#                if a Tax profile file corresponding to the year exists in the current directory, it is automatically loaded
#
#  Return: Nothing
#
    def __init__(self, year=2010, loglevel=3,autoload=True):
        self.LogLevel = loglevel
        self.__Log("Beginning of Init")
        self.__Reset()
        self.LogLevel = loglevel
        self.Year = year
        if autoload:
            fname = ".\\{}.yaml".format(year)
            if os.path.isfile(fname):
                self.__Log("Automatic load of {}".format(fname))
                self.LoadProfile(fname)
                Profile_Name=fname

        self.__Log("End of Init")
        
#----------------------------------------------------------------------------------------------------------------------        return
# Internals Method/function    
#-----------------------------------------------------------------------------------------------------------------------
#
#  Function Reset
#
#  Params: Initialize any Class Global Variable (Properties)
#
#  Description : Function needed to avoid side effect on module reload
#
#  Return: Nothing
#
    def __Reset(self):

        self.__Log("Reset Properties")
        self.Year = 0
        self.bProfileLoaded = False
        self.bTaxDefLoaded = False
        self.bFormsProcessed = False
        self.bTaxCalculted = False
        self.LogLevel = 3
        self.RawTaxProfile = None
        self.RawTaxDef = None
        self.FormList = []
        self.VarDict = {}
        self.FieldDict = {}
        self.StepperDict={}
        self.GVarTaxDefDict={}
        self.ResultDict = {}
        self.EnableComputeLog = False
        self.ComputeLogBuffer = []
        self.Local2Del = []
        
        return

#
#  Function Log
#
#  Params: String to log
#          level of the logging
#
#  Description : If the LogLevel is compatible, the string is written to the console
#
#  Loglevel 1 = Debug <-default for each Log calls
#  Loglevel 2 = Log
#  Loglevel 3 = Warning <- Default level at Class init (show only warning and errors)
#  LogLevel 4 = Errors
#  Loglevel 5 = Exceptions
#
#  Return: Nothing
#
    def __Log(self, string, level=1):
        if level >= self.LogLevel:
            print (string)
        return

#
#  Function ExecStr
#
#  Params: String to log
#          logging enabled or not
#
#  Description : Execute a python code and eventually log it
#
#
#  Return: Nothing
#
    def __ExecStr(self, string):

        result = True
        bef = locals().copy()
        try:
            exec(string, globals(),locals())
        except Exception as e:
            self.__Log(f'Exception while Computing {string}',5)
            self.__Log(f'Exception :  {e.__class__}',5)
            result = False
        aft= locals().copy()
        
        if result:
            for k in aft.keys():
                if k not in bef.keys() and k != 'bef':
                    if k not in self.Local2Del:
                        self.Local2Del.append(k)
                    globals()[k]=locals()[k]
            if self.EnableComputeLog:
                if not string.startswith('del') and not string.startswith('ldv'):
                    self.ComputeLogBuffer.append(string)
        
        return result

#
#  Function LoadYamlFile
#
#  Params: Yaml File name to load
#
#  Description : Load and serialize a Tax Profile
#
#  Return: True of False and the Yaml Raw Content
#
    def __LoadYaml(self, file):
        self.__Log(f'Beginning of LoadYamlFile {file}')

        if os.path.isfile(file):
            with open(file) as yaml_file:
                YamlContent = yaml.load(yaml_file, Loader=yaml.FullLoader)
                yaml_file.close()
            result=True
        else:
            result=False

        
        self.__Log(f'End of LoadYamlFile {file}')
        return result,YamlContent

#  Function FlatenTP
#
#  Params:
#
#  Description 
#       From the RawTaxProfile loaded, if any, the function build a set of Field,variable dictionary
#       as well as a list of Forms definition found
#       Each Field name follow the naming schema :
#                    F{Form Number Name}S{Section Number}{FieldName}
#
#  Return:
#
    def __FlatenTP(self):
        self.__Log("Beginning of FlatenTP")
        
        if self.RawTaxProfile != None:
            for i1, lv1 in enumerate(self.RawTaxProfile["Forms"]):
                for k1, dv1 in lv1.items():
                    if k1.lower() == "form":
                        self.FormList.append(dv1)
                        curform="F"+str(dv1)
                    if k1.lower() == "sections":
                        for i2, lv2 in enumerate(dv1):
                            for k2, dv2 in lv2.items():
                                if k2.lower() == "section":
                                    cursection="S"+str(dv2)
                                elif k2.lower() == "fields":
                                    for i3, lv3 in enumerate(dv2):
                                        for k3, dv3 in lv3.items():
                                            fieldname = curform + cursection + "_" + k3
                                            self.FieldDict[fieldname]=dv3
                                            self.__Log(f'Field {fieldname}: {dv3}',2)
                                else:
                                    self.VarDict[f'{curform}{cursection}_{k2}']=f'{dv2}'
                                    self.__Log(f'Variable {curform}{cursection}_{k2}: {dv2}',2)            
            
        self.__Log("End of FlatenTP")
        return

#  Function FlatenTD
#
#  Params:
#
#  Description 
#       From the RawTaxDef loaded, if any, the function build a set of variables and execution steps per section per Form
#       Each variable name follow the naming schema :
#                    TDV_F{Form Number Name}S{Section Number}{dName}
#       Each step name follow the naming schema :
#                    TDS_F{Form Number Name}S{Section Number}{SeqNumber}
#
#  Return:
#
    def __FlatenTD(self):
        self.__Log("Beginning of FlatenTD")
        
        if self.RawTaxDef != None:
            for k in self.RawTaxDef["Tax"]:
                    if k.lower() != "forms":
                        keyname=f'TDV_G_{k.lower()}'
                        self.GVarTaxDefDict[keyname]=self.RawTaxDef["Tax"][k]
            stepperseq=0
            for i, val in enumerate(self.RawTaxDef["Tax"]["Forms"]):
                carryto2042List=""
                finalresultList=""
                for k, v in val.items():
                    if k.lower() == "form":
                        curform="F"+str(v)
                    if k.lower() == "carryto2042":
                        if carryto2042List == "":
                            carryto2042List=str(v)
                        else:
                            carryto2042List=f"{carryto2042List},{v}"
                    if k.lower() == "finalresult":
                        if finalresultList == "":
                            finalresultList=str(v)
                        else:
                            finalresultList=f"{finalresultList},{v}"
                    if k.lower() == "sections":
                        for ii, vval in enumerate(v):
                            for kk, vv in vval.items():
                                if kk.lower() == "section":
                                    cursection="S"+str(vv)
                                    stepperseq=0
                                else:
                                    keyname=f'TDS_{curform}{cursection}_S{stepperseq}_{kk.lower()}'
                                    self.StepperDict[keyname]=vv
                                    stepperseq+=1
                if carryto2042List != "":
                    keyname=f'TDS_{curform}S0_carryto2042'
                    self.StepperDict[keyname]=carryto2042List

                if finalresultList != "":
                    keyname=f'TDS_{curform}S0_finalresult'
                    self.StepperDict[keyname]=finalresultList

        self.__Log("End of FlatenTD")
        return

#  Function GetSectionFromName
#
#  Params:
#
#  Description :
#       Extract the Section from the Name in the form of TDS_F{form}S{section}_S{Seq}_{Action}
#
#  Return:
#
    def __GetSectionFromName(self,StepName):
        self.__Log(f'Beginning of GetSectionFromName {StepName}')

        section = StepName[10:12]
        if section[-1:]=="_": section = section[:1]
            
        self.__Log(f'End of GetSectionFromName - Section = {section}')
        return int(section)

#  Function GetActionFromName
#
#  Params:
#
#  Description :
#       Extract the Section from the Name in the form of TDS_F{form}S{section}_S{Seq}_{Action}
#
#  Return:
#
    def __GetActionFromName(self,StepName):
        self.__Log(f'Beginning of GetActionFromName {StepName}')

        sa = StepName.split("_")
        action = sa[len(sa)-1]
            
        self.__Log(f'End of GetActionFromName - Action = {action}')
        return action

#  Function LoadStepsFor
#
#  Params:
#
#  Description :
#       Given a Forms Name, the function return a step dictionnary to execute in order to process the Form
#
#  Return:
#
    def __LoadStepsFor(self,FormsName):
        self.__Log(f'Beginning of LoadStepsFor {FormsName}')

        steps = pd.DataFrame.from_dict(self.StepperDict,orient='index')
        steps.reset_index(level=0, inplace=True)
        steps.rename(columns={'index': 'StepName', 0: 'Step'}, inplace=True)
        steps["Section"]=steps["StepName"].apply(lambda x: self.__GetSectionFromName(x))
        steps["Action"]=steps["StepName"].apply(lambda x: self.__GetActionFromName(x))
        search_string=f'TDS_F{FormsName}'
        StepsFor=steps[steps['StepName'].str.contains(search_string)]
        
        self.__Log(f'End of LoadStepsFor {FormsName}')
        return StepsFor

#  Function ProcesSteps
#
#  Params:
#
#  Description :
#       Given a Step list, Execute them and return the result in a Dictionary
#
#  Return:
#         Bool : False if error detected
#
    def __ProcesSteps(self,Steps,CurForm):
        self.__Log(f'Beginning of ProcesSteps for {CurForm}')

        if self.EnableComputeLog:
            self.ComputeLogBuffer.append(f'#Forms {CurForm}')

        result = True
        currentfieldnamecontext=f"{CurForm}"
        currentloopext=""
        Sg=Steps.groupby('Section')
        self.__Log(f'Sections found in form {CurForm} : {Sg.groups.keys()}')
        lvarlist=[]
        
        # Focus on each section of the Form
        for cursection in sorted(Sg.groups.keys()):
            self.__Log(f'\nProcessing Section : {cursection}',2)
            
            currentloopext=""
            currentloopvl=[]
            curcompute=[]
            
            currentfieldnamecontext = f"F{CurForm}S{cursection}"
            self.__Log(f"Current Field Prefix {currentfieldnamecontext}")
            
            if self.EnableComputeLog and cursection!=0:
                self.ComputeLogBuffer.append(f'#  Section {cursection}')

            
            # Narrow the Steps to the actual section
            StepsForCurSection = Steps[Steps['Section']==cursection]

            # CleanUp localy created Variable before processing section
            for v in self.Local2Del:
                r = self.__ExecStr(f'del globals()["{v}"]')
                if r == False:
                    self.__Log(f'Error : While cleaning variable {v}',4)
            self.Local2Del.clear()
            
            # Look for loopon
            sFor="loopon"
            if not StepsForCurSection[StepsForCurSection['Action']==sFor].empty:
                dfb = StepsForCurSection[StepsForCurSection['Action']==sFor].index.values.astype(int)[0]
                currentloopext=StepsForCurSection.loc[dfb,"Step"]
                self.__Log("\nLoop on detected")
                currentloopext = f'{currentfieldnamecontext}_{currentloopext}'
                if currentloopext in self.VarDict.keys():
                    self.__Log(f'Loop On : {self.VarDict[currentloopext]}')
                    currentloopvl = self.VarDict[currentloopext].split(",")
                else:
                    self.__Log(f'Error : Loop On Variable "{currentloopext}" not defined',4)
                    result = False
                    break
                
            # Look for reqfields
            sFor="reqfields"
            if not StepsForCurSection[StepsForCurSection['Action']==sFor].empty:
                dfb = StepsForCurSection[StepsForCurSection['Action']==sFor].index.values.astype(int)[0]
                self.__Log("\nRequired Fields detected")
                if currentloopext == "":
                    currentloopvl.clear()
                    currentloopvl.append("*")
                 #Foreach element in currentloopvl
                for lctxt in currentloopvl:
                    ifv = StepsForCurSection.loc[dfb,"Step"].split(",")
                    for i in range(len(ifv)):
                        if lctxt == "*":
                            ifv[i] = f"{currentfieldnamecontext}_{ifv[i]}"
                        else:
                            ifv[i] = f"{currentfieldnamecontext}_{ifv[i]}_{lctxt}"
                    # Gen LoopName and verify required Fields
                    for i in ifv:
                        self.__Log(f'Checking required field or variable {i}')
                        s0name = f'F{CurForm}S0_{i.split("_")[1]}'
                        lvname = f'F{CurForm}S{cursection}_{i.split("_")[1]}'
                        # If name not in the local section field dict
                        if i not in self.FieldDict.keys():
                            #Check in S0 contect of the Field Dict
                            if s0name in self.FieldDict.keys():
                                self.__Log(f'Loading Field variable {i} with its global S0 value : {self.FieldDict[s0name]}',2)
                                self.FieldDict[i]=self.FieldDict[s0name]
                            #Check as a variable
                            elif lvname not in self.VarDict.keys():
                                self.__Log(f'    field or variable not defined yet. Initializing as a field with 0',2)
                                self.FieldDict[i]=0
                            else:
                                self.__Log(f'    found as a variable with value {self.VarDict[i]}',2)
                        else:
                            self.__Log(f'    found with value {self.FieldDict[i]}',2)
                    
                                                            
            #Look for repportfields
            sFor="repportfields"
            if not StepsForCurSection[StepsForCurSection['Action']==sFor].empty:
                dfb = StepsForCurSection[StepsForCurSection['Action']==sFor].index.values.astype(int)[0]
                self.__Log("\nRepport Fields detected")
                if currentloopext == "":
                    currentloopvl.clear()
                    currentloopvl.append("*")
                 #Foreach element in currentloopvl
                rfv = []
                for lctxt in currentloopvl:
                    fv = StepsForCurSection.loc[dfb,"Step"].split(",")
                    for i in range(len(fv)):
                        if lctxt == "*":
                            rfv.append(f"{currentfieldnamecontext}_{fv[i]}")
                        else:
                            rfv.append(f"{currentfieldnamecontext}_{fv[i]}_{lctxt}")
                self.__Log(f'List of Repport fields : {rfv}')
                                
            # Look for compute_custom
            sFor="compute"
            if not StepsForCurSection[StepsForCurSection['Action'].str.contains(sFor)].empty:
                self.__Log("\nCompute sequence detected")
                for dfb in StepsForCurSection[StepsForCurSection['Action'].str.contains(sFor)].index.values.astype(int):
                    cs = StepsForCurSection.loc[dfb,"Step"]
                    curcompute.append(cs)
                self.__Log(f'List of Compute sequence : {curcompute}')
                
                #Foreach element in currentloopvl
                for lctxt in currentloopvl:
                    self.__Log(f'\nProcessing on variable {lctxt}')

                    if self.EnableComputeLog and lctxt!="*":
                        self.ComputeLogBuffer.append(f'#    Loop {lctxt}')
                    
                    # CleanUp localy created Variable before processing loopOn
                    for v in self.Local2Del:
                        r = self.__ExecStr(f'del globals()["{v}"]')
                        if r == False:
                            self.__Log(f'Error : While cleaning variable {v}',4)
                    self.Local2Del.clear()

                    # Propagate localy the Fields of the section
                    self.__Log("\nField propagation in Locals")
                    for k in self.FieldDict.keys():
                        if k.startswith(f'{currentfieldnamecontext}'):
                            if lctxt == "*" or lctxt == k.split('_')[2]:
                                lf = k.split('_')[1]
                                if isinstance(self.FieldDict[k],str):
                                    execstring = f'{lf} = "{self.FieldDict[k]}"'
                                else:
                                    execstring = f'{lf} = {self.FieldDict[k]}'
                                r = self.__ExecStr(execstring)
                                if lf in globals().keys() and r != False:
                                    self.__Log(f'Variable {lf} successfully created')
                                    self.__Log(f'{lf} = {globals()[lf]}')
                                else:
                                    self.__Log(f'Error : While emitting "{lf}"',4)
                                    result = False
                                    break                            
                    # Propagate localy the variables of the section
                    self.__Log("\nVariable propagation in Locals")
                    for k in self.VarDict.keys():
                        if k.startswith(f'{currentfieldnamecontext}'):
                            lf = k.split('_')[1]
                            if isinstance(self.VarDict[k],str):
                                execstring = f'{lf} = "{self.VarDict[k]}"'
                            else:
                                execstring = f'{lf} = {self.VarDict[k]}'
                            r = self.__ExecStr(execstring)
                            if lf in globals().keys() and r != False:
                                self.__Log(f'Variable {lf} successfully created')
                                self.__Log(f'{lf} = {globals()[lf]}')
                            else:
                                self.__Log(f'Error : While emitting "{lf}"',4)
                                result = False
                                break                            

                    # Compute
                    self.__Log("\nCompute")
                    for c in curcompute:
                        self.__Log(f'Processing {c}')
                        r = self.__ExecStr(c)
                        if r != True:
                            break
                    # Propagate back to dictionary
                    self.__Log("\nField back propagation to dictionary")
                    self.__Log("For fields in profile")
                    for f in self.Local2Del:
                        if lctxt == "*":
                            updf = f'{currentfieldnamecontext}_{f}'
                        else:
                            updf = f'{currentfieldnamecontext}_{f}_{lctxt}'
                        self.__Log(f'Updating self.FieldDict["{updf}"]')
                        if updf in self.FieldDict.keys():
                            self.__Log(f'    Initial value : {self.FieldDict[updf]}')
                        r = self.__ExecStr(f'ldv = {f}')
                        if r == True:
                            self.FieldDict[updf] = ldv
                            self.Local2Del.remove("ldv")
                            self.__Log(f'    New value : {self.FieldDict[updf]}')

                    self.__Log("\nFor fields in report")
                    for k in rfv:
                        lf = k.split('_')[1]
                        if self.EnableComputeLog:
                            self.ComputeLogBuffer.append(f'print ("{lf} =",{lf})')
                        if lf not in self.Local2Del:
                            if lctxt == "*" or lctxt == k.split('_')[2]:
                                self.__Log(f'Updating self.FieldDict["{k}"]')
                                if  k in self.FieldDict.keys():
                                    self.__Log(f'Value of self.FieldDict["{k}"] = {self.FieldDict[k]}]')
                                else:
                                    self.FieldDict[k] = 0
                                    self.__Log(f'New value of self.FieldDict["{k}"] = {self.FieldDict[k]}')



            # Look for Agregate
            sFor="agregate"
            if not StepsForCurSection[StepsForCurSection['Action']==sFor].empty:
                dfb = StepsForCurSection[StepsForCurSection['Action']==sFor].index.values.astype(int)[0]
                agglist=StepsForCurSection.loc[dfb,"Step"].split(",")
                self.__Log("\nAgregate detected")
                self.__Log(f'\nField list to Aggregate : {agglist}')

                for f in agglist:
                    lookupf = f'{currentfieldnamecontext}_{f}'
                    aggval = 0
                    for k in self.FieldDict.keys():
                        if k.startswith(f'{lookupf}'):
                            self.__Log(f'Found {k} = {self.FieldDict[k]} to aggregate')
                            try:
                                aggval = aggval + self.FieldDict[k]
                            except:
                                self.__Log(f'Exception while aggregating {lookupf}',5)
                                pass
                    aggval = int(round(aggval))
                    self.__Log(f'Loading self.FieldDict[{lookupf}] with {aggval}')
                    self.FieldDict[lookupf]=aggval
                
            # Look for Save
            sFor="save"
            if not StepsForCurSection[StepsForCurSection['Action']==sFor].empty:
                dfb = StepsForCurSection[StepsForCurSection['Action']==sFor].index.values.astype(int)[0]
                savlist=StepsForCurSection.loc[dfb,"Step"].split(",")
                self.__Log("\nSave detected")
                self.__Log(f'Field list to propagate in the S0 section for later calculation : {savlist}')

                for f in savlist:
                    sectionf = f'{currentfieldnamecontext}_{f}'
                    targetf =  f'F{CurForm}S0_{f}'
                    if sectionf in self.FieldDict.keys():
                        self.__Log(f'Loading {targetf} with value of {sectionf} = {self.FieldDict[sectionf]}')
                        self.FieldDict[targetf]=self.FieldDict[sectionf]
                
            self.__Log(f'\n')
        self.__Log(f'End of ProcesSteps\n\n')
        return result

#-----------------------------------------------------------------------------------------------------------------------
# Public Method/function    
#-----------------------------------------------------------------------------------------------------------------------
    
#  Function Dump
#
#  Params:
#
#  Description :
#
#  Return:
#
    def Dump(self,topic="all"):
        self.__Log("Beginning of Object Dump")

        if (topic.lower() == "all" or topic.lower() == "raw"):
            print ("")
            print ("Raw Records :")
            print ("")
            if self.bProfileLoaded:
                print (f'Tax Profile Raw Records : {yaml.dump(self.RawTaxProfile)}')
            if self.bTaxDefLoaded:
                print (f'Tax Def Raw Records : {yaml.dump(self.RawTaxDef)}')

        if (topic.lower() == "all" or topic.lower() == "var"):
            print ("Variables :")
            print ("")
            if self.bProfileLoaded:
                print (f'Profil Variables :')
                print (self.VarDict)
            if self.bTaxDefLoaded:
                print ("")
                print (f'Tax Def Global Variables :')
                print (self.GVarTaxDefDict)

        if (topic.lower() == "all" or topic.lower() == "field"):
            if self.bProfileLoaded:
                print ("")
                print (f'Fields :')
                print (self.FieldDict)

        if (topic.lower() == "all" or topic.lower() == "step"):
            if self.bTaxDefLoaded:
                print ("")
                print (f'Steps :')
                print (self.StepperDict)

        if (topic.lower() == "all" or topic.lower() == "result"):
            if self.bTaxCalculted:
                print ("")
                print (f'Results :')
                print (self.ResultDict)

        if self.bProfileLoaded:
            print ("")
            print (f'List of Forms : {self.FormList}')

        self.__Log("End of Object Dump")
        return
    
#  Function CleanUpListInt
#
#  Params:
#         lst : list to Clean
#
#  Description :
#       
#
#  Return:
#        lst : Cleaned List
#
    def CleanUpListInt(self,lst):
        self.__Log(f'Beginning of CleanUpList for {lst}')
        
        if not isinstance(lst, list):
            if isinstance(lst, str):
                if lst[:1] == "[":
                    lst = lst[1:len(lst)-1].split(",")
                else:
                    lst = lst.split(",")
                for a in lst:
                    lst[lst.index(a)] = int(a)
                    
        self.__Log(f'End of CleanUpList returning {lst}')
        return lst
    
#  Function AllocateDeficit
#
#  Params:
#         amount : amount to distribute
#         amountlist : list of amount available for the distribution
#
#  Description :
#
#  Return:
#        repartlist : List of amount distributed
#        newamountlist : list of amount after distribution
#        remains : amount remaining if all can't be distributed
#
    def AllocateDeficit(self,amount,amountlist):
        self.__Log(f'Beginning of AllocateDeficit of {amount} thru {amountlist}')

        repartlist = []
        newamountlist = []
        remains = amount
        
        #Input Sanitization
        
        amount = int(amount)
        #Check if the 2nd arg is really a list (direct call) or a string representing a list (call from the yaml)   
        self.CleanUpListInt(amountlist)

        try:
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
        except Exception as e:
            self.__Log(f'Exception in AllocatDeficit',5)
            self.__Log(f'Exception :  {e.__class__}',5)            
        
        self.__Log(f'End of AllocateDeficit returning reparlist = {repartlist}, updated amountlist {newamountlist}, remaining amount {remains}')
        return repartlist,newamountlist,remains


#  Function DisplayComputeLog
#
#  Params:
#
#  Description :
#
#  Return:
#
    def DisplayComputeLog(self,section="all"):
        self.__Log("Beginning of DisplayComputeLog")
        if self.EnableComputeLog:
                for l in self.ComputeLogBuffer:
                    print (l)

        self.__Log("End of DisplayComputeLog")
        return

#
#  Function FinalTaxe
#
#  Params: Year
#          Taxable Revenu
#
#  Description : Use a Range Grid (one per year) to calculate the Taxe  
#
#  Return: Taxe amount
#
    def FinalTaxe(self, year=datetime.datetime.now().year,taxablerevenue=0,nbpart=1):
        self.__Log(f'Beginning of FinalTaxe for year {year} and a Taxable revenue of {taxablerevenue}')

        if self.bTaxDefLoaded == False: self.LoadTaxDef()
        if self.bTaxDefLoaded:
            Grids = self.RawTaxDef["Tax"]["RangeGrids"]
            for g in Grids:
                if g["Grid"] == year:
                    RL = g["Ranges"]

            TaxeAmount = 0
            Rev = taxablerevenue / nbpart

            while (Rev > 0):
                for i,r in enumerate(RL):
                    a,b,c = r[f'R{i+1}']
                    if a <= Rev <= b:
                        irv = Rev - (a + 1)
                        self.__Log(f'Applied range {i+1} at {c}% for {irv} Euro')
                        TaxeAmount = TaxeAmount + irv*(c/100)
                        self.__Log(f'Added {irv*(c/100)} to Amount')
                        Rev = a

            self.__Log(f'Final Taxe : {round(TaxeAmount,0)}')

            taxablerevenue = round(TaxeAmount,0) * nbpart

        self.__Log(f'End of FinalTaxe')
        return taxablerevenue


    
#
#  Function Load
#
#  Params: File Tax profile name to load
#
#  Description : Load and serialize a Tax Profile
#
#  Return: True of False
#
    def LoadProfile(self, profilefile):
        self.__Log(f'Beginning of LoadProfile {profilefile}')
        result = False
        
        (result,content) = self.__LoadYaml(profilefile)
        if result:
            self.RawTaxProfile=content
            self.bProfileLoaded = True
            self.__FlatenTP()

        self.__Log(f'End of LoadProfile {profilefile}')
        return result

#
#  Function LoadTaxDef
#
#  Params: File Tax definition name to load
#
#  Description : Load and serialize a Tax Profile
#
#  Return: True of False
#
    def LoadTaxDef(self, taxedeffile=".\\TaxDefinition.yaml"):
        self.__Log("Beginning of LoadTaxDef")
        result = False
        
        (result,content) = self.__LoadYaml(taxedeffile)
        if result:
            self.RawTaxDef=content
            self.bTaxDefLoaded = True
            self.__FlatenTD()
       
        self.__Log("End of LoadTaxDef")
        return result

#
#
#  Function LoadFieldDef
#
#  Params: File Tax Field definition name to load
#
#  Description : Load in a dictionary the definition of all the fields (For reporting purpose)
#
#  Return: True of False
#
    def LoadFieldDef(self, file=".\\TaxDictionary.yaml"):
        self.__Log("Beginning of LoadFieldDef")
        result = False
        self.__Log("End of LoadFieldDef")
        return result

#
#
#  Function ProcessForms
#
#  Params: None
#
#  Description : Process and yield Fields values for the Tax Calculation
#
#  Return: True of False
#
    def ProcessForms(self):
        self.__Log("Beginning of ProcessForms")

        result = True
        
        if self.bProfileLoaded:
            if self.bTaxDefLoaded == False: self.LoadTaxDef()
            if self.bTaxDefLoaded:
                if None != self.GVarTaxDefDict["TDV_G_processingorder"]:
                    ProcOrdList = self.GVarTaxDefDict["TDV_G_processingorder"].split(',')
                    for Form in ProcOrdList:
                        for ProForm in self.FormList:
                            if ProForm.lower() == Form.lower():
                                self.__Log(f'Processing forms {Form} ... ',2)
                                ExecSteps = self.__LoadStepsFor(Form)
#Dbg - Remove after
                                self.LogLevel = 1
                                if not self.__ProcesSteps(ExecSteps,Form):
                                    result = False
                                    break
#Dbg - Remove after
                        self.LogLevel = 3
                        if not result:
                            break
                    if result:
                        self.bFormsProcessed = True
        else:
            self.__Log("Error : No Tax Profile loaded",4)
            result = False

        self.__Log("End of ProcessForms")
        return result

#
#
#  Function Calculate
#
#  Params: None
#
#  Description : Calculate the Tax
#
#  Return: True of False
#
    def Calculate(self):
        self.__Log("Beginning of Calculate")

        result = True
        self.ResultDict={}
        
        if self.bFormsProcessed == False: result = self.ProcessForms()
        if result:
            self.__Log(f'Start Processing Tax Calculation ... ')

        if result:
            self.bTaxCalculted = True

        self.__Log("End of Calculate")
        return result

#
#
#  Function Report
#
#  Params: None
#
#  Description : Generate et report to help the Tax Filling
#
#  Return: True of False
#
    def Report(self):
        self.__Log("Beginning of Report")
        result = False
        self.__Log("End of Report")
        return result

#  Function 
#
#  Params:
#
#  Description :
#
#  Return:
#
    def Squel(self):
        self.__Log("Beginning of ")
        self.__Log("End of ")
        return



# -


