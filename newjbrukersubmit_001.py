# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 09:23:20 2021

@author: ERIC
"""

import shutil
import csv
# import json
import platform
import newreadcsv243A as readcsv243A

from  time import strftime, localtime

from javax.swing import JTable, JButton, JFrame, JPanel, JTextField, JLabel, JList, JScrollPane, JOptionPane, JSeparator, JTabbedPane
from javax.swing.table import DefaultTableModel
from java.awt import  BorderLayout,Dimension, FlowLayout, GridLayout, Color

import os
import time
import platform
import copy



def checkExperimentsWillRun(expt_list):
    """
    test whether all pulse sequences will run on current spectrometer.

    Parameters
    ----------
    expt_list : List of Dictionaries
        List of dictionaries read in from a csv file that has experiment
        information  such as solvent, pulse sequence, title
        
    Global Variables
    ----------------
    readcsv243A.experiments : dictionary
        Holds information on what experiments, solvents ar compatible with each spectrometer
        
    readcsv243A.spec_name: string
        Name of the spectrometer that the program is currently running on

    Returns
    -------
    ok : Bool
    
    pulseSequence : String
        pulse sequence name that cannot run on sprectrometer 
        or "" if everything okay

    """
    for rw in expt_list:
        if  rw['Experiment'] == "High Field":
            continue
        for expt in rw['Experiment'].split(','):
            if expt.strip() not in readcsv243A.experiments[readcsv243A.spec_name].keys():
                # print expt.strip()
                return False, expt.strip()
        
        return True, ""
    

def returnJTableData( expt_list, carouselNumber, seconds_start, newTimestamp):
    """
    return a list of lists (dataTable) containing experiment data for use 
    by a JTable widget.
    The dataTable will be sorted based on block/sample number.
    A carousel number will be inserted into the table for each different 
    sample, if the sample is destined for low field and a zero will be added
    if sample is fron high field spectrometers
    The file name will be given a unique seconds number if it is a different sample
    starting from 61

    Parameters
    ----------
    expt_list : List
        List of dictionaries read in from csv file originating from excel sheet 
    carouselNumber : integer
        Starting position number in carousel where samples will be put

    Returns
    -------
    tableData : List
        2-D list of lists that has been sorted on sample/block number

    """

    # sort csv file based on block number
    # assume students may have not started from beginning of block and 
    # not added tubes sequentially.
    tableData = [] # list of lists to be used by jTable
    block_number = [] # list of list to hold sample number and index into list
    
    timestamp = strftime("%d%H%M", localtime())
    
    for i,r in enumerate(expt_list):
        block_number.append([int(r['sample #']),i])
    
    # sort block number list based on block number min to max based on type being integers   
    block_number.sort()
    
    # copy sorted dict data into a simple list of lists
    for jj,ii in block_number:
         r = expt_list[ii]
         if newTimestamp:
             rname = timestamp
         else:
             rname = r['Name']
    
         tableData.append([int(r['sample #']),
                           rname,
                            #r['Name'],
                            r['Experiment'],
                            r['Solvent'],
                            r['Group'],
                            r['Member'],
                            r['Email'],
                            r['Sample Name']])
         
         

   
    timestamplist  = os.listdir(JBrukerSubmit.timestamp_directory)                       
    # Alter 61 file name so that they are unique for each sample
    # i = seconds_start
    i = int(strftime("%S", localtime()))
    oldblockNumber = int(tableData[0][0])
    for rw in tableData:          
        while True:
            
            if len(rw[1]) == 8:
                rw[1] = rw[1][:-2]

            i = (i+1)%100
                
            if len(rw[1]) == 5:
                rw[1] = "0" + str(rw[1])
            if i < 10:
                rw[1] = str(rw[1]) + '0' + str(i)
            else:
                rw[1] = str(rw[1]) + str(i)
           
            
            if rw[1] not in timestamplist:
                break
    
    # insert holder number based on experiment performed on low field
    # if sample for high field analysis set holder number to 0
    # only increment holder/carousel number if new sample    
    # sampleNumberOld = int(tableData[0][0])
    
    # for i,r in enumerate(tableData):
    #     sampleNumber = int(r[0])
    #     lowField = True
    #     if r[2] == 'High Field':
    #         lowField = False
    #     # lowField = r[2] != 'High Field'

    #     # if new sample and low field experiment
    #     # increment carousel Number
    #     if sampleNumber > sampleNumberOld and lowField:
    #         carouselNumber += 1
        
    #     # insert carousel number into table if lowfield experiment
    #     # else insert a Zero
    #     if lowField:
    #         r.insert(1, carouselNumber)
    #     else:
    #         r.insert(1,0)
        
    #     # update old sample number
    #     sampleNumberOld = sampleNumber
    
    
    # sampleNumberOld = int(tableData[0][0])
    
    for i,r in enumerate(tableData):
        if r[2] == 'High Field':
            r.insert(1,0)
        else:
            r.insert(1, carouselNumber)
            carouselNumber += 1


    return tableData



class carousel(JPanel):
    
    def cbuttonClicked(self, event):
        bnum = int(event.getActionCommand())
        self.cbuttons[bnum]['empty'] = not  self.cbuttons[bnum]['empty']
        
        if self.cbuttons[bnum]['empty']:
            # chamge background color to green
            self.cbuttons[bnum]['button'].background = Color.green
        else:
            # change button background color to red
            self. cbuttons[bnum]['button'].background = Color.red
    
    
    def __init__(self):
        
        JPanel.__init__(self)
            
        nrows = 6
        ncols = 10
        
        # panelCarousel = JPanel()
        self.setPreferredSize(Dimension(900,160))           
        self.setLayout(GridLayout(nrows,ncols))
    
        self.cbuttons = {}
        k = 0
        self.setLayout(GridLayout(6,10))
        for i in range(nrows):
           for j in range(ncols):
              k = k+1
              self.cbuttons[k] = {'empty': True, 'button':JButton(str(k), actionPerformed=self.cbuttonClicked)}
              # self.cbuttons[k] = {'empty': True, 'button':JButton(str(k))}
              self.cbuttons[k]['button'].background = Color.green
              self.add(self.cbuttons[k]['button'])
          

              
class sampleTableIn(JPanel):

    def __init__(self, tableChangedCB, tableMouseClicked):
    
        JPanel.__init__(self)
            
        # Create table to display csv file
        self.tableData = []
        
        for r in range(10):
            self.tableData.append(["",]*len(JBrukerSubmit.colHeads))
        
        colNames = JBrukerSubmit.colHeads
        self.dataTableModel = DefaultTableModel(self.tableData, colNames)
        self.table = JTable(self.dataTableModel, 
                            keyTyped=tableChangedCB,
                            mouseClicked=tableMouseClicked)
        
        self.scrollPaneTable = JScrollPane()
        self.scrollPaneTable.setPreferredSize(Dimension(900, 185))
        
        self.scrollPaneTable.getViewport().setView((self.table))

        self.add(self.scrollPaneTable) 
        
        
class sampleTableOut(JPanel):

    def __init__(self):
    
        JPanel.__init__(self)
            
        # Create table to display csv file
        self.tableData = []
        
        for r in range(10):
            self.tableData.append(["",]*len(JBrukerSubmit.colHeads))
        
        colNames = JBrukerSubmit.colHeads
        self.dataTableModel = DefaultTableModel(self.tableData, colNames)
        self.table = JTable(self.dataTableModel)
        
        self.scrollPaneTable = JScrollPane()
        self.scrollPaneTable.setPreferredSize(Dimension(900, 185))
        
        self.scrollPaneTable.getViewport().setView((self.table))

        self.add(self.scrollPaneTable) 


class SubmitList(JPanel):
    
   
    def __init__(self, pendingDirectory, callbackfn):
        
        JPanel.__init__(self)
        
        self.callbackfn = callbackfn
        self.pendingDirectory = pendingDirectory
        
        
        self.setPreferredSize(Dimension(200,525))
        
        self.pendingList = [f for f in os.listdir(self.pendingDirectory) if ".csv" in f[-5:]]
        
        bn = {}
        
        for f in self.pendingList:
            bn[f[:4]] = 1
        
        # print "list(bn.keys())"
        # print list(bn.keys())
        self.blocksData = list(bn.keys())
        self.blocksData.sort()
        # print JBrukerSubmit.pending_directory
        
        # self.data = self.returnCSVlist(self.hiddenFiles)
        self.list = JList(self.blocksData, valueChanged = self.callbackfn)
        self.spane = JScrollPane()
        self.spane.setPreferredSize(Dimension(200,150))
        self.spane.getViewport().setView((self.list))
        
        self.add(self.spane)
            
              
class JBrukerSubmit:
    
    colHeads = ('block Pos',
                'Holder',
                'Name',
                'Experiment',
                'Solvent',
                'Group',
                'Member',
                'Email',
                'Sample ID')
    
    if platform.node() == 'DM-CHEM-200':
        basedir = r"W:\downloads\Eric\remoteUsers"
        submitted_directory = r"W:\downloads\Eric\BrukerAutomationFiles"
        pending_directory = r"W:\downloads\Eric\remoteUsers"
        timestamp_directory =   r"W:\downloads\Eric\timestamps"
    elif platform.node() == 'ERIC-PC':
        basedir =  r"C:\Users\ERIC\Dropbox\projects\programming\2021\python\brukerautomation\csvfiles"
        submitted_directory = r"C:\Users\ERIC\Dropbox\projects\programming\2021\python\brukerautomation\BrukerAutomationFiles"
        pending_directory = r"C:\Users\ERIC\Dropbox\projects\programming\2021\python\brukerautomation\csvfiles"
        timestamp_directory = r"C:\Users\ERIC\Dropbox\projects\programming\2021\python\brukerautomation\timestamps"
    else:
        # running from Bruker spectrometers
        basedir = "/data/downloads/Eric/remoteUsers"
        pending_directory = "/data/downloads/Eric/remoteUsers"
        submitted_directory = "/data/downloads/Eric/BrukerAutomationFiles"
        timestamp_directory =   "/data/downloads/Eric/timestamps"
        
        
    def listSelect(self,event):
        """When a new csv file is selected from the list
        read in the file and display its contents in the table.
        Unordered csv files will be ordered based on the block/sample number.
        A holder column will be added to the CSV data based on the carousel 
        starting position.
        
        Parameters
        ----------
        
        event
        
        Returns
        -------
        
        Nothing
        
        Global Variables
        ----------------
        
        JBrukerSubmit.colHeads
        
        Local Variables
        ---------------
        selected
        csvName
        fn
        ok
        pulseSequence
        warningText

        Class Variables Accessed
        ------------------------
       
        self.list.selectedIndex
        self.carouselStartingPosition.text
        
        Class Variables Changed
        -----------------------
        
        self.label.text
        self.panelLabel : background
        self.statusLabel.text
        self.panelStatusLabel : background        
        self.expt_list
        self.cnumber
        self.carouselStartingPosition.text
        self.tableData

        
        Functions Called
        ----------------
        
        self.readcsvfile_asdict
        returnJTableData
        self.dataTableModel.setDataVector
        self.scrollPaneTable.getViewport().setView
        JOptionPane.showMessageDialog
        checkExperimentsWillRun
        
        """
        
        # Process the events from the list box and update the label
        # get the index from the list and then the filename 
        selected = self.list.selectedIndex
        if selected >= 0:
        
            # update file label and set background colour to normal
            csvName = self.blocksData[selected]
            self.label.text = csvName
            self.panelLabel.setBackground(self.standardBackgroundColor)
            
            # reset status label
            self.statusLabel.text = "Status"
            self.panelStatusLabel.setBackground(self.standardBackgroundColor)
            #
            # update table by reading in csv file
            # read in csv file and store as a list of dictionaries
            # one dictionary for each line   
            fn = csvName
            self.submitList, self.expt_list = self.readcsvfile_asdict(fn)

            # get carousel starting position, if the value cannot be converted
            # to an integer reset it to 1 and reset the GUI to 1
            try:
                self.cnumber = int(self.carouselStartingPosition.text)
            except:
                self.cnumber = 1
                self.carouselStartingPosition.text = "1"
            
            # get the csv data into a list of lists form ready for displaying
            self.tableData = returnJTableData( self.expt_list, 
                                              self.cnumber, 
                                              self.seconds_start,
                                              self.newTimestamp)
            #  reset newTimeStamp just in case
            # self.newTimestamp = False

            # display csv table in table view
            colNames = JBrukerSubmit.colHeads
            # transfer the data over to the table model
            self.dataTableModel.setDataVector(self.tableData, colNames)
            # display the table in the GUI
            self.scrollPaneTable.getViewport().setView((self.table))
            
            # check to see if experiments will run on the spectometer
            ok, pulseSequence =  checkExperimentsWillRun(self.expt_list)
                
            if not ok:
                # display warning dialog
                warningText = pulseSequence + " cannot be run on this spectrometer"
                JOptionPane.showMessageDialog(self.frame, warningText);
                
                
            # colour in potential carousel positions
            
            self.colorincells(self.carouselin, self.panelTableIn)
   
    
    def listInSubmit(self, event):
        """Submit highlighted to csv file to automation folder of spectrometer
        
        Parameters
        ----------
        
        event : 
        
        Class Variables Accessed
        ------------------------
        
        self.list.selectedIndex
        self.data
        self.dataTableModel.dataVector
        self.frame
        
        
        Class Variables Changed
        -----------------------
        
        self.label.text
        self.statusLabel.text
        
        Function Local Variables
        ------------------------
        
        submitString
        result
        ret
        
        Functions Called
        ----------------
        
        JOptionPane.showConfirmDialog
        readcsv243A.submitNMRexpts 
        self.panelStatusLabel.setBackground
        """
        
        # Ask for starting carousel position and submit experimets to topspin
        # obtain file name of CSV file
        selected = self.list.selectedIndex
        grp = self.panelTableIn.dataTableModel.dataVector[0][5]
        nme = self.panelTableIn.dataTableModel.dataVector[0][2]
        csvName = "blck_" + self.blocksData[selected] + "_" + grp + "_" + nme[:-2] + ".csv"
        
        # if no selected file and table is empty just return
        if self.label.text == "Selected File":
            return
        
        # check that we are not overwriting a sample that has already been submitted
        
        # get holder positions
        
        blocknums = {}
        for  row in self.panelTableIn.dataTableModel.dataVector:            
            if int(row[1]) == 0: 
                continue
            blocknums[int(row[1])] = 1
            
        for b in blocknums.keys():
            if not self.carouselin.cbuttons[b]['empty']:
                # send out error message
                JOptionPane.showMessageDialog(self.frame, "Carousel position " + str(b) + " already has sample in it")
                return
        
        # Create check dialog before submitting data to automation
        #self.dataTableModel.dataVector
#        submitString = "submit " + csvName + " starting at carousel position " + self.carouselStartingPosition.text 
        submitString = "submit " + csvName + " starting at carousel position " + str((self.panelTableIn.dataTableModel.dataVector)[0][1]) 
        result = JOptionPane.showConfirmDialog(self.frame, submitString )
        
        # if submission confirmed 
        if result == 0:
            
            # expand table for the experiments
            expandedtable = []
            
            # print dir(self.dataTableModel.dataVector)
            for row in self.panelTableIn.dataTableModel.dataVector:
                
                for expt in row[3].split(','):
                    row2 = []
                    row[3] = expt.strip()
                    for item in row:
                        row2.append(item)                        
                    expandedtable.append(row2)
                    
            # submit csv file to automation
            
            ret = readcsv243A.submitNMRexpts( [expandedtable, csvName, self.carouselStartingPosition.text] )
            # if successful or not update status string
            if ret == 0:
                self.statusLabel.text = "File " + csvName + " Submitted to TOPSPIN  Starting at Carousel Position " + str((self.panelTableIn.dataTableModel.dataVector)[0][1])         
                self.panelStatusLabel.setBackground(Color.GREEN)
            elif ret == 1:
                self.statusLabel.text = "Carousel Position not a number"
                self.panelStatusLabel.setBackground(Color.RED)
            elif ret == 2:
                self.statusLabel.text = "Incompatible experiment chosen for spectrometer"
                self.panelStatusLabel.setBackground(Color.RED)        
            elif ret == 3:
                self.statusLabel.text = "A holder starting position is not between 1 and 60 inclusive"
                self.panelStatusLabel.setBackground(Color.RED)
            elif ret == 4:
                self.statusLabel.text = "Too many samples for starting position chosen"
                self.panelStatusLabel.setBackground(Color.RED)
            
            # if an error occured display error message also in a warning dialog too.            
            if ret in [1,2,3,4]:
                JOptionPane.showMessageDialog(self.frame, self.statusLabel.text)
                return
                
            # if no error occured move files to different directory to hide them
            # add the timestamp to the file filename when moving
            
            for fn in self.submitList:
                shutil.move(os.path.join(JBrukerSubmit.pending_directory,fn), 
                            os.path.join(JBrukerSubmit.submitted_directory, nme + "_" + fn))
                
            # if no error change carousel grid to red            
            blocknums = {}
            for  row in self.panelTableIn.dataTableModel.dataVector:
                # print(row[1])
                blocknums[int(row[1])] = 1
                
            for b in blocknums.keys():
                # print(b)
                if b == 0: continue
                self.carouselin.cbuttons[b]['empty'] = not self.carouselin.cbuttons[b]['empty']
                
        
                if self.carouselin.cbuttons[b]['empty']:
                    # chamge background color to green
                    self.carouselin.cbuttons[b]['button'].background = Color.green
                else:
                    # change button background color to red
                    self.carouselin.cbuttons[b]['button'].background = Color.red
                    
            # if no error update Carousel positions
            # make sure last entry was not highfield as its carousel number will be zero
            # so loop through until we find last low field sample
            for rw in self.panelTableIn.dataTableModel.dataVector[::-1]:
                if rw[1] > 0:
                    self.cnumber = int(rw[1]) + 1
                    break

            # if next carousel number is  > 60 just set the next free pos
            # to 1 even it has been occupied.
            # let the user sort out the next free position manually            
            if self.cnumber > 60:
                self.cnumber = 1
            
            # print "self.cnumber", self.cnumber
            self.carouselStartingPosition.text = str(self.cnumber)
            
            # if no error write timestamps to timestamps directory
            
            for  row in self.panelTableIn.dataTableModel.dataVector:
                # print os.path.join(JBrukerSubmit.timestamp_directory, row[2])
                fp = open(os.path.join(JBrukerSubmit.timestamp_directory, row[2]), 'w')
                fp.write('1')
                fp.close()
                        
            
            # if no error clear table
                                    
            self.listInUpdate(event)

    
    def listInUpdate(self, event):
        pendingList = [f for f in os.listdir(JBrukerSubmit.pending_directory) if ".csv" in f[-5:]]
        
        bn = {}
        
        for f in pendingList:
            bn[f[:4]] = 1
            
        self.blocksData = list(bn.keys())
        self.blocksData.sort()
        

        # update the java list widget that displays the csv file names
        self.list.setListData(self.blocksData)
        
        # clear the table widget

        
        
        self.panelTableIn.tableData = [["",]*len(JBrukerSubmit.colHeads)]*10

        # display csv table in table view
        colNames = JBrukerSubmit.colHeads
        # transfer the data over to the table model
        self.panelTableIn.dataTableModel.setDataVector(self.panelTableIn.tableData, colNames)
        # display the table in the GUI
        self.panelTableIn.scrollPaneTable.getViewport().setView((self.panelTableIn.table))
        
        self.label.text = "Selected File"
        
    
    def clearCarouselInClicked(self, event):
        for k, b in self.carouselin.cbuttons.items():
            b['empty'] = True
            b['button'].background = Color.green
    
    def newTimestampInClicked(self, event):
        self.newTimestamp = not self.newTimestamp
        if self.newTimestamp:
            self.btnNewTimestamp.setBackground(Color.green)
        else:
            self.btnNewTimestamp.setBackground(self.standardBackgroundColor)
    
    def checkCarouselNumber(self, event):
        """ check that carousel field is an integer change background to white
        if okay, red if not.
        
        Paramters
        ---------
        event
     
        Returns
        -------
       
        Class Variables Accessed
        ------------------------
        self.carouselStartingPosition.text
        
        Class Variables Changed
        -----------------------
        self.cnumber  
        """
        
        self.cnumber = self.carouselStartingPosition.text
        try:
            self.cnumber = int(self.cnumber)
            self.carouselStartingPosition.background = Color.WHITE
            self.listSelect(event)
        except:
            self.carouselStartingPosition.background = Color.RED
    
    

    
   
    def init_submitlistpanel(self, pendingDirectory):
        
        
        # self.callbackfn = callbackfn
        # self.pendingDirectory = pendingDirectory
        
        
        # self.setPreferredSize(Dimension(200,525))
        
        self.pendingList = [f for f in os.listdir(pendingDirectory) if ".csv" in f[-5:]]
        
        bn = {}
        
        for f in self.pendingList:
            bn[f[:4]] = 1
        
        # print "list(bn.keys())"
        # print list(bn.keys())
        self.blocksData = list(bn.keys())
        self.blocksData.sort()
        # print JBrukerSubmit.pending_directory
        
        # self.data = self.returnCSVlist(self.hiddenFiles)
        
        self.list = JList(self.blocksData, valueChanged = self.listSelect)
        self.spane = JScrollPane()
        self.spane.setPreferredSize(Dimension(200,150))
        self.spane.getViewport().setView((self.list))
        
        
    def init_retrievelistpanel(self, submittedDirectory):
        
        
        # self.callbackfn = callbackfn
        # self.pendingDirectory = pendingDirectory
        
        
        # self.setPreferredSize(Dimension(200,525))
        
        self.submittedList = [f for f in os.listdir(submittedDirectory) if "4.csv" in f[-6:]]
        
        bn = {}
        
        for f in self.pendingList:
            bn[f[:4]] = 1
        
        # print "list(bn.keys())"
        # print list(bn.keys())
        self.blocksData = list(bn.keys())
        self.blocksData.sort()
        # print JBrukerSubmit.pending_directory
        
        # self.data = self.returnCSVlist(self.hiddenFiles)
        
        self.listOut = JList(self.submittedList, valueChanged = self.listSelectOut)
        self.spaneOut = JScrollPane()
        self.spaneOut.setPreferredSize(Dimension(200,150))
        self.spaneOut.getViewport().setView((self.listOut))
        
        
    def filterListButtonlicked(self, event):
        
        filterString = self.filterListText.text
        
        self.submittedList = [f for f in os.listdir(JBrukerSubmit.submitted_directory) if "4.csv" in f[-6:]]
        self.submittedList = [f for f in  self.submittedList if filterString in f ]
    
        self.listOut.setListData(self.submittedList)
        
        self.panelTableOut.tableData = [["",]*len(JBrukerSubmit.colHeads)]*10

        # display csv table in table view
        colNames = JBrukerSubmit.colHeads
        # transfer the data over to the table model
        self.panelTableOut.dataTableModel.setDataVector(self.panelTableOut.tableData, colNames)
        # display the table in the GUI
        self.panelTableOut.scrollPaneTable.getViewport().setView((self.panelTableOut.table))
        
     
        
    def readcsvfileOut_asdict( self, fn):

        
        # read in csv file as string then split into lines based on newline char
        expt_list = []
        
        fp = open(os.path.join(JBrukerSubmit.submitted_directory,fn), 'r')
        file_str = fp.read()
        fp.close()
        file_list = file_str.splitlines()
        
        # get column names from first row
        csvkeys = [ k.strip().strip('"') for k in file_list[0].split(',') ]
         
        # process the rest of lines and save each row as a dictionary and add to a list
        # if there are empty lines in the csv file break out of for loop  
        newsamplelist = []
        for sss in file_list[1:]:
            
            # print 'sss', sss
            dq_count = False
            wordlist = []
            letters = ''
            for c in sss:   
                if c == '"':
                    dq_count = not dq_count
                    continue
                    
                if c == ',' and not dq_count:
                    wordlist.append(letters)
                    letters = ''
                else:
                    letters += c
                    
            wordlist.append(letters)
                    
            if wordlist[0] == '':
                break
            else:
                if wordlist[0] not in newsamplelist:
                    expt_list.append(wordlist)
                    newsamplelist.append(wordlist[0])
                else:
                    # add expt to list of expt in last sample
                    expts = expt_list[-1][3]
                    expts = expts + ', ' + wordlist[3]
                    # print "expts", expts
                    expt_list[-1][3] = expts
                                    
        return  expt_list
    
    
    
    def listSelectOut(self, event):
      
        # Process the events from the list box and update the label
        # get the index from the list and then the filename 
        selected = self.listOut.selectedIndex
        if selected >= 0:
        
            # update file label and set background colour to normal
            csvName = self.submittedList[selected]

            #
            # update table by reading in csv file
            # read in csv file and store as a list of dictionaries
            # one dictionary for each line   
            fn = csvName

            self.panelTableOut.tableData = self.readcsvfileOut_asdict(fn)
            
            # print self.panelTableOut.tableData
            # display csv table in table view
            colNames = JBrukerSubmit.colHeads
            # transfer the data over to the table model
            self.panelTableOut.dataTableModel.setDataVector(self.panelTableOut.tableData, colNames)
            # display the table in the GUI
            self.panelTableOut.scrollPaneTable.getViewport().setView((self.panelTableOut.table))
            
            # colour in potential carousel positions
            
            self.colorincells(self.carouselout, self.panelTableOut)

        

    def readcsvfile_asdict( self, blockNumberStr):
        """
        reads in csv file created by excel submission form
        first line expected to be column names
        
        Parameters
        ----------
        
        self
        
        blockNumberStr: str
            holds block number
            
        Returns
        -------
        
        expt_list : list of dicts
            stores csav file as a list of dictionaries, a new dict for each row.
            keys are column headings
            
        Local Variables
        ---------------
        fp : file pointer
        file_str : str
            complete csv file read in as string
        csvkeys : list of str
            holds column headers used for dictionary
        values : list of str
            holds the information in each row of csv file
            
        """
        
        # read in csv file as string then split into lines based on newline char        
        blockNumber = int(blockNumberStr)
        
        # blockNumberList = [v for v in range(blockNumber, blockNumber+10)]
        # pendingList = [f for f in os.listdir(JBrukerSubmit.pending_directory) if ".csv" in f[-5:]]
        # submitList = [f for f in pendingList if blockNumber == int(f[:4])]
        # submitList.sort()
               # lll = [[f,time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(os.path.join(JBrukerSubmit.pending_directory,f))))] for f in os.listdir(JBrukerSubmit.pending_directory) if ('.csv' in f[-6:]) and (blockNumber  == int(f[:4]))] 
        lll = [f for f in os.listdir(JBrukerSubmit.pending_directory) if ('.csv' in f[-6:]) and (blockNumber  == int(f[:4]))]
        
        lll = [[f,os.path.getmtime(os.path.join(JBrukerSubmit.pending_directory,f))] for f in lll]
        print lll
        lll.sort(key=lambda tup: tup[1], reverse=True)
        
        submitList = [f for f,t in lll]
                
        expt_list = []
        blocknumsalreadythere = []
        
        for fn  in submitList:
            fp = open(os.path.join(JBrukerSubmit.pending_directory,fn), 'r')
            file_str = fp.read()
            fp.close()
            file_list = file_str.splitlines()
            
            # get column names from first row
            csvkeys = [ k.strip().strip('"') for k in file_list[0].split(',') ]
                      
            # process the rest of lines and save each row as a dictionary and add to a list
            # if there are empty lines in the csv file break out of for loop  
            for sss in file_list[1:]:
                # print 'sss', sss
                dq_count = False
                wordlist = []
                letters = ''
                for c in sss:   
                    if c == '"':
                        dq_count = not dq_count
                        continue
                        
                    if c == ',' and not dq_count:
                        wordlist.append(letters)
                        letters = ''
                    else:
                        letters += c
                        
                wordlist.append(letters)
                        
                if wordlist[0] == '':
                    break
                else:
                    # print wordlist
                    # set cosy to end of expts if there are any
                    # print wordlist[1]
                    if 'cosy' in [ s.strip() for s in  wordlist[1].split(',')]:
                        lll = [ s.strip() for s in  wordlist[1].split(',')]
                        
                        lll.remove('cosy')   
                        lll.append('cosy')                       
                        wordlist[1] = ', '.join(lll)
                        
                    elif "cosyeee" in wordlist[1].split(','):
                        lll = [ s.strip() for s in  wordlist[1].split(',')]
                        
                        lll.remove('cosyeee')  
                        lll.append('cosyeee') 
                        wordlist[1] = ', '.join(lll)
                        
                        
                    if wordlist[0] not in blocknumsalreadythere:
                        blocknumsalreadythere.append(wordlist[0])
                        
                        expt_dict = dict(zip(csvkeys, [s.strip('"') for s in wordlist]))
                        
                        expt_list.append(expt_dict)
                                    
        return submitList, expt_list
        
            
        
    def listSelect(self,event):
        """When a new csv file is selected from the list
        read in the file and display its contents in the table.
        Unordered csv files will be ordered based on the block/sample number.
        A holder column will be added to the CSV data based on the carousel 
        starting position.
        
        Parameters
        ----------
        
        event
        
        Returns
        -------
        
        Nothing
        
        Global Variables
        ----------------
        
        JBrukerSubmit.colHeads
        
        Local Variables
        ---------------
        selected
        csvName
        fn
        ok
        pulseSequence
        warningText

        Class Variables Accessed
        ------------------------
       
        self.list.selectedIndex
        self.carouselStartingPosition.text
        
        Class Variables Changed
        -----------------------
        
        self.label.text
        self.panelLabel : background
        self.statusLabel.text
        self.panelStatusLabel : background        
        self.expt_list
        self.cnumber
        self.carouselStartingPosition.text
        self.tableData

        
        Functions Called
        ----------------
        
        self.readcsvfile_asdict
        returnJTableData
        self.dataTableModel.setDataVector
        self.scrollPaneTable.getViewport().setView
        JOptionPane.showMessageDialog
        checkExperimentsWillRun
        
        """
        
        # Process the events from the list box and update the label
        # get the index from the list and then the filename 
        selected = self.list.selectedIndex
        if selected >= 0:
        
            # update file label and set background colour to normal
            csvName = self.blocksData[selected]
            self.label.text = csvName
            self.panelLabel.setBackground(self.standardBackgroundColor)
            
            # reset status label
            self.statusLabel.text = "Status"
            self.panelStatusLabel.setBackground(self.standardBackgroundColor)
            #
            # update table by reading in csv file
            # read in csv file and store as a list of dictionaries
            # one dictionary for each line   
            fn = csvName
            self.submitList, self.expt_list = self.readcsvfile_asdict(fn)

            # get carousel starting position, if the value cannot be converted
            # to an integer reset it to 1 and reset the GUI to 1
            try:
                self.cnumber = int(self.carouselStartingPosition.text)
            except:
                self.cnumber = 1
                self.carouselStartingPosition.text = "1"
            
            # get the csv data into a list of lists form ready for displaying
            self.panelTableIn.tableData = returnJTableData( self.expt_list, 
                                              self.cnumber, 
                                              self.seconds_start,
                                              self.newTimestamp)
            #  reset newTimeStamp just in case
            # self.newTimestamp = False

            # display csv table in table view
            colNames = JBrukerSubmit.colHeads
            # transfer the data over to the table model
            self.panelTableIn.dataTableModel.setDataVector(self.panelTableIn.tableData, colNames)
            # display the table in the GUI
            self.panelTableIn.scrollPaneTable.getViewport().setView((self.panelTableIn.table))
            
            # check to see if experiments will run on the spectometer
            ok, pulseSequence =  checkExperimentsWillRun(self.expt_list)
                
            if not ok:
                # display warning dialog
                warningText = pulseSequence + " cannot be run on this spectrometer"
                JOptionPane.showMessageDialog(self.frame, warningText);
                
                
            # colour in potential carousel positions
            
            self.colorincells(self.carouselin, self.panelTableIn)
                        
                    
                
             
    def colorincells(self, carousel, paneltable):
    
        for k in range(1,61):
            if carousel.cbuttons[k]['empty']:
                carousel.cbuttons[k]['button'].background = Color.green
            else:
                carousel.cbuttons[k]['button'].background = Color.red
        
        for row in paneltable.dataTableModel.getDataVector():
            # print "row"
            # print row
           
            k = int(row[1])
            # print 'k', k
            
            if k == 0: continue
            
            if carousel.cbuttons[k]['empty']:
                carousel.cbuttons[k]['button'].background = Color.pink
            else:
                carousel.cbuttons[k]['button'].background = Color.orange
    


    def tableMouseClicked(self, event):
        """
        Prior to editing the user will click the holder number cell
        more often than not. This function saves the cell row and column and
        the value in the cell prior to editing.
        
        Parameters
        ----------
        event
        
        Returns
        -------
        Nothing
        
        Global Variables
        ----------------
        
        Local Variables
        ---------------
        tble

        Class Variables Accessed
        ------------------------
        
        Class Variables Changed
        -----------------------
        self.rw
        self.cl
        self.oldHolderValue
        
        Functions Called
        ----------------
        tble.getSelectedRow
        tble.getSelectedColumn
        tble.getValueAt
        """
        
        tble = event.getSource()
        self.rw = tble.getSelectedRow()
        self.cl = tble.getSelectedColumn()
        self.oldHolderValue = tble.getValueAt(self.rw, self.cl)

        
    def tableChangedCB(self,event):
        """
        Function is called when a cell is being edited. After the user 
        presses return the data is updated.
        Should only work if Holder column is being edited
        
        Parameters
        ----------
        
        Returns
        -------
        
        Global Variables
        ----------------
        
        Local Variables
        ---------------
        tble
        vlue
        blckNumber
        holderAlreadyOccupied
        tableValues
        warningText

        Class Variables Accessed
        ------------------------
        self.dataTableModel.dataVector
        
        Class Variables Changed
        -----------------------
        
        Functions Called
        ----------------
        event.getSource
        tble.setValueAt
        JOptionPane.showMessageDialog
        """
        
        tble = event.getSource()
        if (event.keyChar == "\n") and (self.cl > 2):
            tble.setValueAt(self.oldHolderValue, self.rw, self.cl )
            
        elif (event.keyChar == "\n") and (self.cl == 1):
            vlue = tble.getValueAt(self.rw, self.cl)

            # check to see if new holder number is used by another sample
            # get block number of sample changed
            blckNumber = tble.getValueAt(self.rw, 0)

            # get values in table
            holderAlreadyOccupied = False
            tableValues = self.panelTableIn.dataTableModel.dataVector
            for i, rw in enumerate(tableValues):
                if (int(rw[1]) == int(vlue))  and (int(blckNumber) != int(rw[0])):
                    tble.setValueAt(int(self.oldHolderValue), self.rw, 1 )
                    holderAlreadyOccupied = True
                    warningText = "Holder " + str(vlue) + " already used for sample " + str(rw[0])
                    JOptionPane.showMessageDialog(self.frame, warningText);

                    break  
            #
            # check to see if any other rows with same sample number need to be updated
            if not holderAlreadyOccupied:
                for i, rw in enumerate(tableValues):
                    if int(blckNumber) == int(rw[0]):
                        tble.setValueAt(int(vlue), i, 1 )
                        
            # change cell colors
            self.colorincells(self.carouselin, self.panelTableIn)


    def __init__(self):
        
        self.rw = 0 # table row
        self.cl = 0 # table column
        self.newTimestamp = False
        
        computer_name = platform.node()
        spec_name = readcsv243A.spectrometers[computer_name]
        
        self.seconds_offset  = {'A4': 60, 'B4': 70, 'N4': 80}
        
        self.seconds_start = self.seconds_offset[spec_name]
        
        self.frame = JFrame("Submit NMR Experiments")
        self.frame.setSize(1200, 550)
        self.frame.setLayout(BorderLayout())
        self.frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE)
        
        tabbedPane = JTabbedPane()
        self.frame.contentPane.add("Center", tabbedPane);
        
        firstTab = JPanel()
        firstTab.setLayout(BorderLayout())
        tabbedPane.addTab("Submit Samples", firstTab)
        
        secondTab = JPanel()
        secondTab.setLayout(BorderLayout())
        tabbedPane.addTab("Retrieve Samples", secondTab)
              
        self.carouselin =  carousel()
        
        self.panelTableIn = sampleTableIn(self.tableChangedCB, self.tableMouseClicked)
        
        self.submitlistIn = JPanel() 
        self.init_submitlistpanel( JBrukerSubmit.pending_directory)
        self.submitlistIn.add(self.spane)
        
        # print "self.submitlistIn", type(self.submitlistIn)   
        btnS = JButton('Submit File',actionPerformed=self.listInSubmit)
        btnS.setPreferredSize(Dimension(200,20))
        btnU = JButton('Update List',actionPerformed=self.listInUpdate)
        btnU.setPreferredSize(Dimension(200,20))
        btnClearCarousel = JButton('Clear Carousel', actionPerformed=self.clearCarouselInClicked)
        self.btnNewTimestamp = JButton('New Time Stamp', actionPerformed = self.newTimestampInClicked)
        
        self.carouselLabel = JLabel( "Carousel Position", JLabel.CENTER)
        self.carouselStartingPosition = JTextField('1',13, keyPressed = self.checkCarouselNumber)
               
        # label displaying CSV file selected
        self.label = JLabel('Selected File', JLabel.CENTER)
        self.panelLabel = JPanel()
        self.panelLabel.add( self.label)
        self.standardBackgroundColor = self.panelLabel.getBackground()
        
        # label to display warnings and confirm expriments submitted
        self.statusLabel = JLabel('Status', JLabel.CENTER)
        self.panelStatusLabel = JPanel()
        self.panelStatusLabel.add( self.statusLabel)
        
        centerPanelIn = JPanel()
        centerPanelIn.setLayout(FlowLayout())
        
        centerPanelIn.add(self.panelTableIn)
        centerPanelIn.add(self.carouselin)
        centerPanelIn.add(btnClearCarousel)
        
        leftPanelIn = JPanel()
        leftPanelIn.setLayout(FlowLayout())
        leftPanelIn.setPreferredSize(Dimension(220,500))
        
        leftPanelIn.add(btnU)
        leftPanelIn.add(self.submitlistIn)
        leftPanelIn.add(self.btnNewTimestamp)
        # panelList.add(btnShowAllFiles)
        leftPanelIn.add(self.carouselLabel)
        leftPanelIn.add(self.carouselStartingPosition)
        leftPanelIn.add(btnS)
        
        # set preferred size of buttons
        self.btnNewTimestamp.setPreferredSize(Dimension(200,20))
        btnClearCarousel.setPreferredSize(Dimension(900, 20))
        
        # self.carouselpanelin = carousel(self.carouselin)
        firstTab.add(self.panelLabel, BorderLayout.NORTH)
        firstTab.add( leftPanelIn, BorderLayout.WEST)
        firstTab.add(centerPanelIn,  BorderLayout.CENTER)
        firstTab.add(self.panelStatusLabel, BorderLayout.SOUTH)
          
        # create second tab
        self.carouselout =  carousel()
        self.panelTableOut = sampleTableOut()
        
        centerPanelOut = JPanel()
        centerPanelOut.setLayout(FlowLayout())
        
        centerPanelOut.add( self.panelTableOut)
        centerPanelOut.add(self.carouselout)
        
        self.filterListText = JTextField('', 16)
        filterListButton = JButton('Filter List', actionPerformed=self.filterListButtonlicked)        
        self.submitlistOut = JPanel() 
        self.init_retrievelistpanel( JBrukerSubmit.submitted_directory)
        self.submitlistOut.add(self.spaneOut)
        
        leftPanelOut = JPanel()
        leftPanelOut.setLayout(FlowLayout())
        leftPanelOut.setPreferredSize(Dimension(220,500))
        
        leftPanelOut.add(self.filterListText)
        leftPanelOut.add(filterListButton)
        leftPanelOut.add(self.submitlistOut)
      
        secondTab.add(centerPanelOut,  BorderLayout.CENTER)
        secondTab.add(leftPanelOut,  BorderLayout.WEST)
                
        self.frame.setVisible(True)
        
        
if __name__ == "__main__":
    JBrukerSubmit()