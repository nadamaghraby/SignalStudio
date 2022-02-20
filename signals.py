from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication
import pyqtgraph as pg
import matplotlib.pyplot as plt



class graph(object):
    channelIdx = 0
    channels = []
    styles = {'color':'b', 'font-size':'10px'}   
    @classmethod 
    def createPlotWidget(cls):
        cls.graphWidget = pg.PlotWidget()
        cls.graphWidget.setBackground('black')
        cls.graphWidget.setStyleSheet("background-color: rgb(255, 255, 255);")
        cls.graphWidget.setLabel('left', 'Amplitude', **cls.styles)
        cls.graphWidget.setLabel('bottom', 'time (sec)', **cls.styles)
        cls.graphWidget.showGrid(x=True, y=True)
        cls.graphWidget.setXRange(0, 0.7)
        return cls.graphWidget



class signal(object):
    timer = QtCore.QTimer()
    penColors = [(255, 0, 0), (0, 255, 0), (0, 0, 255),(255, 247, 0), (162, 22, 232), (235, 145, 29)] 
    colors = ['r','g','b','y','purple','orange']
    signalNames = ['signal1','signal2','signal3','signal4','signal5','signal6']
    cmaps = ["viridis","plasma","cividis","magma","inferno"]

    freeChannelsNum = 6
    
    def __init__(self, x, y):
        self.time = x.copy()
        self.amplitude = y.copy()
        self.zoomFactor = 1
        self.startTimeIdx = 0
        self.startAmpIdx = -1 * self.zoomFactor
        self.endTimeIdx = 100 * self.zoomFactor
        self.endAmpIdx = 1 * self.zoomFactor
        self.__class__.timer.setInterval(100) # ms interval
        

    
        if self.__class__.freeChannelsNum > 0:
            #print("length of graph channels = {}".format(len(graph.channels)))
            self.channelIdx = - self.__class__.freeChannelsNum 
            self.penColor = self.penColors[self.channelIdx]
            self.cmap = self.cmaps[self.channelIdx % len(self.cmaps)]
            self.show = True
            self.vmin=0
            self.vmax=100
            self.signalName = self.signalNames[self.channelIdx]
            #print(self.signalName)
            self.plot(self.penColor,self.signalName)
            self.__class__.freeChannelsNum = self.__class__.freeChannelsNum - 1
            #print("updated free channels number = {}".format(self.__class__.freeChannelsNum))
            #print(graph.graphWidget.getViewBox().getState().get('viewRange'))
            
        else:
            print("no free channel is available, clear channels first!")
        
        
    def plot(self,color,sigName):
        if self.show:
            graph.graphWidget.setXRange(0, self.time[self.endTimeIdx])
            graph.graphWidget.setYRange(-1 * self.zoomFactor , 1 * self.zoomFactor)
            self.pen = pg.mkPen(color=color)
            graph.graphWidget.addLegend()
            graph.graphWidget.plot(self.time, self.amplitude, pen=self.pen, name = sigName)
        else:
            pass
        
    

    def moveGraph(self, speed):
        try:
            self.startTimeIdx = self.startTimeIdx + speed
            self.endTimeIdx = self.endTimeIdx + speed
            graph.graphWidget.setXRange(self.time[self.startTimeIdx], self.time[self.endTimeIdx])
        except:
            self.startTimeIdx = 0
            self.endTimeIdx = 100 * self.zoomFactor
            graph.graphWidget.setXRange(self.time[self.startTimeIdx], self.time[self.endTimeIdx])

    def zoomIn(self):
        if self.zoomFactor >= 0.2:
            self.zoomFactor = self.zoomFactor - 0.1
            self.adjustGraph()
    def zoomOut(self):
        if self.zoomFactor < 3.0:
            self.zoomFactor = self.zoomFactor + 0.1
            self.adjustGraph()
            
    def adjustGraph(self):
        self.endTimeIdx = int(self.startTimeIdx + (100 * self.zoomFactor))
        graph.graphWidget.setXRange(self.time[self.startTimeIdx], self.time[self.endTimeIdx])
        graph.graphWidget.setYRange(-1 * self.zoomFactor , 1 * self.zoomFactor)
        
    def getFigure(self,signame):
        fig = plt.figure(figsize=(10, 5))
        plt.plot(self.time[self.startTimeIdx:self.endTimeIdx],self.amplitude[self.startTimeIdx:self.endTimeIdx],color='b')
        plt.xlabel('time (sec)')
        plt.ylabel('amplitude (mv)')
        plt.title("Graph of " + signame)
        return fig

    def getSpectrogram(self,vmin,vmax,signame):
        fig = plt.figure(figsize=(10, 5))
        plt.specgram(self.amplitude, Fs= 50,cmap=self.cmap,vmin=vmin,vmax=vmax)
        plt.xlabel('time (sec)')
        plt.ylabel('frequency (Hz)')
        plt.title("Spectrogram of " + signame)
        return fig
