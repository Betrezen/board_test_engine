"""
-----------------------------------------
Draw lines and text on board image module
-----------------------------------------
"""
from PySide import QtCore
from PySide import QtGui


class Draw(object):
    """Draw class"""

    pen_width = 15
    font = QtGui.QFont('Arial', 40)

    points_info = {
        'J4_1': {'coords': [1240, 408],
                 'lineTo': [('x + 287', 'y')],
                 'text_c': ['x + 297', 'y - 15'],
                 'label': 'J4-1=FTDI',
                 'color': QtGui.QColor.fromRgb(255, 201, 14)},

        'J4_2': {'coords': [1240, 465],
                 'lineTo': [('x + 287', 'y')],
                 'text_c': ['x + 297', 'y - 25'],
                 'label': 'J4-2=GND=FTDI',
                 'color': QtCore.Qt.black},

        'J4_3': {'coords': [1240, 515],
                 'lineTo': [('x + 287', 'y')],
                 'text_c': ['x + 297', 'y - 25'],
                 'label': 'J4-3=FTDI',
                 'color': QtGui.QColor.fromRgb(255, 127, 39)},

        'J5_1': {'coords': [1310, 310],
                 'lineTo': [('x + 217', 'y')],
                 'text_c': ['x + 227', 'y - 40'],
                 'label': 'J5-1=VPSU',
                 'color': QtCore.Qt.red},

        'J5_2': {'coords': [1310, 255],
                 'lineTo': [('x + 217', 'y')],
                 'text_c': ['x + 227', 'y - 35'],
                 'label': 'J5-2=VPSU',
                 'color': QtCore.Qt.red},

        'J5_3': {'coords': [1257, 315],
                 'lineTo': [('x + 25', 'y + 35'),
                            ('x + 270', 'y + 35')],
                 'text_c': ['x + 280', 'y'],
                 'label': 'J5-3=GND',
                 'color': QtCore.Qt.black},

        'J5_4': {'coords': [1257, 255],
                 'lineTo': [('x + 50', 'y - 50'),
                            ('x + 270', 'y - 50')],
                 'text_c': ['x + 280', 'y - 85'],
                 'label': 'J5-4=GND',
                 'color': QtCore.Qt.black},

        'J6_5': {'coords': [1257, 203],
                 'lineTo': [('x', 'y - 150'),
                            ('x + 270', 'y - 150')],
                 'text_c': ['x + 280', 'y - 175'],
                 'label': 'J6-5=GPIO0',
                 'color': QtGui.QColor.fromRgb(163, 73, 176)},

        'TP2': {'coords': [1203, 363],
                'lineTo': [('x + 13', 'y + 13'),
                           ('x + 325', 'y + 13')],
                'text_c': ['x + 335', 'y - 8'],
                'label': 'TP2=ADC1',
                'color': QtGui.QColor.fromRgb(163, 73, 176)},

        'TP3': {'coords': [1165, 715],
                'lineTo': [('x', 'y + 470'),
                           ('x + 133', 'y + 470')],
                'text_c': ['x + 143', 'y + 445'],
                'label': 'TP3=ADC2',
                'color': QtGui.QColor.fromRgb(0, 162, 232)},

        'TP6': {'coords': [1188, 765],
                'lineTo': [('x', 'y + 370'),
                           ('x + 108', 'y + 370')],
                'text_c': ['x + 118', 'y + 345'],
                'label': 'TP6=ADC5',
                'color': QtGui.QColor.fromRgb(185, 122, 87)},

        'TP7': {'coords': [1405, 725],
                'lineTo': [('x', 'y + 370'),
                           ('x + 123', 'y + 370')],
                'text_c': ['x + 133', 'y + 345'],
                'label': 'TP7=ADC6',
                'color': QtGui.QColor.fromRgb(255, 174, 201)},
    }

    def draw_point_and_line(self, scene, point_name, actual_value=None):
        """Draw lines and text on board image

        :param scene: PySide.QtGui.QGraphicsScene object
        :param point_name: (str) Name on the point
        :param actual_value: (str/int) Actual value from test engine
        :return: None
        """
        point = self.points_info.get(point_name)
        x, y = point['coords']
        label = point['label']
        label = '{0}: {1}'.format(label, actual_value)
        line_to = point['lineTo']
        line_to = [(eval(a), eval(b)) for a, b in line_to]
        text_pos = point['text_c']
        text_pos_x, text_pos_y = [eval(a) for a in text_pos]
        color = point['color']

        multiline = QtGui.QPainterPath()
        multiline.moveTo(x, y)

        for line_point in line_to:
            _x, _y = line_point
            multiline.lineTo(_x, _y)

        item = QtGui.QGraphicsPathItem(multiline)
        item.setPen(QtGui.QPen(
            color,
            self.pen_width,
            QtCore.Qt.SolidLine,
            QtCore.Qt.RoundCap,
            QtCore.Qt.MiterJoin))
        scene.addItem(item)
        text = scene.addText(label)
        text.setPos(text_pos_x, text_pos_y)
        text.setDefaultTextColor(color)
        text.setFont(self.font)
