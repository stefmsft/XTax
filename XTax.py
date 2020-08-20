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
    """Class representing a spécific year of Tax"""    

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
        self.NbParts = 1
        self.bProfileLoaded = False
        self.bTaxDefLoaded = False
        self.bFormsProcessed = False
        self.bTaxCalculted = False
        self.bIRCalulated = False
        self.LogLevel = 3
        self.RawTaxProfile = None
        self.RawTaxDef = None
        self.NetTax = 0
        self.SoldeImpot = 0
        self.RevFiscalRef = 0
        self.DeficitFoncierAnterieur = 0
        self.TauxPrelevementSource = 0
        self.ListDeficit = []
        self.FormList = []
        self.VarDict = {}
        self.FieldDict = {}
        self.StepperDict={}
        self.GVarTaxDefDict={}
        self.ReportDict = {}
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
            for gv in self.RawTaxProfile:
                if gv != "Forms":
                    try:
                        self.VarDict[f'GV_{gv}']=int(f'{self.RawTaxProfile[gv]}')
                    except:
                        self.VarDict[f'GV_{gv}']=f'{self.RawTaxProfile[gv]}'
                        pass
                    self.__Log(f'    Variable GV_{gv}: {self.RawTaxProfile[gv]}',2)
            if 'Forms' in self.RawTaxProfile:
                self.__Log(f'\nLoading Forms variables',2)
                for i1, lv1 in enumerate(self.RawTaxProfile["Forms"]):
                    for k1, dv1 in lv1.items():
                        if k1.lower() == "form":
                            self.FormList.append(dv1)
                            curform="F"+str(dv1)
                            self.__Log(f'  Form {curform}',2)
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
                                                self.__Log(f'    Field {fieldname}: {dv3}',2)
                                    else:
                                        self.VarDict[f'{curform}{cursection}_{k2}']=f'{dv2}'
                                        self.__Log(f'    Variable {curform}{cursection}_{k2}: {dv2}',2)            
            
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

#  Function GetSectionFields
#
#  Params:
#         fns : Form string name
#         fdict : Dictionary where to populate fields:values
#
#  Description :
#       
#
#  Return:
#        flds : list of field=value
#
    def __GetSectionFields(self,fns,fdict):
        self.__Log(f'Beginning of __GetSectionFields for forms {fns}')

        flds = [f'{k}={self.FieldDict[k]}' for k in list(self.FieldDict.keys()) if fns in k[:len(fns)]]
        #Gen a dict with fields:values
        for li in flds:
            isl = li.split("=")
            if len(isl) > 1:
                fdict[isl[0]]=isl[1]

        self.__Log(f'End of GetSectionFields {fdict}')
        return flds

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
            if cursection != 0: self.__Log(f'\n    Processing Section : {cursection}',2)

            currentloopext=""
            currentloopvl=[]
            curcompute=[]
            WeDoCompute=True
            ConditionDetected=False
            
            currentfieldnamecontext = f"F{CurForm}S{cursection}"
            self.__Log(f"Current Field Prefix {currentfieldnamecontext}")
            
            if self.EnableComputeLog and cursection!=0:
                self.ComputeLogBuffer.append(f'#  Section {cursection}')

            
            # Narrow the Steps to the actual section
            StepsForCurSection = Steps[Steps['Section']==cursection]
            self.__Log(StepsForCurSection['Action'])

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
                    self.__Log(f'Loop On : {self.VarDict[currentloopext]}',2)
                    currentloopvl = self.VarDict[currentloopext].split(",")
                else:
                    self.__Log(f'Warning : Loop On Variable "{currentloopext}" not defined',2)
                    currentloopext = ""
                    
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
                                self.__Log(f'Loading Field variable {i} with its global S0 value : {self.FieldDict[s0name]}')
                                self.FieldDict[i]=self.FieldDict[s0name]
                            #Check as a variable
                            elif lvname not in self.VarDict.keys():
                                self.__Log(f'    field or variable not defined yet. Initializing as a field with 0')
                                self.FieldDict[i]=0
                            else:
                                self.__Log(f'    found as a variable with value {self.VarDict[i]}')
                        else:
                            self.__Log(f'    found with value {self.FieldDict[i]}')
                    
            # Look for Condition
            sFor="condition"
            if not StepsForCurSection[StepsForCurSection['Action']==sFor].empty:
                dfb = StepsForCurSection[StepsForCurSection['Action']==sFor].index.values.astype(int)[0]
                Condition=StepsForCurSection.loc[dfb,"Step"].split(",")[0]
                self.__Log("\nCondition detected")
                self.__Log(f'Condition found to continue process section {cursection} : {Condition}',2)
                ConditionDetected=True
                                                            
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
                            fn = f"{currentfieldnamecontext}_{fv[i]}"
                        else:
                            fn = f"{currentfieldnamecontext}_{fv[i]}_{lctxt}"
                        rfv.append(fn)
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
                    self.__Log("\nField propagation in Locals",2)
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
                                    self.__Log(f'{lf} = {globals()[lf]}',2)
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
                                self.__Log(f'{lf} = {globals()[lf]}',2)
                            else:
                                self.__Log(f'Error : While emitting "{lf}"',4)
                                result = False
                                break   
                                
                    if ConditionDetected:
                        try:
                            WeDoCompute = eval (Condition)
                        except Exception as e:
                            pass

                    if WeDoCompute:
                        # Compute
                        self.__Log('',2)
                        self.__Log("\nCompute")
                        for c in curcompute:
                            self.__Log(f'Processing {c}',2)
                            r = self.__ExecStr(c)
                            if r != True:
                                result = False
                                break

                    # Propagate back to dictionary
                    self.__Log("\nField back propagation to dictionary")
                    self.__Log("For fields in profile")
                    self.__Log('',2)
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
                        if updf in rfv:
                            self.ReportDict[updf]=self.FieldDict[updf]

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
                            self.ReportDict[updf]=self.FieldDict[k]

            # Look for Agregate
            sFor="agregate"
            if not StepsForCurSection[StepsForCurSection['Action']==sFor].empty and WeDoCompute:
                dfb = StepsForCurSection[StepsForCurSection['Action']==sFor].index.values.astype(int)[0]
                agglist=StepsForCurSection.loc[dfb,"Step"].split(",")
                self.__Log("\nAgregate detected")
                self.__Log(f'\nField list to Aggregate : {agglist}')
                
                for f in agglist:
                    f2clean=[]
                    lookupf = f'{currentfieldnamecontext}_{f}'
                    aggval = 0
                    for k in self.FieldDict.keys():
                        if k.startswith(f'{lookupf}'):
                            self.__Log(f'Found {k} = {self.FieldDict[k]} to aggregate')
                            try:
                                aggval = aggval + self.FieldDict[k]
                                f2clean.append(k)
                            except:
                                self.__Log(f'Exception while aggregating {k}',5)
                                result = False
                                break
                    aggval = int(round(aggval))
                    #Cleanup the FieldDict after Aggregation
                    for fc in f2clean:
                        del self.FieldDict[fc]
                    
                    self.__Log(f'Loading self.FieldDict[{lookupf}] with {aggval}',2)
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
                        self.__Log(f'Loading {targetf} with value of {sectionf} = {self.FieldDict[sectionf]}',2)
                        self.FieldDict[targetf]=self.FieldDict[sectionf]
                    else:
                        self.__Log(f'Creating {targetf} loaded with {sectionf} = 0',2)
                        self.FieldDict[targetf]=0
            
                
        # At the End ( After looping on each section) 
        # Get the steps for section 0
        StepsForCurSection = Steps[Steps['Section']==0]
        frlist=[]
        
        # Look for FinalResult
        sFor="finalresult"
        if not StepsForCurSection[StepsForCurSection['Action']==sFor].empty:
            dfb = StepsForCurSection[StepsForCurSection['Action']==sFor].index.values.astype(int)[0]
            frlist=StepsForCurSection.loc[dfb,"Step"].split(",")
            self.__Log("\nFinal Result detected")
            self.__Log(f'Final Result list to propagate their equivalente in CarryTo2042 : {frlist}')

        # Look for CarryTo2042
        sFor="carryto2042"
        if not StepsForCurSection[StepsForCurSection['Action']==sFor].empty:
            dfb = StepsForCurSection[StepsForCurSection['Action']==sFor].index.values.astype(int)[0]
            carrylist=StepsForCurSection.loc[dfb,"Step"].split(",")
            self.__Log("\nCarry To 2042 detected")
            self.__Log(f'Carry to 2042 list  : {carrylist}')
            if not frlist:
                self.__Log(f'But the Final Result List is empty',4)
                result = False
            else:
                i = 0
                for f in carrylist:
                    resultf = f'F{CurForm}S0_{frlist[i]}'
                    targetf =  f'F2042{f}'
                    if resultf in self.FieldDict.keys():
                        self.__Log(f'Loading {targetf} with value of {resultf} = {self.FieldDict[resultf]}')
                        if targetf in self.FieldDict.keys():
                            self.FieldDict[targetf]=self.FieldDict[targetf] + self.FieldDict[resultf]
                        else:
                            self.FieldDict[targetf]=self.FieldDict[resultf]
                        self.__Log(f'New value for {targetf} : {self.FieldDict[resultf]}')
                    i = i + 1

                
        self.__Log(f'\nEnd of ProcesSteps\n\n')
        return result

#-----------------------------------------------------------------------------------------------------------------------
# Public functions Helper    
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

        if (topic.lower() == "all" or topic.lower() == "report"):
            if self.bTaxCalculted:
                print ("")
                print (f'Report :')
                print (self.ReportDict)

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

#  Function SumSectionFields
#
#  Params:
#         f : Form name
#         s : section number
#
#  Description :
#
#  Return:
#        sumf : Sum of fields in the section
#
    def SumSectionFields(self,f,s):
        self.__Log(f'Beginning of SumSectionFields on section {s}')
        
        sname = f'F{f}S{s}'
        lstf = [self.FieldDict[k] for k in list(self.FieldDict.keys()) if sname in k[:len(sname)]]
        sumf = sum(lstf)

        self.__Log(f'End of SumSectionFields returning Sum of Fields = {sumf}')
        return sumf

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

#  Function ReportFieldsInSections
#
#  Params:
#         f : Form number
#         s : Section to number (if none s=0 then all section in the forms are processed)
#         display : If true (default) the fields and their value are printed
#
#  Description :
#       
#
#  Return:
#        fdict : dictionary of fields of the section/s
#
    def ReportFieldsInSections(self,f,s=None,display=True):
        if s == None:
            ends = ""
        else:
            ends = f' and section {s}'
        self.__Log(f'Beginning of ReportFieldsInSections for forms {f}{ends}')

        fdict = {}
        if s == None:
            for i in range(1,12):
                fn = f'F{f}S{i}'
                flds = self.__GetSectionFields(fn,fdict)
                if len(flds) > 0:
                    self.__Log(f'Section {i} : {flds}',2)
        else:
                fn = f'F{f}S{s}'
                flds = self.__GetSectionFields(fn,fdict)
                self.__Log(f'Section {s} : {flds}',2)
        
        self.__Log(f'End of ReportFieldsInSections {fdict}')
        return fdict

#-----------------------------------------------------------------------------------------------------------------------
# Public Method/function    
#-----------------------------------------------------------------------------------------------------------------------

#
#  Function ComputeProgressiveTax
#
#  Params: Year
#          Taxable Revenu
#
#  Description : Use a Range Grid (one per year) to calculate the Taxe  
#
#  Return: Taxe amount
#
    def ComputeProgressiveTax(self, year=datetime.datetime.now().year,taxablerevenue=0,nbpart=1):
        self.__Log(f'Beginning of ComputeProgressiveTax for year {year} income of {taxablerevenue} and {nbpart} part')

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
                    if a+1 < Rev <= b:
                        irv = Rev - (a)
                        self.__Log(f'Applied range {i+1} at {c}% for {irv} Euro')
                        TaxeAmount = TaxeAmount + (irv*c/100)
                        self.__Log(f'Added {irv*c/100} to Amount')
                        Rev = a

            taxablerevenue = int(round(TaxeAmount,0) * nbpart)

            self.__Log(f'Final Taxe : {taxablerevenue}')

        self.__Log(f'End of ComputeProgressiveTax')
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
            self.__Log("Loading Profile ...",2)
            self.__FlatenTP()
            # Ovrewrite Year and NBParts from the profile
            if 'GV_Year' in self.VarDict.keys():
                self.Year = self.VarDict['GV_Year']
            if 'GV_NbParts' in self.VarDict.keys():
                self.NbParts = self.VarDict['GV_NbParts']
            

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
    def LoadTaxDef(self, taxedeffile="TaxDefinition.yaml"):
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
#  Description : Process and yield Fields values of each forms for further Tax Calculation
#
#  Return: True of False
#
    def ProcessForms(self):
        self.__Log("Beginning of ProcessForms")

        result = True

        self.__Log(f'Start Processing Each Forms in order ... ',2)
        
        if self.bProfileLoaded:
            if self.bTaxDefLoaded == False: self.LoadTaxDef()
            if self.bTaxDefLoaded:
                if None != self.GVarTaxDefDict["TDV_G_processingorder"]:
                    ProcOrdList = self.GVarTaxDefDict["TDV_G_processingorder"].split(',')
                    for Form in ProcOrdList:
                        for ProForm in self.FormList:
                            if ProForm.lower() == Form.lower():
                                self.__Log(f'\nProcessing forms {Form} ... ',2)
                                ExecSteps = self.__LoadStepsFor(Form)
                                if not self.__ProcesSteps(ExecSteps,Form):
                                    result = False
                                    break
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
#  Function GetFieldValue
#
#  Params: Name
#
#  Description : Return a Field or Variable value by name
#
#  Return: Value of the Field or Variable
#
    def GetFieldValue(self,name):
        self.__Log("Beginning of GetFieldValue")
        
        if name in self.FieldDict.keys():
            value = self.FieldDict[name]
            self.__Log(f'Found Field {name} = {value}')
        elif name in self.VarDict.keys():
            value = self.VarDict[name]
            self.__Log(f'Found Variable {name} = {value}')
        else:
            value = 0

        self.__Log("End of GetFieldValue")
        return value

#
#
#  Function Decote
#
#  Params: Tax
#
#  Description : Calculate the "Decote" from the TaxFromPropGrid
#
#  Return: Decote value
#
    def Decote(self,tax):
        self.__Log(f'Beginning of Decote for {tax}')
        
        decote = 0
        founddecoteinfo = False

        Grids = self.RawTaxDef["Tax"]["DecoteGrids"]
        for g in Grids:
            if g["Grid"] == self.Year:
                founddecoteinfo = True
                Floors = g["Floors"]
                Forfait = g["Forfait"]
                Percent = g["Percent"]

        if self.NbParts == 1:
            category = "Celib"
        else:
            category = "Couple"

        if founddecoteinfo:
            #Check if decote applicable
            floor = Floors[category]
            if tax <= floor:
                forfait = Forfait[category]
                decote = forfait - (tax * Percent / 100)             
            
        self.__Log(f'End of Decote return {decote}')
        return decote

#
#
#  Function ComputeIR
#
#  Params: None
#
#  Description : Process and yield Fields values for the Tax Calculation
#
#  Return: True of False
#
    def ComputeIR(self,silent=False):
        self.__Log(f'Beginning of ComputeIR with Silent = {silent}')

        result = True
        cll = self.LogLevel
        if silent == True:
            self.LogLevel = 4

        if self.bFormsProcessed:

            #Calculate Taxable revenue
            self.__Log('\n  IMPOT SUR LE REVENU',3)
            self.__Log('  Détail des revenus',3)
            Salary = self.GetFieldValue("F2042S1_AJ")
            Incomes = self.GetFieldValue("F2042S1_Salaires")
            self.__Log(f'  Salaires = {Incomes}',3)
            if Salary != Incomes:
                OtherIncome = Incomes - Salary
                self.__Log(f'  Autres revenus imposables = {OtherIncome}',3)
            self.__Log(f'  Salaires = {Incomes}',3)
            tenpercent = round(Incomes*0.1,0)
            self.__Log(f'  10% déduction = {-int(tenpercent)}',3)
            Incomes = int(Incomes - tenpercent)
            self.__Log(f'  Salaires, Pensions, rentes nets = {Incomes}',3)
            
            self.__Log('\n  Revenus perçu par le foyer fiscal',3)
            RevFoncImp = self.GetFieldValue("F2042S4_BA")
            DefGlo = self.GetFieldValue("F2042S4_BC")
            if RevFoncImp > 0:
                self.__Log(f'  Revenus foncier nets = {RevFoncImp}',3)
            else:
                self.__Log(f'  Revenus foncier nets = {-DefGlo}',3)

            BrutGlobalIncome = Incomes - DefGlo + RevFoncImp
            self.__Log(f'\n  Revenus brut global = {BrutGlobalIncome}',3)
            
            DeductibleGSC = self.GetFieldValue("F2042S6_DE")
            self.__Log(f'  CSG Deductible = {-DeductibleGSC}',3)
            
            GlobalIncome = BrutGlobalIncome - DeductibleGSC
            self.__Log(f'\n  Revenu Imposable = {GlobalIncome}',3)

            #Still to validate
            RevTauxForfaitaire = int(round(self.SumSectionFields(2042,2) - self.GetFieldValue("F2042S2_CK") - self.GetFieldValue("F2042S2_BH") + self.GetFieldValue("F2042S3_VG")))
            self.__Log(f'\n  Revenus au taux forfaitaire 12,8% = {RevTauxForfaitaire}',3)

            if self.Year != None and self.NbParts != None:
                IRThruProgGrid = self.ComputeProgressiveTax(self.Year,GlobalIncome,self.NbParts)
                self.__Log(f'\n  Impot sur les revenus sousmis au barème = {IRThruProgGrid}',3)

            IRBeforeTaxR = IRThruProgGrid
            self.__Log(f'\n  Impôt avant réduction d impôt = {IRBeforeTaxR}',3)
            
            self.__Log('\n  REDUCTIONS D IMPOT\n',3)
            #Get eventually a decote
            decote = round(self.Decote(IRBeforeTaxR))
            if decote > 0:
                self.__Log(f'  Décote = {decote}',3)
                IRBeforeTaxR = IRBeforeTaxR - decote
            
            #Check for extra reduction
            if self.Year > 2016 and self.Year < 2020:
                if GlobalIncome < 19175:
                    ri = 0.2 * IRBeforeTaxR
                    IRBeforeTaxR = round(IRBeforeTaxR - ri)
                    self.__Log(f'  Réduction sous condition de revenu (20%) = {ri}',3)
                elif GlobalIncome < 21247:
                    if self.NbParts == 1:
                        part = 1
                        demip = 0
                    else:
                        part = 2
                        demip = (self.NbParts -2) / 2
                    rp = 0.2 * (((21247*part + 3835*demip) - GlobalIncome)/2072)
                    ri =  round(rp * IRBeforeTaxR)
                    IRBeforeTaxR = IRBeforeTaxR - ri                    
                    self.__Log(f'  Réduction sous condition de revenu ({round(rp*100)}%) = {ri}',3)

            #Invest type Scelier
            # Adapt for other investment ...
            InvLoc1 = self.GetFieldValue("F2042S7_HV")
            InvLoc2 = self.GetFieldValue("F2042S7_ZB")
            ReductionInvLoc = 0
            
            if InvLoc1 > 0:
                ReductionInvLoc = int(InvLoc1 * 25 / 100)
                LibelInvLoc = "Investissement Locatif Scellier achevé en 2010"
            elif InvLoc2 > 0:
                # Formula to be retreive
                ReductionInvLoc = int(InvLoc2 * 2 /100)
                LibelInvLoc = "Scellier, prorogation de l'engagement"
                                
            if ReductionInvLoc > 0:
                self.__Log(f'  {LibelInvLoc} = {ReductionInvLoc}',3)
                IRBeforeTaxR = IRBeforeTaxR - ReductionInvLoc
            
            #Donation to Org 
            OrgDon = self.GetFieldValue("F2042S7_UD")
            if OrgDon > 0:
                self.__Log(f'  Dons Personnes en difficulté = {OrgDon}',3)
                IRBeforeTaxR = IRBeforeTaxR - int(OrgDon*75/100)

            #Donation to General Interest Org
            OrgGIDon = self.GetFieldValue("F2042S7_UF")
            if OrgGIDon > 0:
                self.__Log(f'  Dons organisation humanitaires = {OrgGIDon}',3)
                IRBeforeTaxR = IRBeforeTaxR - int(OrgGIDon*66/100)
            
            self.__Log(f'  Total des réduction d\'impôt = {IRBeforeTaxR-IRThruProgGrid}',3)

            PropTax = round(RevTauxForfaitaire * 12.8 / 100)
            self.__Log(f'  Impôt proportionel = {PropTax}',3)

            IRBeforeTaxR = IRBeforeTaxR + PropTax
            
            if self.Year == 2018:
                rals = self.GetFieldValue("F2042S8_HV")
                self.__Log(f'  Reprise de l\'avance perçue sur réductions et crédits d\'impôt = {rals}',3)
                IRBeforeTaxR = IRBeforeTaxR + rals

            self.__Log(f'  Impot total avant crédits d\'impôts = {IRBeforeTaxR}',3)
            
            self.__Log('\n  CREDIT D\'IMPOT,IMPUTATION\n',3)
            
            NetTax = IRBeforeTaxR

            #Tax Already paid outside
            PrelAlredayTaken = self.GetFieldValue("F2047S2_F207")
            if PrelAlredayTaken > 0:
                self.__Log(f'  Impot payé à l\'étranger = {-PrelAlredayTaken}',3)
                NetTax = NetTax - PrelAlredayTaken

            #Tax Already paid outside
            PrelForfait = self.GetFieldValue("F2042S2_CK")
            if PrelForfait > 0:
                self.__Log(f'  Prelevement Forfaitaire déjà versé = {-PrelForfait}',3)
                NetTax = NetTax - PrelForfait

            #Home emploment
            HEmp = self.GetFieldValue("F2042S7_DB")
            if HEmp > 0:
                HEmp = int(round(HEmp/2))
                self.__Log(f'  Emploi salarié à domicile = {-HEmp}',3)
                NetTax = NetTax - HEmp

            #Only for 2018 ( White Year)
            if self.Year == 2018:
                self.__Log(f'  Credit Impot Modernisation du recouvrement = {-IRThruProgGrid}',3)
                NetTax = NetTax - IRThruProgGrid
            
            self.__Log('\n  IMPOT NET\n',3)
            self.__Log(f'  Total de l\'impot sur le revenu net et reprise eventuelles : {NetTax}\n',3)
            
            self.NetTax = NetTax

            #Calcul prelevements sociaux
            cm = self.GetFieldValue("F2047S2_F222")
            gd = self.GetFieldValue("F2042S3_VG")
            if cm != 0 and gd != 0:
                self.__Log('\n  ------------------------------------',3)
                self.__Log('  PRELEVEMENTS SOCIAUX\n',3)
                self.__Log('\n  Détail des revenus (CSG - CRDS) /  (PREL SOL)',3)
                cm = self.GetFieldValue("F2047S2_F222")
                gd = self.GetFieldValue("F2042S3_VG")
                self.__Log(f'  Revenus de capitaux mobilers : ( {cm} ) / ( {cm} )',3)
                self.__Log(f'  Plus-values et gains divers : ( {gd} ) / ( {gd} )\n',3)
                bi = cm + gd
                self.__Log(f'  BASE IMPOSABLE : ( {bi} ) / ( {bi} )',3)
                micsg = round(bi * 9.70 / 100)
                mips = round(bi * 7.50 / 100)
                self.__Log(f'  Taux de l\'imposition : ( 9,70% ) / ( 7,50% )',3)
                self.__Log(f'  Montant de l\'imposition : ( {micsg} ) / ( {mips} )\n',3)
                tpsn = micsg + mips
                self.__Log(f'  Total des prélévements sociaux nets : {tpsn}',3)

            self.SoldeImpot = 0
            if self.Year > 2018:
                rals = self.GetFieldValue("F2042S8_HV")
                if rals == 0:
                    self.__Log('  You didn\'t provide the 8HV Field in your profile. Remaining Tax to pay can\'t be calculated',3)
                else:
                    #Calcul Solde Impot
                    self.__Log('\n  ------------------------------------',3)
                    self.__Log(f'  CALCUL DU SOLDE DE VOTRE IMPOT POUR {self.Year}\n',3)
                    self.__Log('\n  IMPOT SUR LE REVENU',3)
                    self.__Log(f'\n  Impôt sur le revenu {self.Year} dû : {NetTax}',3)        
                    self.__Log(f'  Retenue à la source prélévée en {self.Year} par vos verseurs de revenus : {-rals}',3)
                    self.__Log(f'  Avance perçue sur les reductions et crédits d\'impôts : {self.GetFieldValue("F2042S7_AvanceReduc")}',3)
                    self.SoldeImpot = NetTax - rals + int(self.GetFieldValue("F2042S7_AvanceReduc"))
                    self.__Log(f'\n  Solde d\'impôt sur les revenus {self.Year}  : {self.SoldeImpot}\n',3)
            elif self.Year == 2018:
                self.SoldeImpot = NetTax
                
            if self.SoldeImpot > 0:
                self.__Log(f'\n  TOTAL DE VOTRE IMPOSITION NETTE RESTANT A PAYER : {self.SoldeImpot}',3)
            elif self.SoldeImpot < 0:
                self.__Log(f'\n  COMPTE TENU DES ELEMENTS QUE VOUS AVEZ DECLARES, LE MONTANT QUI VOUS SERA REMBOURSE EST DE : {self.SoldeImpot}',3)
                               
            #Information complementaires
            self.__Log('\n  ------------------------------------',3)
            self.__Log('  INFORMATIONS COMPLEMENTAIRES',3)
            self.RevFiscalRef = GlobalIncome + RevTauxForfaitaire
            self.__Log(f'  Revenu fiscal de référence : {self.RevFiscalRef}\n',3)

            self.DeficitFoncierAnterieur = self.GetFieldValue("F2044S6_F651")
            self.ListDeficit = self.GetFieldValue("F2044S6_F650a")
            if self.DeficitFoncierAnterieur != 0:
                self.__Log('\n  Reports sur les années suivantes',3)
                self.__Log(f'  Déficits fonciers antérieurs non déduits des autres revenus : {self.DeficitFoncierAnterieur}\n',3)
            
            self.TauxPrelevementSource = round(IRThruProgGrid / self.GetFieldValue("F2042S1_Salaires"),2)
            self.__Log(f'\n  Nouveau taux de prélèvement à la source : {round(self.TauxPrelevementSource*100,1)} %\n',3)

            if result:
                self.bIRCalulated = True
        else:
            self.__Log("Error : Call ProcessForms or Calculate before this method",4)
            result = False

        self.LogLevel = cll
        self.__Log("End of ComputeIR")
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
    def Calculate(self,silent=False):
        self.__Log(f'Beginning of Calculate with silent = {silent}')

        result = True
        self.ResultDict={}
        
        if self.bFormsProcessed == False: result = self.ProcessForms()
        if result:
            self.__Log(f'\n\nStart Processing Tax Calculation ... ',2)
            result = self.ComputeIR(silent=silent)
            if result:
                self.__Log(f'Tax Calculation sucessful ',2)                

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

# -


