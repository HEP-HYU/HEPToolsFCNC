#!/usr/bin/env python
import os, sys
from ROOT import *
from array import array
from subprocess import call
from os.path import isfile
import numpy as np

# Setup TMVA
TMVA.Tools.Instance()
TMVA.PyMethodBase.PyInitialize()
reader = TMVA.Reader("Color:!Silent")

ch = 'Hct1'
#ch = 'Hut1'

tuples = sys.argv[1]

# Load data
data = TFile.Open('/home/minerva1993/fcnc/analysis_jw/tmva/v7/mkNtuple_v7/'+tuples)
data_tree = data.Get('tmva_tree')

target = TFile('output_'+ch+'_'+tuples,'RECREATE')
tree = TTree("tree","tree")

branches = {}
for branch in data_tree.GetListOfBranches():
  branchName = branch.GetName()
  if branchName not in ["lepDPhi", "bjetmDR", "bjetmDEta", "bjetmDPhi", "dibjetsMass", "bjetPt_dibjetsm", "cjetPt", "transverseMass", "jet1phi", "jet2phi", "jet3phi", "jet4phi", "KinLepWMass", "KinLepTopMass", "KinHadWMass", "KinHadTopMass", "FCNHKinLepWMass", "FCNHKinLepTopMass", "FCNHKinHMass", "FCNHKinHucTopMass", "M3LepWMass", "M3HadWMass", "M3HMass", "M3DR", "M3LepTopMass", "M3HucTopMass", "DRlepWphi", "DRjet0phi", "DRjet1phi", "DRjet2phi", "DRjet3phi", "DRjet12phi", "DRjet23phi", "DRjet31phi", "DRlepTphi", "DRhadTphi", "EventWeight", "totnevt", "nevt", "GoodPV", "EventCategory","GenMatch",
  "ncjets_m", "missingET",
  "jet1pt", "jet2pt", "jet3pt", "jet4pt",
  "jet1eta", "jet2eta", "jet3eta", "jet4eta",
  "jet1m", "jet2m", "jet3m", "jet4m",
  "jet1csv", "jet2csv", "jet3csv", "jet4csv",
  "jet1cvsl", "jet2cvsl", "jet3cvsl", "jet4cvsl", 
  "jet1cvsb","jet2cvsb", "jet3cvsb", "jet4cvsb",
  #"DRlepWpt", "DRlepWeta", "DRlepWdeta", "DRlepWdphi", "DRlepWm",
  #"DRjet0pt", "DRjet0eta", "DRjet0m", "DRjet0csv","DRjet0cvsl","DRjet0cvsb",
  #"DRlepTpt", "DRlepTeta", "DRlepTdeta","DRlepTdphi","DRlepTm",
  #"DRjet0cvsl", "DRjet1cvsl","DRjet2cvsl","DRjet3cvsl",
  #"DRjet0cvsb", "DRjet1cvsb", "DRjet2cvsb", "DRjet3cvsb", 
  ]:
      branches[branchName] = array('f', [-999])
      reader.AddVariable(branchName, branches[branchName])
      data_tree.SetBranchAddress(branchName, branches[branchName])

  elif branchName in ["GoodPV", "EventCategory", "GenMatch"]:
    branches[branchName] = array('f', [-999])
    reader.AddSpectator(branchName, branches[branchName])
    #data_tree.SetBranchAddress("GoodPV", branches["GoodPV"])

reader.BookMVA('PyKeras', TString('/home/minerva1993/fcnc/analysis_jw/tmva/v7/keras7_'+ch+'/weights/TMVAClassification_Keras_TF.weights.xml'))
reader.BookMVA('BDT', TString('/home/minerva1993/fcnc/analysis_jw/tmva/v7/keras7_'+ch+'/weights/TMVAClassification_BDT.weights.xml'))

print "processing "+tuples
totalevt = data_tree.GetEntries()
print "this sample contains "+str(totalevt)+" events"

score1 = np.zeros(1, dtype=float)
score2 = np.zeros(1, dtype=float)
event_weight = np.zeros(1, dtype=float)
pileup =  np.zeros(1, dtype=int)
category = np.zeros(1, dtype=int)
genMatch = np.zeros(1, dtype=int)

tree.Branch('KerasScore', score1, 'KerasScore/D')
tree.Branch('BDTScore', score2, 'BDTScore/D')
tree.Branch('Event_Weight', event_weight, 'Event_Weight/D')
tree.Branch("PU", pileup, 'PU/I')
tree.Branch("category", category, 'category/I')
tree.Branch("genMatch", genMatch, 'genMatch/I')

for i in xrange(totalevt-1):
  data_tree.GetEntry(i)
  nevt = data_tree.GetLeaf("nevt").GetValue(0)

  if tuples in ["tmva_SingleLepton_Run2016.root"]:
    score1[0] = reader.EvaluateMVA('PyKeras')
    score2[0] = reader.EvaluateMVA('BDT')
    event_weight[0] = data_tree.EventWeight
    pileup[0] = data_tree.GoodPV
    category[0] = data_tree.EventCategory
    genMatch[0] = data_tree.GenMatch
  else:
    if nevt == i:
      if tuples in ["tmva_wjets.root", "tmva_zjets10to50.root", "tmva_zjets.root"]:
        score1[0] = reader.EvaluateMVA('PyKeras')
        score2[0] = reader.EvaluateMVA('BDT')
        event_weight[0] = data_tree.EventWeight
        pileup[0] = data_tree.GoodPV
        category[0] = data_tree.EventCategory
        genMatch[0] = data_tree.GenMatch
        #print data_tree.GoodPV
        #print data_tree.GetLeaf("nevt").GetValue(0)
        #print i
      else:
        if float(nevt)/totalevt > 0.8:
          score1[0] = reader.EvaluateMVA('PyKeras')
          score2[0] = reader.EvaluateMVA('BDT')
          event_weight[0] = data_tree.EventWeight
          pileup[0] = data_tree.GoodPV
          category[0] = data_tree.EventCategory
          genMatch[0] = data_tree.GenMatch
          #if i%1000 == 0: print data_tree.GoodPV
          #if i%1000 == 0: print data_tree.GetLeaf("nevt").GetValue(0)
          #if i%1000 == 0: print i
        else:
          score1[0] = 2
          score2[0] = 2
          event_weight[0] = 10
          pileup[0] = -1
          category[0] = -1
      
  s = str(i)

  if totalevt > 100000:
    if i%20000 == 0: print "processing "+tuples+" "+s
  elif totalevt > 10000 and nevt < 100000:
    if i%10000 == 0: print "processing "+tuples+" "+s
  elif totalevt < 10000:
    if i%1000 == 0: print "processing "+tuples+" "+s

  tree.Fill()

  if i == totalevt:
    del score1, score2, branches

target.Write()
target.Close()