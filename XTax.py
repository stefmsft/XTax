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
    def __init__(self, year=2010, loglevel=3):
        self.LogLevel = loglevel
        self.__Log("Beginning of Init")
        self.__Reset()
        self.Year = year
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

        self.Year = 0
        self.bProfileLoaded = False
        self.bTaxDefLoaded = False
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
        
        return

#
#  Function Log
#
#  Params: String to log
#          level of the logging
#
#  Description : If the LogLevel is compatible, the string is written to the console
#
#  Return: Nothing
#
    def __Log(self, string, level=1):
        if level >= self.LogLevel:
            print (string)
        return

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
                                            fieldname = curform + cursection + k3
                                            self.FieldDict[fieldname]=dv3
                                            self.__Log(f'Field {fieldname}: {dv3}',2)
                                else:
                                    self.VarDict[k2]=dv2
                                    self.__Log(f'Variable {k2}: {dv2}',2)            
            
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
        
        carryto2042List=""
        finalresultList=""
        if self.RawTaxDef != None:
            for k in self.RawTaxDef["Tax"]:
                    if k.lower() != "forms":
                        keyname=f'TDV_G_{k.lower()}'
                        self.GVarTaxDefDict[keyname]=self.RawTaxDef["Tax"][k]
            stepperseq=0
            for i, val in enumerate(self.RawTaxDef["Tax"]["Forms"]):
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
            
        self.__Log(f'End of GetSectionFromName')
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
            
        self.__Log(f'End of GetActionFromName')
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
#
    def __ProcesSteps(self,Steps,CurForm):
        self.__Log(f'Beginning of ProcesSteps')

        currentfieldnamecontext=f"{CurForm}"
        currentloopext=""
        Sg=Steps.groupby('Section')
        print ("Loop by Sections")

        # Focus on each section of the Form
        for cursection in sorted(Sg.groups.keys()):
            print (f'Processing Section : {cursection}')
            currentfieldnamecontext = f"F{CurForm}S{cursection}"
            print (f"Current Field Prefix {currentfieldnamecontext}")
            
            StepsForCurSection = Steps[Steps['Section']==cursection]

            # Look for loopon
            sFor="loopon"
            if not StepsForCurSection[StepsForCurSection['Action']==sFor].empty:
                dfb = StepsForCurSection[StepsForCurSection['Action']==sFor].index.values.astype(int)[0]
                currentloopext=StepsForCurSection.loc[dfb,"Step"]
                print ("Loop on detected")
                print (f'Loop On : {currentloopext}')
                
            # Look for inputfields
            sFor="reqfields"
            if not StepsForCurSection[StepsForCurSection['Action']==sFor].empty:
                dfb = StepsForCurSection[StepsForCurSection['Action']==sFor].index.values.astype(int)[0]
                print ("Required Fields detected")
                ifv = StepsForCurSection.loc[dfb,"Step"].split(",")
                for i in range(len(ifv)):
                    ifv[i] = f"{currentfieldnamecontext}{ifv[i]}_{currentloopext}"
                print (f'List of Required fields : {ifv}')

        self.__Log(f'End of ProcesSteps')
        return

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
        result = False
        self.ResultDict={}
        
        if self.bProfileLoaded:
            if self.bTaxDefLoaded == False: self.LoadTaxDef()
            if self.bTaxDefLoaded:
                if None != self.GVarTaxDefDict["TDV_G_processingorder"]:
                    ProcOrdList = self.GVarTaxDefDict["TDV_G_processingorder"].split(',')
                    for Form in ProcOrdList:
                        for ProForm in self.FormList:
                            if ProForm.lower() == Form.lower():
                                self.__Log(f'Processing {Form} ... ',3)
                                ExecSteps = self.__LoadStepsFor(Form)
                                self.ResultDict = self.__ProcesSteps(ExecSteps,Form)
                                self.bTaxCalculted = True

        self.__Log("End of Calculate")
        return

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


