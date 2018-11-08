#!/usr/bin/env python
import sys, os, shutil
from variables import input_variables_bdt, train_files, evalScale
from ROOT import *

TMVA.Tools.Instance()
TMVA.PyMethodBase.PyInitialize()

#Version of classifier
ch = sys.argv[1]
jetcat = sys.argv[2]
ver = sys.argv[3]

#Configurations
sigCut = TCut("njets == 3 && nbjets_m == 2")
bkgCut = TCut("njets == 3 && nbjets_m == 2")
options = "nTrain_Signal=40000:nTrain_Background=65000:nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"

#directory name
rootDir = '/data/users/minerva1993/work/2018_fcnc_RunII2017/finalMVA/mkNtuple/1101/root_/'
configDir = '/home/minerva1993/HEPToolsFCNC/analysis_2017/finalMVA/'
weightDir = 'training/final' + '_' + ch + '_' +jetcat + '_'
scoreDir = 'scores/' + ch + '_' +jetcat + '_'
njets_cut = int(jetcat[1:2]) #Must be jXbX
if njets_cut not in [3,4]:
  print("Check jet category")
  sys.exit()
if len(jetcat) > 3:
  nbjets_cut = int(jetcat[3:4])
  if nbjets_cut not in [2,3,4]:
    print("Check b jet category")
    sys.exit()
else: nbjets_cut = 0

#Check if the model and files already exist
if not os.path.exists( os.path.join(configDir, weightDir+ver, 'weights') ):
  os.makedirs( os.path.join(configDir, weightDir+ver, 'weights') )
if not os.path.exists( os.path.join(configDir, scoreDir+ver) ):
  os.makedirs( os.path.join(configDir, scoreDir+ver) )
for item in os.listdir( os.path.join(configDir, weightDir+ver, 'weights') ) or os.listdir( os.path.join(configDir, scoreDir+ver) ):
  if item.endswith(".C") or item.endswith(".root") or item.endswith("log"):
    #os.remove(os.path.join(os.path.join(configDir, weightDir+ver), item))
    print("Remove previous files or move on to next version!")
    sys.exit()

#Options for data preparation
sig_files, bkg_files = train_files(ch)

#int_vars = []
input_features = []
input_features.extend(input_variables_bdt(jetcat))
input_features.remove('STTT')

fout = TFile("output.root","recreate")
factory = TMVA.Factory("TMVAClassification", fout, "!V:!Silent:Color:DrawProgressBar:AnalysisType=Classification" )

loader = TMVA.DataLoader((weightDir+ver).split("/")[-1])
#for var in int_vars:
#    loader.AddVariable(var, "I")
for var in input_features:
    loader.AddVariable(var, "F")

loader.SetWeightExpression("EventWeight")
loader.AddSpectator("EventCategory")
loader.AddSpectator("njets")
loader.AddSpectator("nbjets_m")

trees = []
for fName in sig_files:
    #if "Hut" in fName: fileWeight = 1
    #elif "Hct" in fName: fileWeight = 0.15
    fileWeight = 1
    f = TFile(rootDir+fName.replace("h5","root"))
    t = f.Get("tree")
    loader.AddSignalTree(t, fileWeight)
    trees.append([f, t])
for fName in bkg_files:
    #if "Hut" in fName: fileWeight = 1
    #elif "Hct" in fName: fileWeight = 0.15
    fileWeight = 1
    f = TFile(rootDir+fName.replace("h5","root"))
    t = f.Get("tree")
    loader.AddBackgroundTree(t, fileWeight)
    trees.append([f, t])

loader.PrepareTrainingAndTestTree(sigCut, bkgCut, options)

factory.BookMethod(loader, TMVA.Types.kBDT, "BDT", "!H:!V:NTrees=600:MinNodeSize=5%:MaxDepth=4:BoostType=Grad:Shrinkage=0.5:SeparationType=GiniIndex:nCuts=30")

factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()
fout.Close()

if not os.path.exists( os.path.join(configDir, weightDir+ver, 'training_bdt.py') ):
  shutil.copy2('training_bdt.py', os.path.join(configDir, weightDir+ver, 'training_bdt.py'))
if not os.path.exists( os.path.join(configDir, weightDir+ver, 'output.root') ):
  shutil.move('output.root', os.path.join(configDir, weightDir+ver))
