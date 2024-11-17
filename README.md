# ComBat-GUI

A Graphical User Interface to harmonize neuroimaging/genetic data with ComBat.

# Install

´´´python
conda create -n myenv python=3.12.7

pip install -r requirements.txt

´´´
# ComBat functions used

cite: I. W. Sampaio et al.: "Comparison of Multi-site Neuroimaging Data Harmonization Techniques for Machine Learning Applications," IEEE EUROCON 2023 - 20th International Conference on Smart Technologies, Torino, Italy, 2023, pp. 307-312, doi: 10.1109/EUROCON56442.2023.10198911.

from repo: https://github.com/inesws/deconfounders_pyClasse.git
( please refer to that repo for updates on ComBatHarmonize classe )

# Usage

- Data : should be a csv file with rows = subjects and columns = features ( functional connectivity, MRI ROIs, genetic features etc.)
- Covariates : should be a csv file with FIRST ROW = Columns Names, Other rows = subjects (matching Dat) and columns =  covariates
  e.g: index,Batch,Age,Gender,Diagnosis,CT_avg,CT_std,TIV,abGM,abWM,abCSF
- ComBat Estimates : upload a previous estimated combat model to apply to new test data (it's saved in pickle in the harmonize step) -- usage is still underdevelopment and testing

# References
- I. W. Sampaio et al.: "Comparison of Multi-site Neuroimaging Data Harmonization Techniques for Machine Learning Applications," IEEE EUROCON 2023 - 20th International Conference on Smart Technologies, Torino, Italy, 2023, pp. 307-312, doi: 10.1109/EUROCON56442.2023.10198911.
- Fortin, J. P. et al. Harmonization of cortical thickness measurements across scanners and sites. Neuroimage 167, 104–120 (2018).
-  Johnson, W. E., Li, C. & Rabinovic, A. Adjusting batch effects in microarray expression data using empirical Bayes methods. Biostatistics 8, 118–127 (2007).
