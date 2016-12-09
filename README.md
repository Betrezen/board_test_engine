# board_test_engine
do HW board testing in realtime which available through UART/COM protocol

That is small project which dedicated to board testing
which available through UART / COM

--convert ui to py
pyside-uic -o qt_client/qtmain.py images/qtmain_3.ui

--run web app
cd www
python app.py

--run qt client
cd qt_client/
python qtclient.py
