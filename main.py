# libraries needed for main python file
# the file we run for the app to work
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QScrollArea
import sys
from signals import  graph, signal
from gui import Ui_MainWindow
import numpy as np
import os
import math
import pathlib
import pyqtgraph as pg
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


# class definition for application window components like the ui

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.channelselector.setRange(1, 3)
        self.ui.open.triggered.connect(self.open)
        self.ui.save.triggered.connect(self.saveAs)
        self.ui.pushButtonplay.clicked.connect(self.startChannels)
        self.ui.pushButtonpause.clicked.connect(self.pauseChannels)
        self.ui.pushButtonzoomin.clicked.connect(self.zoomIn)
        self.ui.pushButtonzoomout.clicked.connect(self.zoomOut)
        self.ui.comboBoxcolor.currentIndexChanged.connect(self.changeColor)
        self.ui.comboBoxspectrosig.currentIndexChanged.connect(self.changeSpectroProperties)
        self.ui.comboBoxcolorpal.currentTextChanged.connect(self.changeSpectroProperties)
        self.ui.horizontalSliderspectromax.valueChanged.connect(self.changeSpectroProperties)
        self.ui.horizontalSliderspectromin.valueChanged.connect(self.changeSpectroProperties)
        self.ui.pushButtonChangeLabel.clicked.connect(self.changelabel)
        self.ui.pushButtonHideSignal.clicked.connect(self.hideSignals)
        self.ui.pushButtonShowSignal.clicked.connect(self.showSignals)
        self.ui.horizontalScrollBarsig1.valueChanged.connect(self.horizontalScrollBarMovement)
        self.ui.verticalScrollBarsig1.valueChanged.connect(self.veritcalScrollBarMovement)
        signal.timer.timeout.connect(self.moveSignals)
        
        

        self.signals = []
        self.signalsMaxValueX = []
        self.signalsMaxValueY = []
        self.signalsMinValueY = []
        self.channelColor=[]
        self.currentVerticalValue = 0
        self.currentHorizontalValue = 0

    def zoomIn(self):
        try:
            for signal in self.signals:
                signal.zoomIn()
        except:
            pass

    def zoomOut(self):
        try:
            for signal in self.signals:
                signal.zoomOut()
        except:
            pass

    def open(self):
        files_name = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open only txt or CSV', os.getenv('HOME'), "csv(*.csv);; text(*.txt)")
        path = files_name[0]

        if pathlib.Path(path).suffix == ".txt":
            data = np.genfromtxt(path, delimiter=',')
            x = data[:, 0]
            y = data[:, 1]
            x = list(x[:])
            y = list(y[:])
            self.signalsMaxValueX.append(max(x))
            self.signalsMaxValueY.append(max(y))
            self.signalsMinValueY.append(min(y))
            self.adjustGraphBoundaries()
            sigData = signal(x, y)
            self.signals.append(sigData)

        elif pathlib.Path(path).suffix == ".csv":
            data = pd.read_csv(path)
            x = data.values[:, 0]
            y = data.values[:, 1]
            x = list(x[:])
            y = list(y[:])
            self.signalsMaxValueX.append(max(x))
            self.signalsMaxValueY.append(max(y))
            self.signalsMinValueY.append(min(y))
            self.adjustGraphBoundaries()
            sigData = signal(x, y)
            self.signals.append(sigData)

    def moveSignals(self):
        for signal in self.signals:
            signal.moveGraph(self.ui.horizontalSlidersignalsspeed.value())


    def startChannels(self):
        for signal in self.signals:
            signal.timer.start()
  

    def pauseChannels(self):
        for signal in self.signals:
            signal.timer.stop()


    def adjustGraphBoundaries(self):
      graph.graphWidget.plotItem.vb.setLimits(xMin=0,xMax=max(self.signalsMaxValueX),yMin=min(self.signalsMinValueY),yMax=max(self.signalsMaxValueY))

    def changeColor(self):
        selectedSignal = self.signals[self.ui.channelselector.value()-1] 
        print("signal color before change = {}".format(selectedSignal.penColor))
        selectedSignal.penColor = signal.penColors[self.ui.comboBoxcolor.currentIndex()]
        print("signal color after change = {}".format(selectedSignal.penColor))
        graph.graphWidget.clear()
        self.adjustGraphBoundaries()
        for sig in self.signals:
            if sig.show:
                sig.plot(color=sig.penColor,sigName = sig.signalName)


    def changelabel(self):
        selectedSig = self.signals[self.ui.channelselector.value()-1] 
        print("signal label before change = {}".format(selectedSig.signalName))
        selectedSig.signalName = self.ui.changesignalname.text()
        print("signal label after change = {}".format(selectedSig.signalName))
        graph.graphWidget.clear()
        self.adjustGraphBoundaries()
        for signum in self.signals:
            if signum.show:
                signum.plot(color=signum.penColor,sigName = signum.signalName)
        
        
 
    
    def hideSignals(self):   
        selectedSig = self.signals[self.ui.channelselector.value()-1]
        selectedSig.show = False
        self.signalsMaxValueX.remove(max(selectedSig.time))
        self.signalsMaxValueY.remove(max(selectedSig.amplitude))
        self.signalsMinValueY.remove(min(selectedSig.amplitude))
        graph.graphWidget.clear()
        self.adjustGraphBoundaries()
        for sigg in self.signals:
           if sigg.show:
                sigg.plot(color=sigg.penColor,sigName = sigg.signalName)
                print("graphed!!")

    def showSignals(self):   
        selectedSig = self.signals[self.ui.channelselector.value()-1]
        selectedSig.show = True
        self.signalsMaxValueX.append(max(selectedSig.time))
        self.signalsMaxValueY.append(max(selectedSig.amplitude))
        self.signalsMinValueY.append(min(selectedSig.amplitude))
        graph.graphWidget.clear()
        self.adjustGraphBoundaries()
        for sigg in self.signals:
            if sigg.show:
                sigg.plot(color=sigg.penColor,sigName = sigg.signalName)
                


    def horizontalScrollBarMovement(self):
        self.pauseChannels()
        horizontalStep = (self.ui.horizontalScrollBarsig1.value()- self.currentHorizontalValue) * (max(self.signalsMaxValueX)/100)
        graph.graphWidget.plotItem.getViewBox().translateBy(x=horizontalStep)
        self.currentHorizontalValue = self.ui.horizontalScrollBarsig1.value()


    def veritcalScrollBarMovement(self):
        self.pauseChannels()
        verticalStep = (self.ui.verticalScrollBarsig1.value()- self.currentVerticalValue)*(-max(self.signalsMaxValueY)/10)
        self.currentVerticalValue = self.ui.verticalScrollBarsig1.value()
        graph.graphWidget.plotItem.getViewBox().translateBy(y=verticalStep)
        


    def drawSpectro(self,signals): 
        try:
            currentIndex = self.ui.comboBoxspectrosig.currentIndex()
            plt.specgram(signals[currentIndex].amplitude,Fs=50,cmap=signals[currentIndex].cmap,vmin=signals[currentIndex].vmin,vmax=signals[currentIndex].vmax)
            plt.xlabel('Time (sec)')
            plt.ylabel('Frequency (Hz)')
            plt.savefig(f'signal{(currentIndex+1)}.png', dpi=300, bbox_inches='tight')
            pixmap = QPixmap(f'signal{(currentIndex+1)}.png').scaled(300,300)
            self.ui.label.setPixmap(pixmap)
            
        except:
            self.ui.label.clear()
            print("this signal is not plotted!!")

        
  

    def changeSpectroColor(self):
        try:
            selectedSignal = self.signals[self.ui.comboBoxspectrosig.currentIndex()]
            selectedSignal.cmap = self.ui.comboBoxcolorpal.currentText()
        except:
            print("This signal is not plotted!!")
            
        


    def changeSpectroBoundaries(self,signals):
        try:
            for signal in self.signals:
                signal.vmin = self.ui.horizontalSliderspectromin.value()
                signal.vmax = self.ui.horizontalSliderspectromax.value()
        except:
            print("This signal is not plotted!!")

    def changeSpectroProperties(self):
        self.changeSpectroColor()
        self.changeSpectroBoundaries(self.signals)
        self.drawSpectro(self.signals)

    def saveAs(self):
        report = PdfPages('SignalReport.pdf')
        table_header=["Signal Name","Mean (mv)","Standard Deviation (mv)","Maximum Value (mv)","Minimum Value (mv)","Duration (sec)"]
        table_data=[table_header]
        for signal in self.signals:
            if signal.show:
                report.savefig(signal.getFigure(signal.signalName))
                time = np.array(signal.time)
                amplitude = np.array(signal.amplitude)
                signal_info=["{}".format(signal.signalName),round(amplitude.mean(),5),round(amplitude.std(),5),round(amplitude.max(),5),round(amplitude.min(),5),round((time.max() - time.min()),5)]
                table_data.append(signal_info)
        report.savefig(self.signals[self.ui.comboBoxspectrosig.currentIndex()].getSpectrogram(self.signals[self.ui.comboBoxspectrosig.currentIndex()].vmin,self.signals[self.ui.comboBoxspectrosig.currentIndex()].vmax,
        self.signals[self.ui.comboBoxspectrosig.currentIndex()].signalName))
        fig = plt.figure(constrained_layout=True)
        fig.patch.set_visible(False)
        fig, ax = plt.subplots()
        ax.axis('off')
        ax.axis('tight')
        table = ax.table(cellText=table_data, loc='center')
        table.scale(1,2)
        fig.tight_layout()
        report.savefig()
        plt.close
        report.close()


# function for launching a QApplication and running the ui and main window
def window():
    app = QApplication(sys.argv)
    win = ApplicationWindow()
    win.show()
    sys.exit(app.exec_())


# main code
if __name__ == "__main__":
    window()
