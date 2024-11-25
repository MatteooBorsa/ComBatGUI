# ComBat-GUI

A Graphical User Interface to harmonize neuroimaging/genetic data with ComBat.
Developed by Jonny Marques, Lorenzo Castelli, Matteo Borsa, Inês W. Sampaio
# Install

```python
conda create -n myenv python=3.12.7

pip install -r requirements.txt

```
# ComBat functions used

Implemented combat function  from repo: https://github.com/inesws/neurocombat_pyClasse.git
( please refer to that repo for updates on the ComBatHarmonize Class)

Also:
https://github.com/inesws/deconfounders_pyClasse.git

# Usage
In Data dummy example the structure of the two inputs is exemplified;
- Data : should be a csv file with rows = subjects and columns = features ( functional connectivity, MRI ROIs, genetic features etc.)
- Covariates : should be a csv file with FIRST ROW = Columns Names, Other rows = subjects (matching Dat) and columns =  covariates
  e.g: index,Batch,Age,Gender,Diagnosis,CT_avg,CT_std,TIV,abGM,abWM,abCSF
- ComBat Estimates : upload a previous estimated combat model to apply to new test data (it's saved in pickle in the harmonize step) -- usage is still underdevelopment and testing

![image](https://github.com/user-attachments/assets/51004206-0843-46fd-a9ad-d08ba57b5191)

# References
- I. W. Sampaio et al.: "Comparison of Multi-site Neuroimaging Data Harmonization Techniques for Machine Learning Applications," IEEE EUROCON 2023 - 20th International Conference on Smart Technologies, Torino, Italy, 2023, pp. 307-312, doi: 10.1109/EUROCON56442.2023.10198911.
- Fortin, J. P. et al. Harmonization of cortical thickness measurements across scanners and sites. Neuroimage 167, 104–120 (2018).
-  Johnson, W. E., Li, C. & Rabinovic, A. Adjusting batch effects in microarray expression data using empirical Bayes methods. Biostatistics 8, 118–127 (2007).

# ACKNOWLEDGEMENTS
Project funded under the National Recovery and Resilience Plan (NRRP), Mission 4, “Education and Research” - Component 2, “From research to Business” Investiment 3.1 - Call for tender No. 3264 of Dec 28, 2021 of Italian Ministry of University and Research (MUR) funded by the European Union - NextGenerationEU, with award number: Project code IR0000011, Concession Decree No. 117 of June 21,2022 adopted by the Italian Ministry of University and Research, CUP B51E22000150006, Project title “EBRAINS-Italy (European Brain ReseArch INfrastructureS-italy).



