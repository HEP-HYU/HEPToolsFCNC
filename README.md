# Analysis for 2017 TT and ST FCNC (H to bb)

Before start, make sure the nuples are located in correct place and update the path.

  * Making file lists, ntuple merge script,  and overall PU weight
```{.Bash}
cd HEPToolsFCNC/analysis_2017/commonTools
python create_input_file_list.py
python countZeroPU.py
source merge_ntuples.sh
```
From TruePVWeight.txt, you can find the overall weights for MC events, which compensate the effect of clean up with respect to TruePV in MC. Copy and paste the lines into MyAnalysis.C, and reco ntuplizers.

  * Control plots without reconstruction
You can make control plots without signal reconstruction to save time and check Data/MC agreement. You need to compile the code, before launch parallel jobs!
```{.Bash}
cd ../fullAna
python create_script.py
source compile.sh
python runNoReco.py
cp doReco/*.root ./
python ratioEMuCombine.py
```
  *Reconstruction
This is for ST FCNC reconstruction using Keras+TF. For TT FCNC, some options in flat ntuplizer must be changes (eg. event selection, b tagging requirements). The flat ntuples for jer assignment is stored in both root and hdf format. root output is kept for BDT test. Default training code uses 0th ST Hct ntuple with classifier version '01'. score and assign folders will be made automatically.
```{.Bash}
#First you make flat ntuples.
../reco/mkNtuple/
source compile.sh
source job_ntuple.sh
python dir_manage.py
#Launch training
cd ../training
python training_kerasTF.py STFCNC 01
#With classifier, run prediction.
python select_model.py STFCNC 01
python evaluation_kerasTF.py STFCNC 01 True model.h5
cat ../commonTools/file_top.txt | xargs -i -P1 -n2 python combi_assign.py True STFCNC 01 #for signal efficiency
cat ../commonTools/file_top.txt | xargs -i -P$(nproc) -n2 python combi_assign.py False STFCNC 01
cat ../commonTools/file_other.txt | xargs -i -P$(nproc) -n2 python combi_assign.py False STFCNC 01
cat ../commonTools/file_syst.txt | xargs -i -P$(nproc) -n2 python combi_assign.py False STFCNC 01
#Plot histograms with reconstruction
cd ../fullAna/
cat ../commonTools/file_top.txt | xargs -i -P$(nproc) -n2 python runReco.py STFCNC01
cat ../commonTools/file_other.txt | xargs -i -P$(nproc) -n2 python runReco.py STFCNC01
cat ../commonTools/file_syst.txt | xargs -i -P$(nproc) -n2 python runReco.py STFCNC01
source job_merge.sh
python ratioEMuCombine.py
cd doReco/STFCNC01
../../plotIt/plotIt -o systematics/ ../../plotIt/configs/config.yml -y
```
  *Final MVA
```{.Bash}
cd /HEPToolsFCNC/finalMVA/mkNtuple
python dir_manage.py
source job_ntuple.sh
cd ../training
python training_kerasTF.py Hct 01 j4b2
cd ..
python evaluation_kerasTF.py Hct 01 j4b2 model_35_0.7971.h5
```



  *Todo list
1. Rearrange BDT codes for reco
2. Final MVA
3. Systematic-ready

  *All rights for plotIt: https://github.com/cp3-llbb/plotIt/
