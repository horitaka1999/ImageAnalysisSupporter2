import sys
from vectorSupport import pcaVector
from matplotlib.figure import Figure
import SimpleITK as sitk
import os
from math import sqrt
from sympy import geometry as Gt
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, uic, QtCore,QtGui
from PyQt5.QtWidgets import QFileDialog,QMessageBox,QSlider
import matplotlib as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from matplotlib import patches
from Contours import ContorProduce
import polygonSupport as Ps
if not os.path.exists('data'):
    os.mkdir('data')
SAVE_PATH = 'data/sliced.npy'
StyleSheet = '''
        *{
            font-weight: bold;
        }
        QMainWindow{
            background-color:rgba(148,87,168,0.5);
        }
        QLabel{
            background-color:rgba(0,0,0,0.5);
            color: white;
        }
        QLineEdit{
            border-radius:8px;
            background-color:rgba(0,0,0,0.5);
            color: white;
        }
        QLineEdit:hover{
        }
        QPushButton{
            background-color: rgba(0,0,0,0.5);
            border-color: white;
            color :white;
        }
        QPushButton:hover{
            padding-top: 10px;
            padding-bottom: 5px;
        }
        QComboBox{
            background-color: rgba(0,0,0,0.1);
            color :black;
        }
        QSlider{
            background-color: rgba(0,0,0,0.5);

        }
        
                
        '''

def loadNII(file_path): #return numpy array
    tmp = os.path.splitext(file_path)
    if not(tmp[1] == '.nii' or tmp[1]== '.gz'):
       return np.array([]) 
    image = sitk.ReadImage(file_path)
    ndrev = sitk.GetArrayFromImage(image)
    return ndrev

class Application(QtWidgets.QMainWindow):
    def __init__(self):
        # Call the inherited classes __init__ method
        super().__init__()
        #UIの初期化

        self.initUI()
        self.Setting()
        self.initFigure()
        self.initContorFigure()
        self.initPolygonFigure()
        self.initshowFigure()
        
    def Setting(self):
        self.anno = False
        self.setStyleSheet(StyleSheet)
        self.Loaded = False
        self.fixed = False
        self.kParameterWidget.setValidator(QtGui.QIntValidator())
        self.FileBrowser.clicked.connect(self.showDIALOG)
        self.NiiList.currentIndexChanged.connect(lambda: self.showNii(self.NiiList.currentText()))
        self.ContorList.currentIndexChanged.connect(lambda: self.showContor(self.ContorList.currentText()))
        
    def initUI(self):
        self.resize(1650,800)#ウィンドウサイズの変更
        self.FigureWidget = QtWidgets.QWidget(self)
        self.FigureWidget.setGeometry(10,50,600,600) 
        # FigureWidgetにLayoutを追加
        self.FigureLayout = QtWidgets.QVBoxLayout(self.FigureWidget)
        self.FigureLayout.setContentsMargins(0,0,0,0)
        #Contorを表示するwidgetを追加
        self.ContorFigureWidget = QtWidgets.QWidget(self)
        self.ContorFigureWidget.setGeometry(700,50,600,600)
       #ContorWidget用のlayoutを追加 
        self.ContorFigureLayout = QtWidgets.QVBoxLayout(self.ContorFigureWidget)
        self.ContorFigureLayout.setContentsMargins(0,0,0,0)

        #PolygonDataAnalysis用のFigureqwidget
        self.PolygonWidget = QtWidgets.QWidget(self)
        self.PolygonWidget.setGeometry(1310,50,300,300)
        self.PolygonLayout = QtWidgets.QVBoxLayout(self.PolygonWidget)
        self.PolygonLayout.setContentsMargins(0,0,0,0)

        self.ContorList = QtWidgets.QComboBox(self)
        self.ContorList.setGeometry(750,10,50,20)

        self.FileBrowser = QtWidgets.QPushButton('select file',self)
        self.FileBrowser.move(0,10)

        self.NiiList =QtWidgets.QComboBox(self) 
        self.NiiList.setGeometry(550,10,50,20)

        self.FileNameText = QtWidgets.QLabel(self)
        self.FileNameText.setText('your selected file path')
        self.FileNameText.setGeometry(110,10,300,30)
        
        self.Output = QtWidgets.QLabel(self)
        self.Output.setText('Output')
        self.Output.setGeometry(820,10,100,30)
        
        self.VectorOutput = QtWidgets.QLabel(self)
        self.VectorOutput.setText('culcurated Score')
        self.VectorOutput.setGeometry(950,10,200,30)

        self.kParameterNotionText = QtWidgets.QLabel(self)
        self.kParameterNotionText.setText('kparameter')
        self.kParameterNotionText.setGeometry(1200,10,100,30)

        self.kParameterWidget = QtWidgets.QLineEdit(self)
        self.kParameterWidget.setGeometry(1350,10,30,30)

        self.showFigureWidget = QtWidgets.QWidget(self)
        self.showFigureWidget.setGeometry(1310,360,300,300)
        self.showFigureLayout = QtWidgets.QVBoxLayout(self.showFigureWidget)
        self.showFigureLayout.setContentsMargins(0,0,0,0)

    def initSlider(self,vmax):
        if self.Loaded:
            self.sld.setParent(None)
        self.sld = QtWidgets.QSlider(Qt.Vertical,self)
        self.sld.setMinimum(0)
        self.sld.setMaximum(vmax)
        self.sld.setFocusPolicy(Qt.NoFocus)
        self.sld.setGeometry(650,50,20,600)
        self.sld.setValue(0)
        self.sld.setSingleStep(1)
        self.sld.valueChanged.connect(self.valueChange)
        self.sld.show()

    def valueChange(self):
        self.showNii(str(self.sld.value()))

    def initContorFigure(self):
        self.ContorFigure = plt.figure.Figure()
        self.ContorFigureCanvas = FigureCanvas(self.ContorFigure)
        self.ContorFigureCanvas.mpl_connect('motion_notify_event',self.mouse_move)

        self.ContorFigureCanvas.mpl_connect('button_press_event',self.onclick)

        self.ContorFigureLayout.addWidget(self.ContorFigureCanvas)
        self.contor_axes = self.ContorFigure.add_subplot(1,1,1)
        self.contor_axes.set_aspect('equal')
        self.contor_axes.axis('off')
    
    def initFigure(self):
        self.Figure = plt.figure.Figure()
        # FigureをFigureCanvasに追加
        self.FigureCanvas = FigureCanvas(self.Figure)
        # LayoutにFigureCanvasを追加
        self.FigureLayout.addWidget(self.FigureCanvas)
        #figureからaxesを作成
        self.axes = self.Figure.add_subplot(1,1,1)
        self.axes.axis('off')

    def initPolygonFigure(self):
        self.PolygonFigure = plt.figure.Figure()
        self.PolygonFigureCanvas = FigureCanvas(self.PolygonFigure)
        self.PolygonLayout.addWidget(self.PolygonFigureCanvas)
        self.polygon_axes = self.PolygonFigure.add_subplot(1,1,1)
        self.polygon_axes.set_aspect('equal')
        self.polygon_axes.axis('off')

    def initshowFigure(self):
        self.showFigure = plt.figure.Figure()
        self.showFigureCanvas = FigureCanvas(self.showFigure)
        self.showFigureLayout.addWidget(self.showFigureCanvas)
        self.showFigure_axes = self.showFigure.add_subplot(1,1,1)
        self.showFigure_axes.set_aspect('equal')
        self.showFigure_axes.axis('off')
    
    def updateFigure(self):
        self.FigureCanvas.draw()

    def updateContorFigure(self):
        self.ContorFigureCanvas.draw()

    def updatePolygonFigure(self):
        self.PolygonFigureCanvas.draw()

    def updateShowFigure(self):
        self.showFigureCanvas.draw()

    def showDIALOG(self):
        self.NiiList.clear()
        self.NiiLength = 0
        # 第二引数はダイアログのタイトル、第三引数は表示するパス
        fname = QFileDialog.getOpenFileName(self, 'Open file', './')
        FILEPATH = fname[0]
        self.FileNameText.setText(FILEPATH)
        NII_Data = loadNII(FILEPATH)
        if len(NII_Data) > 0:
            self.NiiLength = len(NII_Data) 
            np.save(SAVE_PATH,NII_Data)
            for index in range(self.NiiLength):
                self.NiiList.addItem(str(index))
            self.initSlider(self.NiiLength-1)
            self.Loaded = True
        else:
            self.Loaded = False
            dlg = QMessageBox(self)
            dlg.setWindowTitle('error')
            dlg.setText('input file  needs to be .nii file')
            dlg.exec()

    def showNii(self,index):#indexがstr型でくる
        self.axes.cla()
        self.axes.axis('off')
        self.ContorList.clear()
        if index == '':
            return
        index = int(index)
        self.NII_IMAGE= np.load(SAVE_PATH)[index]
        self.ContorData = ContorProduce(self.NII_IMAGE)#画像選択時にその輪郭データを作成
        for i in range(len(self.ContorData.contours)):
            self.ContorList.addItem(str(i))
        tmp = self.NII_IMAGE
        self.axes.imshow(self.NII_IMAGE)
        self.updateFigure()
        
    def showContor(self,index):#indexがstr型でくる
        self.contor_axes.cla()#前のplotデータの削除
        if index == '':
            return
        index = int(index)
        self.ContorBox = self.ContorData.produce(index)
        X = self.ContorBox[:,0]
        Y = self.ContorBox[:,1]
        self.anno = self.contor_axes.scatter(X,Y,c='blue',s=10)
        self.contor_axes.axis('off')
        self.pca = pcaVector(self.ContorBox)#Contor表示時にpcaを計算,defaultで５つの近傍
        self.pca.saveData()
        self.updateContorFigure()

    def showSelectedContor(self,ContorBox,index,kParameter):
        self.contor_axes.cla()
        self.selected_x = []
        self.selected_y = []
        selected_polygon = []
        selected_polygon2 = [] # tuple型
        for i in range(index-kParameter,index+kParameter):
            if 0 <= i < len(ContorBox):
                self.selected_x.append(ContorBox[i][0])
                self.selected_y.append(ContorBox[i][1])
                selected_polygon.append([ContorBox[i][0],ContorBox[i][1]])
                selected_polygon2.append((ContorBox[i][0],ContorBox[i][1]))
        self.PolygonData = Gt.Polygon(*selected_polygon2)#Polygonの面積評価などに必要
        X = self.ContorBox[:,0]
        Y = self.ContorBox[:,1]

        self.anno = self.contor_axes.scatter(X,Y,c = 'blue',s=10)
        self.contor_axes.scatter(self.selected_x,self.selected_y,c = 'red',s=10)
        self.contor_axes.axis('off')
        #polygon の表示
        self.showPolygon(selected_polygon)
        self.drawPolygon(selected_polygon)

        self.updateContorFigure()
        return

    def showPolygon(self,selected_polygon):
        
        self.patch = patches.Polygon(xy=selected_polygon, closed=True)
        self.contor_axes.add_patch(self.patch)
    
    def drawPolygon(self,selected_polygon):
        self.polygon_axes.cla()
        vec = (selected_polygon[-1][0] - selected_polygon[0][0],selected_polygon[-1][1] - selected_polygon[0][1])
        self.rotatePolygon = Ps.rotate(vec,selected_polygon,int(self.PolygonData.area) > 0)
        X = np.array(self.rotatePolygon)[:,0]
        Y = np.array(self.rotatePolygon)[:,1]
        self.polygon_axes.scatter(X,Y,c='red',s=10)
        self.patch2 = patches.Polygon(xy=self.rotatePolygon, closed=True)
        self.polygon_axes.add_patch(self.patch2)
        #self.polygon_axes.axis('off')
        self.updatePolygonFigure()
        
    def mouse_move(self,event):#ContorFigure Clicked Event
        if self.fixed:
            return
        x = event.xdata
        y = event.ydata
        if event.inaxes != self.contor_axes or  self.anno == False:
            return
        cont,rev = self.anno.contains(event)
        if not cont:
            self.Output.setText('cannot calculate!')
            return 
        if cont:
            self.kParameter = 16
            if self.kParameterWidget.text().isdecimal():
                self.kParameter = int(self.kParameterWidget.text())
            self.Currentindex = rev['ind'][0]
            self.showSelectedContor(self.ContorBox,self.Currentindex,self.kParameter)
            self.showCalc()
        if self.Currentindex >= len(self.ContorBox):
            print('error')
            return



    def showPolygonImage(self):
        score = 0
        rotatePolygon = np.array(self.rotatePolygon,dtype = np.uint8)

        self.filledPolygon = Ps.fillPolygon(rotatePolygon)
        self.polygon_axes.cla()
        self.polygon_axes.imshow(self.filledPolygon)
        self.updatePolygonFigure()
        return 
        
    def showPolygonScore(self):
        self.showFigure_axes.cla()
        data = Ps.calcCost(self.filledPolygon)
        data = np.array(data)
        X = data[:,0]
        Y = data[:,1]
        self.showFigure_axes.scatter(X,Y)
        self.updateShowFigure()
        return


    def onclick(self,event):
        if self.fixed:
            self.fixed = False#固定を解除
            return
        self.fixed = True
        self.showPolygonImage()
        self.showPolygonScore()
        return


    def showCalc(self):#面積の表示
        self.Output.setText(str(int(self.PolygonData.area)))
       
        
def main():
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = Application()
    mainwindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()