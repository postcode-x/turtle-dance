import struct
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
import matplotlib.figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sys
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import copy
import matplotlib
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.image as image
import os
from moves import *

moves = carlton
img = image.imread('turtlelol.png')
xp, yp, __ = img.shape
x = np.arange(0, xp, 1)
y = np.arange(0, yp, 1)


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.pose_index = 0
        self.point_index = 0
        self.size = 0
        self.current_full_filename = ''
        self.current_filename = ''
        self.limits = 96

        self.x_ = []
        self.y_ = []
        self.z_ = []
        self.body_data = ()
        self.body_data_copy = ()

        self.setFixedSize(600, 632)
        self.setWindowTitle('Dancing Turtle')
        self.center()

        main_layout = QtWidgets.QVBoxLayout()
        layout_left = QtWidgets.QVBoxLayout()

        self.figure = matplotlib.figure.Figure()  # Plot
        self.canvas = FigureCanvas(self.figure)
        self.axes = Axes3D(self.figure)

        self.expression_slider = QtWidgets.QSlider(Qt.Horizontal)
        self.expression_slider.valueChanged.connect(self.expression_slider_change)
        self.expression_slider.setValue(0)
        self.expression_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.expression_slider.setTickInterval(2)
        self.expression_slider.setEnabled(False)

        layout_left.addWidget(self.canvas)
        layout_left.addWidget(self.expression_slider)

        main_layout.addLayout(layout_left)
        self.setLayout(main_layout)

        self.axes.view_init(20, 60)
        self.load_data()
        self.load_pose()
        self.plot_3d()

    def expression_slider_change(self):
        self.pose_index = self.expression_slider.value()
        self.setWindowTitle('Dancing Turtle')
        self.load_pose()
        self.plot_3d()

    def load_data(self):

        points = []
        filename = 'mocap.dat'
        f = open(filename, 'rb')

        try:

            head, tail = os.path.split(str(filename))
            self.current_full_filename = str(filename)
            self.current_filename = tail

            with f:
                while 1:
                    input_stream = f.read(2)
                    if not input_stream:
                        f.close()
                        break
                    points.append(struct.unpack('<h', input_stream)[0])

        finally:
            f.close()

            points_x = []
            points_y = []
            points_z = []

            # CARLTON

            carl_translate = [640, 680]
            tmp = []
            for u in range(0, 23):
                tmp.append(points[3 * u + 2] - 20)

            for n in range(0, len(moves)):
                for k in range(0, 23):
                    points_x.append(-moves[n][3 * k] + carl_translate[0])
                    points_y.append(-(round((moves[n][3 * k + 1]))) + carl_translate[1])
                    if k < 12:
                        points_z.append(moves[n][3 * k + 2])
                    else:
                        points_z.append(tmp[k])

            # END CARLTON

            self.body_data = (copy.copy(points_x), copy.copy(points_y), copy.copy(points_z))
            self.body_data_copy = copy.deepcopy(self.body_data)

            self.expression_slider.setMinimum(0)
            self.expression_slider.setMaximum(int(len(self.body_data[0]) / 23) - 1)
            self.expression_slider.setValue(0)
            self.expression_slider.setEnabled(True)

    def load_pose(self):

        points_per_body = 23
        start = self.pose_index * points_per_body
        stop = start + points_per_body

        self.x_ = copy.copy(self.body_data[0][start:stop])
        self.y_ = copy.copy(self.body_data[1][start:stop])
        self.z_ = copy.copy(self.body_data[2][start:stop])

    def set_view(self):

        self.axes.clear()

        lim = 248

        self.axes.set_facecolor('#077abb')
        self.axes.grid(False)
        self.axes.set_xlim(-lim, lim)

        self.axes.xaxis.set_ticks(np.arange(-lim, lim + 1, lim / 4))
        self.axes.set_ylim(-lim, lim)
        self.axes.yaxis.set_ticks(np.arange(-lim, lim + 1, lim / 4))
        self.axes.set_zlim(0, 2 * lim)
        self.axes.zaxis.set_ticks(np.arange(0, 2 * lim + 1, lim / 4))

        self.axes.set_xticks([])
        self.axes.set_yticks([])
        self.axes.set_zticks([])

        self.axes.set_axis_off()

        self.axes.tick_params(axis='x', colors='black', labelsize=6)
        self.axes.tick_params(axis='z', colors='black', labelsize=6)
        self.axes.tick_params(axis='y', colors='black', labelsize=6)

        self.axes.set_xlabel('x', fontsize=6, color='black')
        self.axes.set_ylabel('z', fontsize=6, color='black')
        self.axes.set_zlabel('y', fontsize=6, color='black')

        self.axes.w_xaxis.set_pane_color((1, 1, 1, 0))
        self.axes.w_yaxis.set_pane_color((1, 1, 1, 0))
        self.axes.w_zaxis.set_pane_color((1, 1, 1, 0))

    def draw_feet(self, points_x, points_y, points_z):

        x_data = [points_x[0], points_x[1] - 20, points_x[1] + 20]
        y_data = [points_z[0], points_z[1], points_z[1]]
        z_data = [points_y[0], points_y[1], points_y[1]]
        vertices = [list(zip(x_data, y_data, z_data))]
        self.axes.add_collection3d(Poly3DCollection(vertices, facecolors='#c2dd38'))

    def draw_extremity(self, points_x, points_y, points_z):

        x_data = [points_x[0], points_x[1] - 20, points_x[1] + 20]
        y_data = [points_z[0], points_z[1], points_z[1]]
        z_data = [points_y[0], points_y[1], points_y[1]]
        vertices = [list(zip(x_data, y_data, z_data))]
        self.axes.add_collection3d(Poly3DCollection(vertices, facecolors='#c2dd38'))

        x_data = [points_x[1] + 20, points_x[1] - 20, points_x[2] - 20, points_x[2] + 20]
        y_data = [points_z[1], points_z[1], points_z[2], points_z[2]]
        z_data = [points_y[1], points_y[1], points_y[2], points_y[2]]
        vertices = [list(zip(x_data, y_data, z_data))]
        self.axes.add_collection3d(Poly3DCollection(vertices, facecolors='#c2dd38'))

    def draw_torso(self, points_x, points_y, points_z):

        x_data = [points_x[0], points_x[1], points_x[2], points_x[3]]
        y_data = [points_z[0], points_z[1], points_z[2], points_z[3]]
        z_data = [points_y[0], points_y[1], points_y[2], points_y[3]]
        vertices = [list(zip(x_data, y_data, z_data))]
        self.axes.add_collection3d(Poly3DCollection(vertices, facecolors='#c2dd38'))

        x_data = [points_x[0] + 10, points_x[1] - 10, points_x[2] - 10, points_x[3] + 10]
        y_data = [points_z[0] + 15, points_z[1] + 15, points_z[2] + 15, points_z[3] + 15]
        z_data = [points_y[0], points_y[1], points_y[2], points_y[3]]
        vertices = [list(zip(x_data, y_data, z_data))]
        self.axes.add_collection3d(Poly3DCollection(vertices, facecolors='#ffd662'))

    def plot_3d(self):

        self.set_view()

        X, Y = np.meshgrid(x, y)
        Z = np.ones(X.shape)

        self.axes.plot_surface(4*X + (self.x_[13] - 50)*np.ones(X.shape), + self.z_[13]*np.ones(Z.shape),
                               -4*Y + (self.y_[13] + 40)*np.ones(Y.shape), facecolors=img, rstride=1, cstride=1,
                               antialiased=True, shade=False)

        self.draw_feet((self.x_[0], self.x_[2]),
                       (self.y_[0], self.y_[2]),
                       (self.z_[0], self.z_[2]))

        self.draw_feet((self.x_[10], self.x_[8]),
                       (self.y_[10], self.y_[8]),
                       (self.z_[10], self.z_[8]))

        self.draw_extremity((self.x_[4], self.x_[3], self.x_[2]),
                            (self.y_[4], self.y_[3], self.y_[2]),
                            (self.z_[4], self.z_[3], self.z_[2]))

        self.draw_extremity((self.x_[6], self.x_[7], self.x_[8]),
                            (self.y_[6], self.y_[7], self.y_[8]),
                            (self.z_[6], self.z_[7], self.z_[8]))

        self.draw_torso((self.x_[4], self.x_[6], self.x_[14], self.x_[18]),
                        (self.y_[4], self.y_[6], self.y_[14], self.y_[18]),
                        (self.z_[4], self.z_[6], self.z_[14], self.z_[18]))

        self.draw_extremity((self.x_[18], self.x_[19], self.x_[20]),
                            (self.y_[18], self.y_[19], self.y_[20]),
                            (self.z_[18], self.z_[19], self.z_[20]))

        self.draw_extremity((self.x_[14], self.x_[15], self.x_[16]),
                            (self.y_[14], self.y_[15], self.y_[16]),
                            (self.z_[14], self.z_[15], self.z_[16]))

        self.canvas.draw_idle()

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
