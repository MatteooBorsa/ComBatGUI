import customtkinter
import numpy as np
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import pandas as pd
import scipy.io
import csv
import seaborn as sns  
from tkinter import PhotoImage
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import new_confounder_correction_classes_combat_modmean_lr_normal
from new_confounder_correction_classes_combat_modmean_lr_normal import ComBatHarmonization
import umap
import umap.umap_ as umap
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import random
import pickle


def creaPopUpInfoPag1():
    global framePopUpInfoPag1, buttonXPopUpInfoPag1
    
    buttonInfoPag1.configure(state=DISABLED, fg_color='grey30', text_color_disabled='grey80')
    framePopUpInfoPag1=customtkinter.CTkFrame(master=root, width=600, height=300, fg_color='white', bg_color='grey25')
    framePopUpInfoPag1.place(x=300, y=150)
    labelRequirements=customtkinter.CTkLabel(master=framePopUpInfoPag1, text='REQUIREMENTS:', font=('Roboto', 24), text_color='black', bg_color='white')
    labelRequirements.place(x=210, y=20)
    labelPopUpInfoPag1=customtkinter.CTkLabel(master=framePopUpInfoPag1, text='-To be able to HARMONIZE the dataset, you need to provide all the necessary inputs:\nthe DATASET file, the COVARIATES file, the site of origin, and the covariates to preserve.\n\n-The number of subjects in the DATASET and COVARIATES files must be the same\n\n-The DATASET and COVARIATES files must be in .CSV format and must include\na header in the first row with the column names\n\n-The ESTIMATES file is not mandatory, but if provided it allows\nyou to skip the model fitting phase\n\n-The ESTIMATES file must be in .PKL format', text_color='black', font=('Roboto', 14), bg_color='white')
    labelPopUpInfoPag1.place(x=10, y=80)
    buttonXPopUpInfoPag1=customtkinter.CTkButton(master=framePopUpInfoPag1, text='x', font=('Roboto', 30), text_color='red', bg_color='white', fg_color='white', hover_color='grey80', height=10, width=10, command=lambda:(framePopUpInfoPag1.destroy(), buttonInfoPag1.configure(state=NORMAL, fg_color='blue', text_color='white')))
    buttonXPopUpInfoPag1.place(x=565, y=5)
    
def creaPopUpInfoPag2():
    global framePopUpInfoPag2, buttonXPopUpInfoPag2
    
    buttonInfoPag2.configure(state=DISABLED, fg_color='grey25', text_color_disabled='grey80')
    framePopUpInfoPag2=customtkinter.CTkFrame(master=framePag2, width=600, height=350, fg_color='white', bg_color='grey25')
    framePopUpInfoPag2.place(x=320, y=50)
    labelInfo=customtkinter.CTkLabel(master=framePopUpInfoPag2, text='INFO:', font=('Roboto', 24), text_color='black', bg_color='white')
    labelInfo.place(x=300, y=20)
    labelPopUpInfoPag2=customtkinter.CTkLabel(master=framePopUpInfoPag2, text='PCA (Principal Component Analysis) is a statistical technique used to reduce\nthe dimensionality of a dataset while preserving most of the variability present in the data.\n\nUMAP (Uniform Manifold Approximation and Projection) is a dimensionality\nreduction technique that aims to preserve both the local and global structure of the data.\n\nYou can freely use PCA and UMAP to evaluate whether the harmonization\nof the dataset has been carried out correctly.\n\n----------\n\nBy clicking the download buttons, you will get a .CSV file\nwith the harmonized dataset and a .PKL file with the estimates.', text_color='black', font=('Roboto', 14), bg_color='white')
    labelPopUpInfoPag2.place(x=10, y=80)
    buttonXPopUpInfoPag2=customtkinter.CTkButton(master=framePopUpInfoPag2, text='x', font=('Roboto', 30), text_color='red', bg_color='white', fg_color='white', hover_color='grey80', height=10, width=10, command=lambda:(framePopUpInfoPag2.destroy(), buttonInfoPag2.configure(state=NORMAL, fg_color='blue', text_color='white')))
    buttonXPopUpInfoPag2.place(x=565, y=5)

def creaPopUpErrFile():
    global yPopUpErrFile, framePopUpErrFile
    yPopUpErrFile-=60
    
    if yPopUpErrFile >=200:
        framePopUpErrFile.place(x=575, y=yPopUpErrFile)
        root.after(10, creaPopUpErrFile)
def togliPopUpErrFile():
    global yPopUpErrFile, framePopUpErrFile
    yPopUpErrFile+=60
    
    if yPopUpErrFile <=700:
        framePopUpErrFile.place(x=575, y=yPopUpErrFile)
        root.after(10, togliPopUpErrFile)
        
def dowloadDataset():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", 
                                             filetypes=[("CSV files", "*.csv")])
    if file_path:
        np.savetxt(file_path, dataset_harmonized , delimiter=',')  # Salva la matrice come CSV
        datasetScaricatoCorrettamente=customtkinter.CTkLabel(master=framePag2, text='✔️', font=('Roboto', 30), text_color='green', bg_color='grey25')
        datasetScaricatoCorrettamente.place(x=570, y=485)

def dowloadEstimates():
    
    file_path = filedialog.asksaveasfilename(defaultextension=".pkl", filetypes=[("Pickle files", "*.pkl")])    
    if file_path:
    
        save_object(fitted_model,file_path)
        
        estimatesScaricatoCorrettamente=customtkinter.CTkLabel(master=framePag2, text='✔️', font=('Roboto', 30), text_color='green', bg_color='grey25', height=20)
        estimatesScaricatoCorrettamente.place(x=1100, y=485)
    

    
def azzeraSubmitBatch():
    global checkSubmitBatch
    checkSubmitBatch=0
    if numPazientiCovariate==numPazientiDataset:
        checkNumPazienti=1
    else:
        checkNumPazienti=0
    if MATRICEDATASET is not None and MATRICECOVARIATE is not None and checkSubmitBatch==1 and checkSubmitNum==1 and checkSubmitCat==1 and checkNumPazienti==1:
        buttonArmonizza.configure(state=NORMAL, fg_color='green4')
    else:
        buttonArmonizza.configure(state=DISABLED, fg_color='grey35', text_color_disabled='grey')
def azzeraSubmitNum():
    global checkSubmitNum
    checkSubmitNum=0
    if numPazientiCovariate==numPazientiDataset:
        checkNumPazienti=1
    else:
        checkNumPazienti=0
    if MATRICEDATASET is not None and MATRICECOVARIATE is not None and checkSubmitBatch==1 and checkSubmitNum==1 and checkSubmitCat==1 and checkNumPazienti==1:
        buttonArmonizza.configure(state=NORMAL, fg_color='green4')
    else:
        buttonArmonizza.configure(state=DISABLED, fg_color='grey35', text_color_disabled='grey')
def azzeraSubmitCat():
    global checkSubmitCat
    checkSubmitCat=0
    if numPazientiCovariate==numPazientiDataset:
        checkNumPazienti=1
    else:
        checkNumPazienti=0
    if MATRICEDATASET is not None and MATRICECOVARIATE is not None and checkSubmitBatch==1 and checkSubmitNum==1 and checkSubmitCat==1 and checkNumPazienti==1:
        buttonArmonizza.configure(state=NORMAL, fg_color='green4')
    else:
        buttonArmonizza.configure(state=DISABLED, fg_color='grey35', text_color_disabled='grey')

def attivaSubmitBatch():
    global checkSubmitBatch
    checkSubmitBatch=1
    if numPazientiCovariate==numPazientiDataset:
        checkNumPazienti=1
    else:
        checkNumPazienti=0
    if MATRICEDATASET is not None and MATRICECOVARIATE is not None and checkSubmitBatch==1 and checkSubmitNum==1 and checkSubmitCat==1 and checkNumPazienti==1:
        buttonArmonizza.configure(state=NORMAL, fg_color='green4')
    else:
        buttonArmonizza.configure(state=DISABLED, fg_color='grey35', text_color_disabled='grey')
def attivaSubmitNum():
    global checkSubmitNum
    checkSubmitNum=1
    if numPazientiCovariate==numPazientiDataset:
        checkNumPazienti=1
    else:
        checkNumPazienti=0
    if MATRICEDATASET is not None and MATRICECOVARIATE is not None and checkSubmitBatch==1 and checkSubmitNum==1 and checkSubmitCat==1 and checkNumPazienti==1:
        buttonArmonizza.configure(state=NORMAL, fg_color='green4')
    else:
        buttonArmonizza.configure(state=DISABLED, fg_color='grey35', text_color_disabled='grey')
def attivaSubmitCat():
    global checkSubmitCat
    checkSubmitCat=1
    if numPazientiCovariate==numPazientiDataset:
        checkNumPazienti=1
    else:
        checkNumPazienti=0
    if MATRICEDATASET is not None and MATRICECOVARIATE is not None and checkSubmitBatch==1 and checkSubmitNum==1 and checkSubmitCat==1 and checkNumPazienti==1:
        buttonArmonizza.configure(state=NORMAL, fg_color='green4')
    else:
        buttonArmonizza.configure(state=DISABLED, fg_color='grey35', text_color_disabled='grey')

def azzeraDATASET():
    global MATRICEDATASET, MATRICECOVARIATE
    MATRICEDATASET=None
    if numPazientiCovariate==numPazientiDataset:
        checkNumPazienti=1
    else:
        checkNumPazienti=0
    if MATRICEDATASET is not None and MATRICECOVARIATE is not None and checkSubmitBatch==1 and checkSubmitNum==1 and checkSubmitCat==1 and checkNumPazienti==1:
        buttonArmonizza.configure(state=NORMAL, fg_color='green4')
    else:
        buttonArmonizza.configure(state=DISABLED, fg_color='grey35', text_color_disabled='grey')
def azzeraCOVARIATE():
    if numPazientiCovariate==numPazientiDataset:
        checkNumPazienti=1
    else:
        checkNumPazienti=0
    global MATRICEDATASET, MATRICECOVARIATE
    MATRICECOVARIATE=None
    if MATRICEDATASET is not None and MATRICECOVARIATE is not None and checkSubmitBatch==1 and checkSubmitNum==1 and checkSubmitCat==1 and checkNumPazienti==1:
        buttonArmonizza.configure(state=NORMAL, fg_color='green4')
    else:
        buttonArmonizza.configure(state=DISABLED, fg_color='grey35', text_color_disabled='grey')
def azzeraESTIMATES():
    global MATRICEESTIMATES
    MATRICEESTIMATES=None
    
def seleziona_file_e_assegna_matrice_INPUTDATASET():
    # Apre la finestra di dialogo per selezionare un file CSV o MAT
    filepath = filedialog.askopenfilename(filetypes=[("File CSV", ".csv")])   #, ("File MAT", ".mat")
    global MATRICEDATASET, MATRICECOVARIATE, numPazientiDataset
    if filepath:  # Assicura che il percorso del file sia valido
        if filepath.endswith('.csv'):
            MATRICEDATASET = leggi_csv_e_restituisci_matrice_CSV(filepath)
            buttonDataset.configure(state='disabled', fg_color='grey30')
            fileNameDataset = filepath.split("/")[-1]
            frameAnteprimaDataset=customtkinter.CTkFrame(master=root, height=50, width=250, bg_color='grey25', fg_color='white')
            frameAnteprimaDataset.place(x=300, y=90)
            if len(fileNameDataset) >= 20:
                fileNameDataset = fileNameDataset[:19] + "..."
            labelFileDataset = customtkinter.CTkLabel(master=root, text=f'{fileNameDataset}', font=('Roboto', 14), bg_color='white', fg_color='white', text_color='black')
            labelFileDataset.place(x=360, y=100)
            imageCSVDataset=customtkinter.CTkImage(light_image=Image.open('IconaCSV.png'), size=(40, 40))
            labelImageCSVDataset=customtkinter.CTkLabel(master=root, text='', image=imageCSVDataset)
            labelImageCSVDataset.place(x=305, y=95)
            
            numPazientiDataset=MATRICEDATASET.shape[0]
            numFeaturesDataset=MATRICEDATASET.shape[1]
            labelNumeroPazientiDataset=customtkinter.CTkLabel(master=root, text=f'Number of subjects = {numPazientiDataset}', text_color='white', font=('Roboto', 16), bg_color='grey25')
            labelNumeroPazientiDataset.place(x=300, y=150)
            labelNumeroFeaturesDataset=customtkinter.CTkLabel(master=root, text=f'Number of features = {numFeaturesDataset}', text_color='white', font=('Roboto', 16), bg_color='grey25')
            labelNumeroFeaturesDataset.place(x=300, y=175)
            
            if numPazientiCovariate==numPazientiDataset:
                checkNumPazienti=1
            else:
                checkNumPazienti=0

            buttonXDataset = customtkinter.CTkButton(master=root, text='x', font=('Roboto', 20), bg_color='white', fg_color='white', text_color='red', height=10, width=10, hover_color='DodgerBlue3',
                                                     command=lambda:(labelNumeroPazientiDataset.destroy(), labelNumeroFeaturesDataset.destroy(), buttonXDataset.destroy(), buttonDataset.configure(state='normal', fg_color='blue4'), 
                                                                     frameAnteprimaDataset.destroy(), labelFileDataset.destroy(), labelImageCSVDataset.destroy(), buttonArmonizza.configure(state=DISABLED, fg_color='red', text_color_disabled='grey'),
                                                                     azzeraDATASET(), framePopUpNumPaz.destroy()))
            buttonXDataset.place(x=525, y=90)
            

            if checkNumPazienti==0 and numPazientiCovariate!=0:
                framePopUpNumPaz=customtkinter.CTkFrame(master=root, width=150, height=150, fg_color='white', bg_color='grey30')
                framePopUpNumPaz.place(x=810, y=170)
                imageWarningPaz=customtkinter.CTkImage(light_image=Image.open('IconaWarning.png'), size=(40, 40))
                labelWarningPaz=customtkinter.CTkLabel(master=framePopUpNumPaz, text='', image=imageWarningPaz, bg_color='white')
                labelWarningPaz.place(x=55, y=10)
                labelPopUpNumPaz=customtkinter.CTkLabel(master=framePopUpNumPaz , text='Error:\n\nTHE NUMBER\nOF SUBJECTS\nDOES NOT MATCH', text_color='red', font=('Roboto', 12), bg_color='white')
                labelPopUpNumPaz.place(x=20, y=55)
                buttonXPopUpNumPaz=customtkinter.CTkButton(master=framePopUpNumPaz, text='x', font=('Roboto', 18), text_color='red', bg_color='white', fg_color='white', hover_color='grey30', height=10, width=10, command=lambda:framePopUpNumPaz.destroy())
                buttonXPopUpNumPaz.place(x=125, y=5)

            if MATRICEDATASET is not None and MATRICECOVARIATE is not None and checkSubmitBatch==1 and checkSubmitNum==1 and checkSubmitCat==1 and checkNumPazienti==1:
                buttonArmonizza.configure(state=NORMAL, fg_color='green4')
            else:
                buttonArmonizza.configure(state=DISABLED, fg_color='grey35', text_color_disabled='grey')

def estraiElencoCovariateBatch():
    global selectedBatch
    selectedBatch = [selectedValue.get()]
    print(selectedBatch)
def stampaElencoCovariateNum():
    global selectedNum
    selectedNum = [elencoCovariate[i] for i, var in enumerate(elencoCovariateNum) if var.get() == 'on']
    print(selectedNum)
def stampaElencoCovariateCat():
    global selectedCat
    selectedCat = [elencoCovariate[i] for i, var in enumerate(elencoCovariateCat) if var.get() == 'on']
    print(selectedCat)

def creaSpuntaBatch():
    global frameSpuntaBatch, labelSpuntaBatch
    frameSpuntaBatch=customtkinter.CTkFrame(master=frame2DxUpPag1 , width=200, height=270, bg_color='grey25', fg_color='transparent')
    frameSpuntaBatch.place(x=10, y=60)
    labelSpuntaBatch=customtkinter.CTkLabel(master=frame2DxUpPag1 , text='✔️', font=('Roboto', 30), text_color='green')
    labelSpuntaBatch.place(x=90, y=150)
def creaSpuntaNum():
    global frameSpuntaNum, labelSpuntaNum
    frameSpuntaNum=customtkinter.CTkFrame(master=frame2DxUpPag1 , width=200, height=270, bg_color='grey25', fg_color='transparent')
    frameSpuntaNum.place(x=200, y=60)
    labelSpuntaNum=customtkinter.CTkLabel(master=frame2DxUpPag1 , text='✔️', font=('Roboto', 30), text_color='green')
    labelSpuntaNum.place(x=275, y=150)
def creaSpuntaCat():
    global frameSpuntaCat, labelSpuntaCat
    frameSpuntaCat=customtkinter.CTkFrame(master=frame2DxUpPag1 , width=200, height=270, bg_color='grey25', fg_color='transparent')
    frameSpuntaCat.place(x=380, y=60)
    labelSpuntaCat=customtkinter.CTkLabel(master=frame2DxUpPag1 , text='✔️', font=('Roboto', 30), text_color='green')
    labelSpuntaCat.place(x=470, y=150)
        
def seleziona_file_e_assegna_matrice_INPUTCOVARIATE():
    # Apre la finestra di dialogo per selezionare un file CSV o MAT
    filepath = filedialog.askopenfilename(filetypes=[("File CSV", ".csv"), ("File MAT", ".mat")])
    global selectedValue
    global MATRICECOVARIATE, MATRICEDATASET, elencoCovariate, frame2DxUpPag1, labelErrorNumColonneCovariate 
    global elencoCovariateBatch, elencoCovariateNum, elencoCovariateCat, numPazientiCovariate
    global yPopUpErrFile, framePopUpErrFile
    global yPopUpNumPaz, framePopUpNumPaz

    if filepath:  # Assicura che il percorso del file sia valido
        if filepath.endswith('.csv'):

            MATRICECOVARIATE = leggi_csv_e_restituisci_matrice_CSV(filepath)
            
            numColonneCovariate=MATRICECOVARIATE.shape[1]
            if numColonneCovariate<100:
                
                frameErrorNumColonneCovariate=customtkinter.CTkFrame(master=root, height=50, width=250, bg_color='grey25', fg_color='grey25')
                frameErrorNumColonneCovariate.place(x=30, y=350)
                
                buttonCovariates.configure(state='disabled', fg_color='grey30')
                
                fileNameCovariate = filepath.split("/")[-1]
                frameAnteprimaCovariate=customtkinter.CTkFrame(master=root, height=50, width=250, bg_color='grey25', fg_color='white')
                frameAnteprimaCovariate.place(x=300, y=290)
                
                if len(fileNameCovariate) >= 20:
                    fileNameCovariate = fileNameCovariate[:19] + "..."
                    
                labelFileCovariate = customtkinter.CTkLabel(master=root, text=f'{fileNameCovariate}', font=('Roboto', 14), bg_color='white', fg_color='white', text_color='black')
                labelFileCovariate.place(x=360, y=300)
                
                imageCSVCovariate=customtkinter.CTkImage(light_image=Image.open('IconaCSV.png'), size=(40, 40))
                labelImageCSVCovariate=customtkinter.CTkLabel(master=root, text='', image=imageCSVCovariate)
                labelImageCSVCovariate.place(x=305, y=295)
                  
                elencoCovariate = np.empty_like(MATRICECOVARIATE.columns, dtype=object)
    
                for i, nome_colonna in enumerate(MATRICECOVARIATE.columns):
                    elencoCovariate[i] = nome_colonna
                
                frame2DxUpPag1=customtkinter.CTkFrame(master = root ,height=380 , width = 580, fg_color='grey25', bg_color='grey30')
                frame2DxUpPag1.place(x = 600, y = 40)
                
                numPazientiCovariate=MATRICECOVARIATE.shape[0]
                numCovariate=MATRICECOVARIATE.shape[1]
                labelNumeroPazientiCovariate=customtkinter.CTkLabel(master=root, text=f'Number of subjects = {numPazientiCovariate}', text_color='white', font=('Roboto', 16), bg_color='grey25')
                labelNumeroPazientiCovariate.place(x=300, y=350)
                labelNumeroCovariate=customtkinter.CTkLabel(master=root, text=f'Number of covariates = {numCovariate}', text_color='white', font=('Roboto', 16), bg_color='grey25')
                labelNumeroCovariate.place(x=300, y=375)
                
                if numPazientiCovariate==numPazientiDataset:
                    checkNumPazienti=1
                else:
                    checkNumPazienti=0
    
                buttonXCovariate = customtkinter.CTkButton(master=root, text='x', font=('Roboto', 20), bg_color='white', fg_color='white', text_color='red', height=10, width=10, hover_color='DodgerBlue3',
                                                         command=lambda:(labelNumeroPazientiCovariate.destroy(), labelNumeroCovariate.destroy(), buttonXCovariate.destroy(), buttonCovariates.configure(state=NORMAL, fg_color='blue4'), frameAnteprimaCovariate.destroy(), labelFileCovariate.destroy(), labelImageCSVCovariate.destroy(), buttonArmonizza.configure(state=DISABLED, fg_color='red', text_color_disabled='grey'), azzeraCOVARIATE(), frame2DxUpPag1.destroy(), 
                                                                         azzeraSubmitBatch(), azzeraSubmitNum(), azzeraSubmitCat(), framePopUpNumPaz.destroy()))
                buttonXCovariate.place(x=525, y=290)
                
                frameCaricamento=customtkinter.CTkFrame(master = root ,height=380 , width = 580, fg_color='grey25', bg_color='grey30')
                frameCaricamento.place(x = 600, y = 40)
                scrittaCaricamentoCovariate=customtkinter.CTkLabel(master=frameCaricamento, text='loading the covariates file', text_color='white', font=('Roboto', 20), bg_color='grey25')
                scrittaCaricamentoCovariate.place(x=175, y=100)
                progressBarCovariate=customtkinter.CTkProgressBar(master=frameCaricamento, height=30, width=350, border_color='white', border_width=2, progress_color='blue')
                progressBarCovariate.place(x=125, y=150)
                randomNum=random.randint(10, 100)
                for i in range(randomNum):
                    time.sleep(0.001)
                    progressBarCovariate.set(i / 100)
                    frameCaricamento.update_idletasks()
                    percentualeCovariate=customtkinter.CTkLabel(master=frameCaricamento, text=f'{i}' + '%', text_color='white', font=('Roboto', 20), bg_color='grey25')
                    percentualeCovariate.place(x=275, y=200)
    
                labelBatch=customtkinter.CTkLabel(master=frame2DxUpPag1 , text='Site of origin:', font=('Roboto', 16), text_color='white', bg_color='grey25')
                labelBatch.place(x=10, y=5)
                labelCovariataNum1=customtkinter.CTkLabel(master=frame2DxUpPag1 , text='Numeric covariates', font=('Roboto', 16), text_color='white', bg_color='grey25')
                labelCovariataNum1.place(x=200, y=5)
                labelCovariataNum2=customtkinter.CTkLabel(master=frame2DxUpPag1 , text='you want to preserve:', font=('Roboto', 16), text_color='white', bg_color='grey25')
                labelCovariataNum2.place(x=200, y=30)
                labelCovariataCat1=customtkinter.CTkLabel(master=frame2DxUpPag1 , text='Cathegorical covariates', font=('Roboto', 16), text_color='white', bg_color='grey25')
                labelCovariataCat1.place(x=395, y=5)
                labelCovariataCat1=customtkinter.CTkLabel(master=frame2DxUpPag1 , text='you want to preserve:', font=('Roboto', 16), text_color='white', bg_color='grey25')
                labelCovariataCat1.place(x=395, y=30)
                
                frameScrollboxBatch=customtkinter.CTkScrollableFrame(master=frame2DxUpPag1, width=150, height=250, bg_color='grey25', fg_color='grey30')
                frameScrollboxBatch.place(x=10, y=60)
                frameScrollboxNum=customtkinter.CTkScrollableFrame(master=frame2DxUpPag1, width=150, height=250, bg_color='grey25', fg_color='grey30')
                frameScrollboxNum.place(x=200, y=60)
                frameScrollboxCat=customtkinter.CTkScrollableFrame(master=frame2DxUpPag1, width=150, height=250, bg_color='grey25', fg_color='grey30')
                frameScrollboxCat.place(x=395, y=60)
                
                selectedValue=customtkinter.StringVar(value=' ')
                for i in range(len(elencoCovariate)):
                    checkCovariata=customtkinter.CTkRadioButton(master=frameScrollboxBatch , text=f'{elencoCovariate[i]}', text_color='white', font=('Roboto', 14), variable=selectedValue, value=elencoCovariate[i])
                    checkCovariata.pack(ipady=10)
                buttonXSubmitBatch=customtkinter.CTkButton(master=frame2DxUpPag1 , text='x', text_color='white', font=('Roboto', 20), width=40, hover_color='firebrick1', height=40, bg_color='grey25', fg_color='red', command=lambda:(frameSpuntaBatch.destroy(), labelSpuntaBatch.destroy(), buttonSubmitBatch.configure(state=NORMAL, fg_color='blue'), azzeraSubmitBatch()))
                buttonXSubmitBatch.place(x=10, y=330)
                buttonXSubmitBatch.configure(state=DISABLED)
                buttonSubmitBatch=customtkinter.CTkButton(master=frame2DxUpPag1 , text='Submit', text_color='white', font=('Roboto', 20), width=100, height=40, bg_color='grey25', fg_color='blue', command=lambda:(estraiElencoCovariateBatch(), creaSpuntaBatch(), buttonSubmitBatch.configure(state=DISABLED, fg_color='grey30'), buttonXSubmitBatch.configure(state=NORMAL), attivaSubmitBatch()))
                buttonSubmitBatch.place(x=85, y=330)
                
                elencoCovariateNum=[]
                for i in range(len(elencoCovariate)):
                    elencoCovariateNum.append(customtkinter.StringVar(value='off'))
                    checkCovariata=customtkinter.CTkCheckBox(master=frameScrollboxNum , text=f'{elencoCovariate[i]}', text_color='white', font=('Roboto', 14), variable=elencoCovariateNum[i], onvalue='on', offvalue='off')
                    checkCovariata.pack(ipady=10)
                buttonXSubmitNum=customtkinter.CTkButton(master=frame2DxUpPag1 , text='x', text_color='white', font=('Roboto', 20), width=40, hover_color='firebrick1', height=40, bg_color='grey25', fg_color='red', command=lambda:(frameSpuntaNum.destroy(), labelSpuntaNum.destroy(), buttonSubmitNum.configure(state=NORMAL, fg_color='blue'), azzeraSubmitNum()))
                buttonXSubmitNum.place(x=200, y=330)
                buttonXSubmitNum.configure(state=DISABLED)
                buttonSubmitNum=customtkinter.CTkButton(master=frame2DxUpPag1 , text='Submit', text_color='white', font=('Roboto', 20), width=100, height=40, bg_color='grey25', fg_color='blue', command=lambda:(stampaElencoCovariateNum(), creaSpuntaNum(), buttonSubmitNum.configure(state=DISABLED, fg_color='grey30'), buttonXSubmitNum.configure(state=NORMAL), attivaSubmitNum()))
                buttonSubmitNum.place(x=275, y=330)
                
                elencoCovariateCat=[]
                for i in range(len(elencoCovariate)):
                    elencoCovariateCat.append(customtkinter.StringVar(value='off'))
                    checkCovariata=customtkinter.CTkCheckBox(master=frameScrollboxCat , text=f'{elencoCovariate[i]}', text_color='white', font=('Roboto', 14), variable=elencoCovariateCat[i], onvalue='on', offvalue='off')
                    checkCovariata.pack(ipady=10)
                buttonXSubmitCat=customtkinter.CTkButton(master=frame2DxUpPag1 , text='x', text_color='white', font=('Roboto', 20), width=40, hover_color='firebrick1', height=40, bg_color='grey25', fg_color='red', command=lambda:(frameSpuntaCat.destroy(), labelSpuntaCat.destroy(), buttonSubmitCat.configure(state=NORMAL, fg_color='blue'), azzeraSubmitCat()))
                buttonXSubmitCat.place(x=395, y=330)
                buttonXSubmitCat.configure(state=DISABLED)
                buttonSubmitCat=customtkinter.CTkButton(master=frame2DxUpPag1 , text='Submit', text_color='white', font=('Roboto', 20), width=100, height=40, bg_color='grey25', fg_color='blue', command=lambda:(stampaElencoCovariateCat(), creaSpuntaCat(), buttonSubmitCat.configure(state=DISABLED, fg_color='grey30'), buttonXSubmitCat.configure(state=NORMAL), attivaSubmitCat()))
                buttonSubmitCat.place(x=470, y=330)
                
                for i in range(randomNum, 101):
                    time.sleep(0.001)
                    progressBarCovariate.set(i / 100)
                    frameCaricamento.update_idletasks()
                    percentualeCovariate=customtkinter.CTkLabel(master=frameCaricamento, text=f'{i}' + '%', text_color='white', font=('Roboto', 20), bg_color='grey25')
                    percentualeCovariate.place(x=275, y=200)
                
                frameCaricamento.destroy()
    

                if checkNumPazienti==0 and numPazientiDataset!=0:
                    framePopUpNumPaz=customtkinter.CTkFrame(master=root, width=150, height=150, fg_color='white', bg_color='grey30')
                    framePopUpNumPaz.place(x=810, y=170)
                    imageWarningPaz=customtkinter.CTkImage(light_image=Image.open('IconaWarning.png'), size=(40, 40))
                    labelWarningPaz=customtkinter.CTkLabel(master=framePopUpNumPaz, text='', image=imageWarningPaz, bg_color='white')
                    labelWarningPaz.place(x=55, y=10)
                    labelPopUpNumPaz=customtkinter.CTkLabel(master=framePopUpNumPaz , text='Error:\n\nTHE NUMBER\nOF SUBJECTS\nDOES NOT MATCH', text_color='red', font=('Roboto', 12), bg_color='white')
                    labelPopUpNumPaz.place(x=20, y=55)
                    buttonXPopUpNumPaz=customtkinter.CTkButton(master=framePopUpNumPaz, text='x', font=('Roboto', 18), text_color='red', bg_color='white', fg_color='white', hover_color='grey30', height=10, width=10, command=lambda:framePopUpNumPaz.destroy())
                    buttonXPopUpNumPaz.place(x=125, y=5)

                if MATRICEDATASET is not None and MATRICECOVARIATE is not None and checkSubmitBatch==1 and checkSubmitNum==1 and checkSubmitCat==1 and checkNumPazienti==1:
                    buttonArmonizza.configure(state=NORMAL, fg_color='green4')
                else:
                    buttonArmonizza.configure(state=DISABLED, fg_color='grey35', text_color_disabled='grey')
            else:
                yPopUpErrFile=700
                framePopUpErrFile=customtkinter.CTkFrame(master=root, width=150, height=150, fg_color='white', bg_color='grey25')
                imageWarningPaz=customtkinter.CTkImage(light_image=Image.open('IconaWarning.png'), size=(40, 40))
                labelWarningPaz=customtkinter.CTkLabel(master=framePopUpErrFile, text='', image=imageWarningPaz, bg_color='white')
                labelWarningPaz.place(x=55, y=10)
                labelPopUpErrFile=customtkinter.CTkLabel(master=framePopUpErrFile , text='Error:\n\nCHECK THAT\nYOU UPLOADED\nA COVARIATES FILE', text_color='red', font=('Roboto', 12), bg_color='white')
                labelPopUpErrFile.place(x=20, y=55)
                creaPopUpErrFile()
                buttonXPopUpErrFile=customtkinter.CTkButton(master=framePopUpErrFile, text='x', font=('Roboto', 14), text_color='red', bg_color='white', fg_color='white', hover_color='grey30', height=10, width=10, command=togliPopUpErrFile)
                buttonXPopUpErrFile.place(x=125, y=5)

def seleziona_file_e_assegna_matrice_INPUTESTIMATES():
    # Apre la finestra di dialogo per selezionare un file CSV o MAT
    filepath = filedialog.askopenfilename(filetypes=[("File pikle", ".pkl")])
    
    if filepath:  # Assicura che il percorso del file sia valido
        global MATRICEESTIMATES  # Dichiaro MATRICE1 come globale per poterla modificare all'interno della funzione
        if filepath.endswith('.pkl'):
            MATRICEESTIMATES = load_object(filepath)
            previousCategorical=MATRICEESTIMATES.__dict__['feat_detail']['features']['categorical']
            previousContinuous=MATRICEESTIMATES.__dict__['feat_detail']['features']['continuous']
            
            buttonEstimates.configure(state='disabled', fg_color='grey30')
            fileNameEstimates = filepath.split("/")[-1]
            frameAnteprimaEstimates=customtkinter.CTkFrame(master=root, height=50, width=250, bg_color='grey25', fg_color='white')
            frameAnteprimaEstimates.place(x=300, y=490)
            if len(fileNameEstimates) >= 20:
                fileNameEstimates = fileNameEstimates[:19] + "..."
            labelFileEstimates = customtkinter.CTkLabel(master=root, text=f'{fileNameEstimates}', font=('Roboto', 14), bg_color='white', fg_color='white', text_color='black')
            labelFileEstimates.place(x=360, y=500)
            imagePKLEstimates=customtkinter.CTkImage(light_image=Image.open('IconaPKL.png'), size=(40, 40))
            labelImagePKLEstimates=customtkinter.CTkLabel(master=root, text='', image=imagePKLEstimates, bg_color='white')
            labelImagePKLEstimates.place(x=305, y=495)
            buttonXEstimates = customtkinter.CTkButton(master=root, text='x', font=('Roboto', 20), bg_color='white', fg_color='white', text_color='red', height=10, width=10, hover_color='DodgerBlue3',
                                                     command=lambda:(buttonXEstimates.destroy(), buttonEstimates.configure(state='normal', fg_color='blue'), frameAnteprimaEstimates.destroy(), labelFileEstimates.destroy(), labelImagePKLEstimates.destroy(),azzeraESTIMATES()))
            buttonXEstimates.place(x=525, y=490)                
            frameCovariateEstimates=customtkinter.CTkFrame(master=root, height=180, width=350, bg_color='grey25', fg_color='white')
            frameCovariateEstimates.place(x=450, y=200)
            imageWarningEst=customtkinter.CTkImage(light_image=Image.open('IconaWarningBlu.png'), size=(60, 60))
            labelWarningEst=customtkinter.CTkLabel(master=frameCovariateEstimates, text='', image=imageWarningEst, bg_color='white')
            labelWarningEst.place(x=140, y=10)
            labelCovariateEstimates=customtkinter.CTkLabel(master=frameCovariateEstimates, text=f'Categorical covariates preserved:\n{previousCategorical}\nNumerical covariate preserved:\n{previousContinuous}\n', text_color='black', font=('Roboto', 12), bg_color='white')
            labelCovariateEstimates.place(x=80, y=70)
            lineaBlu=customtkinter.CTkFrame(master=frameCovariateEstimates, height=2, width=346, bg_color='white', fg_color='blue')
            lineaBlu.place(x=2, y=130)
            labelCovariateEstimates2=customtkinter.CTkLabel(master=frameCovariateEstimates, text=f'INPUT COVARIATE NAMES\nMUST BE THE SAME', text_color='blue', font=('Roboto', 11), bg_color='white')
            labelCovariateEstimates2.place(x=20, y=140)
            buttonCapito=customtkinter.CTkButton(master=frameCovariateEstimates, text='Understood', font=('Roboto', 14), text_color='white', bg_color='white', fg_color='blue', width=20, command=lambda:frameCovariateEstimates.destroy())
            buttonCapito.place(x=230, y=140)
        
def leggi_csv_e_restituisci_matrice_CSV(filepathCSV):
    # Legge il file CSV utilizzando pandas
    matrice = pd.read_csv(filepathCSV)
    return matrice 

def Combat():
    global dataset_harmonized, fitted_model

    columns = range(MATRICEDATASET.shape[1])
    feat_detail={'features': {'id': columns,
                              'categorical': selectedCat,
                              'continuous': selectedNum}}
        
    combat_object=ComBatHarmonization(cv_method=None, ref_batch=None,
                                          regression_fit=0,
                                          feat_detail=feat_detail,
                                          feat_of_no_interest=None)
            
    MATRICECOVARIATE.rename(columns={selectedBatch[0] :"batch"}, inplace=True)      
    MATRICECOVARIATE['batch'].astype('int')
    dataset_dict={'data': MATRICEDATASET , 'covariates': MATRICECOVARIATE}
    
    if MATRICEESTIMATES == None:  
        
        print('Sto  facendo fit e transform')
        fitted_model = combat_object.fit(dataset_dict)
        dataset_harmonized = fitted_model.transform(dataset_dict)
        
    else:
        print('Sto solo facendo transform')
        fitted_model = MATRICEESTIMATES
        dataset_harmonized = MATRICEESTIMATES.transform(dataset_dict)
        
        

def PCAfun():
    global fig1,fig2
    buttonPCA.configure(state=DISABLED, fg_color='blue', text_color_disabled='white')
    buttonUMAP.configure(state=NORMAL, fg_color='white')
    spuntaPCA=customtkinter.CTkLabel(master=framePag2, text='✔', text_color='blue', font=('Roboto', 30), bg_color='grey30', fg_color='grey30')
    spuntaPCA.place(x=110, y=10)
    cancellaSpuntaUMAP=customtkinter.CTkFrame(master=framePag2, height=50, width=40, fg_color='grey30', bg_color='grey30')
    cancellaSpuntaUMAP.place(x=110, y=70)
    
    if fig1 == None:  
        
        frameCaricamentoPCA=customtkinter.CTkFrame(master=framePag2, height=450, width=1030, fg_color='grey25', bg_color='grey30')
        frameCaricamentoPCA.place(x=150, y=10)
        scrittaCaricamentoCovariate=customtkinter.CTkLabel(master=frameCaricamentoPCA, text='Loading PCA scatter plot', text_color='white', font=('Roboto', 20), bg_color='grey25')
        scrittaCaricamentoCovariate.place(x=400, y=100)                
        progressBarPCA=customtkinter.CTkProgressBar(master=frameCaricamentoPCA, height=30, width=450, border_color='white', border_width=2, progress_color='blue')
        progressBarPCA.place(x=300, y=150)
        randomNum=random.randint(10, 100)
        for i in range(randomNum):
            time.sleep(0.001)
            progressBarPCA.set(i / 100)
            frameCaricamentoPCA.update_idletasks()
            percentualePCA=customtkinter.CTkLabel(master=frameCaricamentoPCA, text=f'{i}' + '%', text_color='white', font=('Roboto', 20), bg_color='grey25')
            percentualePCA.place(x=500, y=200)

        scaled_data = StandardScaler().fit_transform(MATRICEDATASET)
        pca = PCA()
        pca.fit(scaled_data) # addestra il modello PCA 
        projected_data = pca.transform(scaled_data) # trasforma i dati utilizzando le informazioni apprese durante l'addestramento del modello
        
        
        num_colors = len(set(MATRICECOVARIATE.batch))
        labels = list(range(1, num_colors + 1))
        colors = sns.color_palette("colorblind")
        fig1, ax1 = plt.subplots()
        scatter = ax1.scatter(projected_data[:, 0], projected_data[:, 1], c=[colors[int(x)] for x in MATRICECOVARIATE.batch], alpha=0.8)
        handles = [plt.Line2D([], [], marker="o", color=color, ls="", markersize=8) for color in colors]
        plt.xlabel('PC 1')
        plt.ylabel('PC 2')
        ax1.legend(handles, labels, loc='lower left', bbox_to_anchor=(0.02, 0.02), ncol=1, title="Sites")
        ax1.set_title('Raw dataset PCA projection', fontsize=24)
        ax1.grid()
        ax1.set_aspect('equal', 'datalim')
        
        scaled_data = StandardScaler().fit_transform(dataset_harmonized)
        pca = PCA()
        pca.fit(scaled_data) # addestra il modello PCA 
        projected_data = pca.transform(scaled_data) # trasforma i dati utilizzando le informazioni apprese durante l'addestramento del modello
        
        
        fig2, ax2 = plt.subplots()
        scatter = ax2.scatter(projected_data[:, 0], projected_data[:, 1], c=[colors[int(x)] for x in MATRICECOVARIATE.batch], alpha=0.8)
        handles = [plt.Line2D([], [], marker="o", color=color, ls="", markersize=8) for color in colors]
        plt.xlabel('PC 1')
        plt.ylabel('PC 2')
        ax2.legend(handles, labels, loc='lower left', bbox_to_anchor=(0.02, 0.02), ncol=1, title="Sites")
        ax2.set_title('Harmonized dataset PCA projection', fontsize=24)
        ax2.grid()
        ax2.set_aspect('equal', 'datalim')
        
        
        canvas1 = FigureCanvasTkAgg(fig1, master=frameScatter1)
        canvas1.draw()
        canvas1.get_tk_widget().place(relwidth=1, relheight=1)
        
        canvas2 = FigureCanvasTkAgg(fig2, master=frameScatter2)
        canvas2.draw()
        canvas2.get_tk_widget().place(relwidth=1, relheight=1)
        
        for i in range(randomNum, 101):
            time.sleep(0.001)
            progressBarPCA.set(i / 100)
            frameCaricamentoPCA.update_idletasks()
            percentualePCA=customtkinter.CTkLabel(master=frameCaricamentoPCA, text=f'{i}' + '%', text_color='white', font=('Roboto', 20), bg_color='grey25')
            percentualePCA.place(x=500, y=200)
        frameCaricamentoPCA.destroy()
        
    else:
        canvas1 = FigureCanvasTkAgg(fig1, master=frameScatter1)
        canvas1.draw()
        canvas1.get_tk_widget().place(relwidth=1, relheight=1)
        
        canvas2 = FigureCanvasTkAgg(fig2, master=frameScatter2)
        canvas2.draw()
        canvas2.get_tk_widget().place(relwidth=1, relheight=1)
    
def UMAPfun():
    global fig3, fig4
    buttonUMAP.configure(state=customtkinter.DISABLED, fg_color='blue', text_color_disabled='white')
    buttonPCA.configure(state=customtkinter.NORMAL, fg_color='white')
    spuntaUMAP=customtkinter.CTkLabel(master=framePag2, text='✔', text_color='blue', font=('Roboto', 30), bg_color='grey30', fg_color='grey30')
    spuntaUMAP.place(x=110, y=70)
    cancellaSpuntaPCA=customtkinter.CTkFrame(master=framePag2, height=50, width=40, fg_color='grey30', bg_color='grey30')
    cancellaSpuntaPCA.place(x=110, y=10)
    
    
    if fig3 == None:
        
        frameCaricamentoUMAP=customtkinter.CTkFrame(master=framePag2, height=450, width=1030, fg_color='grey25', bg_color='grey30')
        frameCaricamentoUMAP.place(x=150, y=10)
        scrittaCaricamentoUMAP=customtkinter.CTkLabel(master=frameCaricamentoUMAP, text='Loading UMAP scatter plot', text_color='white', font=('Roboto', 20), bg_color='grey25')
        scrittaCaricamentoUMAP.place(x=400, y=100)                
        randomNum1=random.randint(10, 50)
        randomNum2=random.randint(60, 100)
        progressBarUMAP=customtkinter.CTkProgressBar(master=frameCaricamentoUMAP, height=30, width=450, border_color='white', border_width=2, progress_color='blue')
        progressBarUMAP.place(x=300, y=150)
        for i in range(randomNum1):
            time.sleep(0.001)
            progressBarUMAP.set(i / 100)
            frameCaricamentoUMAP.update_idletasks()
            percentualeUMAP=customtkinter.CTkLabel(master=frameCaricamentoUMAP, text=f'{i}' + '%', text_color='white', font=('Roboto', 20), bg_color='grey25')
            percentualeUMAP.place(x=500, y=200)

        reducer = umap.UMAP(random_state=42)
        scaled_data = StandardScaler().fit_transform(MATRICEDATASET)
        embedding = reducer.fit_transform(scaled_data)
    
        num_colors = len(set(MATRICECOVARIATE.batch))
        labels = list(range(1, num_colors + 1))
        colors = sns.color_palette("colorblind")
        fig3, ax1 = plt.subplots()
        scatter = ax1.scatter(embedding[:, 0], embedding[:, 1], c=[colors[int(x)] for x in MATRICECOVARIATE.batch], alpha=0.8)
        handles = [plt.Line2D([], [], marker="o", color=color, ls="", markersize=8) for color in colors]
        plt.xlabel('UMAP 1')
        plt.ylabel('UMAP 2')
        ax1.legend(handles, labels, loc='lower left', bbox_to_anchor=(0.02, 0.02), ncol=1, title="Sites")
        ax1.set_title('Raw dataset UMAP projection', fontsize=24)
        ax1.grid()
        ax1.set_aspect('equal', 'datalim')
    
        # Secondo UMAP plot
        reducer = umap.UMAP(random_state=42)
        scaled_data = StandardScaler().fit_transform(dataset_harmonized)
        embedding = reducer.fit_transform(scaled_data)
        
        for i in range(randomNum1, randomNum2):
            time.sleep(0.001)
            progressBarUMAP.set(i / 100)
            frameCaricamentoUMAP.update_idletasks()
            percentualeUMAP=customtkinter.CTkLabel(master=frameCaricamentoUMAP, text=f'{i}' + '%', text_color='white', font=('Roboto', 20), bg_color='grey25')
            percentualeUMAP.place(x=500, y=200)
    
        fig4, ax2 = plt.subplots()
        scatter = ax2.scatter(embedding[:, 0], embedding[:, 1], c=[colors[int(x)] for x in MATRICECOVARIATE.batch], alpha=0.8)
        handles = [plt.Line2D([], [], marker="o", color=color, ls="", markersize=8) for color in colors]
        plt.xlabel('UMAP 1')
        plt.ylabel('UMAP 2')
        ax2.legend(handles, labels, loc='lower left', bbox_to_anchor=(0.02, 0.02), ncol=1, title="Sites")
        ax2.set_title('Harmonized dataset UMAP projection', fontsize=24)
        ax2.grid()
        ax2.set_aspect('equal', 'datalim')
            
        canvas1 = FigureCanvasTkAgg(fig3, master=frameScatter1)
        canvas1.draw()
        canvas1.get_tk_widget().place(relwidth=1, relheight=1)
        
        canvas2 = FigureCanvasTkAgg(fig4, master=frameScatter2)
        canvas2.draw()
        canvas2.get_tk_widget().place(relwidth=1, relheight=1)
        
        for i in range(randomNum2, 101):
            time.sleep(0.001)
            progressBarUMAP.set(i / 100)
            frameCaricamentoUMAP.update_idletasks()
            percentualeUMAP=customtkinter.CTkLabel(master=frameCaricamentoUMAP, text=f'{i}' + '%', text_color='white', font=('Roboto', 20), bg_color='grey25')
            percentualeUMAP.place(x=500, y=200)
        frameCaricamentoUMAP.destroy()
    else: 
        canvas1 = FigureCanvasTkAgg(fig3, master=frameScatter1)
        canvas1.draw()
        canvas1.get_tk_widget().place(relwidth=1, relheight=1)
        
        canvas2 = FigureCanvasTkAgg(fig4, master=frameScatter2)
        canvas2.draw()
        canvas2.get_tk_widget().place(relwidth=1, relheight=1)



def save_object(obj, filename):
    with open(filename, 'wb') as outp:
        pickle.dump(obj, outp, pickle.HIGHEST_PROTOCOL)
        
        
def load_object(filename):
    with open(filename, 'rb') as inp:
        return pickle.load(inp)
        
def openQRcode():
    frameQRcode=customtkinter.CTkFrame(master=framePag2, height=450, width=450, bg_color='grey25', fg_color='navy')
    frameQRcode.place(x=425, y=20)
    imageQRcode=customtkinter.CTkImage(light_image=Image.open('QRcode.png'), size=(400, 400))
    labelQRcode=customtkinter.CTkLabel(master=frameQRcode, text='', image=imageQRcode)
    labelQRcode.place(x=25, y=25)
    buttonXQRcode=customtkinter.CTkButton(master=frameQRcode, height=10, width=10, text='x', font=('Roboto', 19), text_color='grey80', bg_color='navy', fg_color='navy', command=lambda:frameQRcode.destroy())
    buttonXQRcode.place(x=425, y=2)

def openAboutUs():
    frameAboutUs=customtkinter.CTkFrame(master = root, height=580, width=1180, bg_color='grey30', fg_color='grey80')
    frameAboutUs.place(x = 10,y = 10)
    buttonIndietroAboutUs=customtkinter.CTkButton(master=frameAboutUs, height=30, width=10, text='←', font=('Roboto', 30), text_color='grey25', bg_color='grey80', fg_color='grey80', hover_color='grey70', corner_radius=30, command=lambda:frameAboutUs.destroy())
    buttonIndietroAboutUs.place(x=15, y=15)
    labelAboutUs1=customtkinter.CTkLabel(master=frameAboutUs, text='About us', font=('Roboto', 30), bg_color='grey80', fg_color='grey80', text_color='grey30')
    labelAboutUs1.place(x=550, y=10)
    labelAboutUs2=customtkinter.CTkLabel(master=frameAboutUs, text='\nComBat Harmonization GUI was developed with the aim of creating a user-friendly graphical interface\nthat implements software for the harmonization of multicenter neuroimaging data, making it accessible to users\nwho are not proficient in programming.', font=('Helvetica', 20), text_color='grey30', bg_color='grey80', fg_color='grey80')
    labelAboutUs2.place(x=100, y=50)
    labelAboutUs3=customtkinter.CTkLabel(master=frameAboutUs, text='Developed by', font=('Roboto', 30), bg_color='grey80', fg_color='grey80', text_color='grey30')
    labelAboutUs3.place(x=525, y=250)
    labelAboutUs4=customtkinter.CTkLabel(master=frameAboutUs, text='Jonny Marques Arbex\nMatteo Borsa\nLorenzo Castelli', font=('Roboto', 20), bg_color='grey80', fg_color='grey80', text_color='grey30')
    labelAboutUs4.place(x=525, y=300)

def creaPag2():
    global buttonPCA, buttonUMAP
    global framePag2, frameUpPag2, buttonInfoPag2
    global frameScatter1, frameScatter2
    global fig1,fig3
    
    fig1 = None
    fig3 = None
    
    framePag2=customtkinter.CTkFrame(master=root, height=560, width=1200, fg_color='grey30', bg_color='grey30')
    framePag2.place(x=0, y=40)
    buttonIndietro.configure(state=NORMAL)
    
    frameUpPag2=customtkinter.CTkFrame(master=framePag2, height=450, width=1030, fg_color='grey25', bg_color='grey30')
    frameUpPag2.place(x=150, y=10)
    
    frameDownSXPag2=customtkinter.CTkFrame(master=framePag2, height=70, width=510, fg_color='grey25', bg_color='grey30')
    frameDownSXPag2.place(x=150, y=470)
    frameDownDXPag2=customtkinter.CTkFrame(master=framePag2, height=70, width=510, fg_color='grey25', bg_color='grey30')
    frameDownDXPag2.place(x=670, y=470) 
    
    frameScatter1 = customtkinter.CTkFrame(master=framePag2, height=400, width=480, fg_color='grey25', bg_color='grey30')
    frameScatter1.place(x=170, y=40)
    frameScatter2 = customtkinter.CTkFrame(master=framePag2, height=400, width=480, fg_color='grey25', bg_color='grey30')
    frameScatter2.place(x=680, y=40)
    
    labelHarmCompleted = customtkinter.CTkLabel(master = framePag2, text='Data Harmonization completed', font=('Roboto', 24, 'bold'), text_color='white', bg_color='grey25')
    labelHarmCompleted.place(x = 200, y = 220)
    labelHarmCompleted1 = customtkinter.CTkLabel(master = framePag2, text='Compare the data before and after harmonization using the "PCA" or "UMAP" buttons on the left', font=('Roboto', 18), text_color='white', bg_color='grey25')
    labelHarmCompleted1.place(x = 200, y = 250)
    
    
    buttonPCA=customtkinter.CTkButton(master=framePag2, text='PCA', font=('Roboto', 24), text_color='black', bg_color='grey30', fg_color='grey80', width=100, height=50, hover=FALSE, command=lambda:(PCAfun(),labelHarmCompleted.destroy(),labelHarmCompleted1.destroy()))
    buttonPCA.place(x=10, y=10)
    buttonUMAP=customtkinter.CTkButton(master=framePag2, text='UMAP', font=('Roboto', 24), text_color='black', bg_color='grey30', fg_color='grey80', width=100, height=50, hover=FALSE, command=lambda:(UMAPfun(),labelHarmCompleted.destroy(),labelHarmCompleted1.destroy()))
    buttonUMAP.place(x=10, y=70)
    
    buttonDownloadDataset=customtkinter.CTkButton(master=framePag2, text='Download ↓', font=('Roboto', 18), text_color='white', bg_color='grey25', fg_color='blue4', width=100, height=50, hover=FALSE, command=lambda:dowloadDataset() )
    buttonDownloadDataset.place(x=540,y=480)
    buttonDownloadEstimates=customtkinter.CTkButton(master=framePag2, text='Download ↓', font=('Roboto', 18), text_color='white', bg_color='grey25', fg_color='blue4', width=100, height=50, hover=FALSE, command=lambda:dowloadEstimates() )
    buttonDownloadEstimates.place(x=1060,y=480)
    labelDownloadDataset = customtkinter.CTkLabel(master = framePag2, text='Harmonized dataset', font=('Roboto', 24), text_color='white', bg_color='grey25')
    labelDownloadDataset.place(x = 160, y = 490)
    labelDownloadEstimates = customtkinter.CTkLabel(master = framePag2, text='ComBat estimates', font=('Roboto', 24), text_color='white', bg_color='grey25')
    labelDownloadEstimates.place(x = 680, y = 490)
    
    buttonQRcode=customtkinter.CTkButton(master=framePag2, text='Leave a feedback', text_color='grey80', font=('Roboto', 12), height=40, width=120, fg_color='grey25', bg_color='grey30', hover_color='grey40', command=lambda:openQRcode())
    buttonQRcode.place(x=10, y=420)
    buttonCredits=customtkinter.CTkButton(master=framePag2, text='About us', text_color='grey80', font=('Roboto', 12), height=40, width=120, fg_color='grey25', bg_color='grey30', hover_color='grey40', command=lambda:openAboutUs())
    buttonCredits.place(x=10, y=370)
    
    buttonInfoPag2 = customtkinter.CTkButton(master = framePag2, text='i', text_color='white', font=('Roboto', 26) , height=10, width=35, fg_color='blue', bg_color='grey30', hover_color='blue', text_color_disabled='grey30', command=lambda: (creaPopUpInfoPag2()))
    buttonInfoPag2.place(x=10, y=130)

    
root=customtkinter.CTk()
global checkNumPazientiDataset, checkNumPazientiCovariate, checkNumPazienti

MATRICEDATASET=None
MATRICECOVARIATE=None
MATRICEESTIMATES=None
checkSubmitBatch=0
checkSubmitNum=0
checkSubmitCat=0
numPazientiCovariate=0
numPazientiDataset=0
checkNumPazienti=0

root.title('ComBat Harmonization') 
larghezzaSchermo=root.winfo_screenwidth()
altezzaSchermo=root.winfo_screenheight()
xPos=larghezzaSchermo/5
yPos=altezzaSchermo/2
root.geometry(f'1200x600+{xPos}+{yPos}')
root.resizable(FALSE,FALSE)

framePrincipalePag1 = customtkinter.CTkFrame(master = root,height=600, width = 1200, fg_color='grey30', bg_color='grey30')
framePrincipalePag1.place(x = 0,y = 0)
frameDxUpPag1=customtkinter.CTkFrame(master = root ,height=380 , width = 580, fg_color='grey25', bg_color='grey30')
frameDxUpPag1.place(x = 600, y = 40)
frameSxPag1=customtkinter.CTkFrame(master=root, height=540, width=560, fg_color='grey25', bg_color='grey30')
frameSxPag1.place(x=20, y=40)

buttonIndietro=customtkinter.CTkButton(master=root, text='←', font=('Roboto', 26), text_color='white', bg_color='grey30', fg_color='grey30', height=29, width=29, corner_radius=29, hover_color='grey25', command=lambda:(framePag2.destroy(), buttonIndietro.configure(state=DISABLED)))
buttonIndietro.place(x=30, y=2)
buttonIndietro.configure(state=DISABLED)

labelDataset = customtkinter.CTkLabel(master = root, text='Dataset', font=('Roboto', 24), text_color='white', bg_color='grey25')
labelDataset.place(x = 100, y = 50)
buttonDataset = customtkinter.CTkButton(master = root, text='↑ Upload', font=('Roboto', 20) , height=50, width=200, fg_color='blue4', bg_color='grey25', command=lambda:seleziona_file_e_assegna_matrice_INPUTDATASET())
buttonDataset.place(x = 40, y = 90)

labelCovariates = customtkinter.CTkLabel(master = root, text='Covariates', font=('Roboto', 24), text_color='white', bg_color='grey25')
labelCovariates.place(x = 80, y = 250)
buttonCovariates = customtkinter.CTkButton(master = root, text='↑ Upload', font=('Roboto', 20) , height=50, width=200, fg_color='blue4', bg_color='grey25', command=lambda:(seleziona_file_e_assegna_matrice_INPUTCOVARIATE()))
buttonCovariates.place(x = 40, y = 290) 

labelEstimates = customtkinter.CTkLabel(master = root, text='ComBat Estimates', font=('Roboto', 20), text_color='white', bg_color='grey25')
labelEstimates.place(x = 60, y = 450)
buttonEstimates = customtkinter.CTkButton(master = root, text='↑ Upload', font=('Roboto', 20) , height=50, width=200, fg_color='blue', bg_color='grey25', command=lambda:(seleziona_file_e_assegna_matrice_INPUTESTIMATES()))
buttonEstimates.place(x = 40, y = 490)

labelCampoObbligatorioDataset=customtkinter.CTkLabel(master=root, text='Required', font=('Roboto', 20), text_color='grey80', bg_color='grey25')
labelCampoObbligatorioDataset.place(x=300, y=100)
labelCampoObbligatorioCovariate=customtkinter.CTkLabel(master=root, text='Required', font=('Roboto', 20), text_color='grey80', bg_color='grey25')
labelCampoObbligatorioCovariate.place(x=300, y=300)

buttonArmonizza = customtkinter.CTkButton(master = root, text='Harmonize', font=('Roboto', 33) , height=80, width=400, fg_color='green4', bg_color='grey30', hover_color='PaleGreen3', text_color_disabled='PaleGreen3', command=lambda: (creaPag2(), Combat()))
buttonArmonizza.place(x=690, y=470)
buttonArmonizza.configure(state=DISABLED, fg_color='grey35', text_color_disabled='grey')

buttonInfoPag1 = customtkinter.CTkButton(master = root, text='i', text_color='white', font=('Roboto', 26) , height=10, width=35, fg_color='blue', bg_color='grey25', hover_color='blue', text_color_disabled='grey30', command=lambda: (creaPopUpInfoPag1()))
buttonInfoPag1.place(x=538, y=45)

root.mainloop()