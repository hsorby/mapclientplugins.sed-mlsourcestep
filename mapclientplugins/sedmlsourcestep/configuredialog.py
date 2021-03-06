
import os.path

from PySide import QtGui
from mapclientplugins.sedmlsourcestep.ui_configuredialog import Ui_ConfigureDialog

INVALID_STYLE_SHEET = 'background-color: rgba(239, 0, 0, 50)'
DEFAULT_STYLE_SHEET = ''

class ConfigureDialog(QtGui.QDialog):
    '''
    Configure dialog to present the user with the options to configure this step.
    '''

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        QtGui.QDialog.__init__(self, parent)
        
        self._ui = Ui_ConfigureDialog()
        self._ui.setupUi(self)

        self._workflow_location = None

        # Keep track of the previous identifier so that we can track changes
        # and know how many occurrences of the current identifier there should
        # be.
        self._previousIdentifier = ''
        # Set a place holder for a callable that will get set from the step.
        # We will use this method to decide whether the identifier is unique.
        self.identifierOccursCount = None
        
        self._previousLocation = ''

        self._makeConnections()

    def _makeConnections(self):
        self._ui.lineEditIdentifier.textChanged.connect(self.validate)
        self._ui.lineEditLocation.textChanged.connect(self.validate)
        self._ui.pushButtonLocation.clicked.connect(self._locationButtonClicked)

    def setWorkflowLocation(self, location):
        self._workflow_location = location

    def accept(self):
        '''
        Override the accept method so that we can confirm saving an
        invalid configuration.
        '''
        result = QtGui.QMessageBox.Yes
        if not self.validate():
            result = QtGui.QMessageBox.warning(self, 'Invalid Configuration',
                'This configuration is invalid.  Unpredictable behaviour may result if you choose \'Yes\', are you sure you want to save this configuration?)',
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if result == QtGui.QMessageBox.Yes:
            QtGui.QDialog.accept(self)

    def validate(self):
        '''
        Validate the configuration dialog fields.  For any field that is not valid
        set the style sheet to the INVALID_STYLE_SHEET.  Return the outcome of the 
        overall validity of the configuration.
        '''
        # Determine if the current identifier is unique throughout the workflow
        # The identifierOccursCount method is part of the interface to the workflow framework.
        value = self.identifierOccursCount(self._ui.lineEditIdentifier.text())
        valid_identifier = (value == 0) or (value == 1 and self._previousIdentifier == self._ui.lineEditIdentifier.text())
        if valid_identifier:
            self._ui.lineEditIdentifier.setStyleSheet(DEFAULT_STYLE_SHEET)
        else:
            self._ui.lineEditIdentifier.setStyleSheet(INVALID_STYLE_SHEET)

        valid_location = os.path.isdir(os.path.join(self._workflow_location, self._ui.lineEditLocation.text()))
        if valid_location:
            self._ui.lineEditLocation.setStyleSheet(DEFAULT_STYLE_SHEET)
        else:
            self._ui.lineEditLocation.setStyleSheet(INVALID_STYLE_SHEET)

        return valid_identifier and valid_location

    def getConfig(self):
        '''
        Get the current value of the configuration from the dialog.  Also
        set the _previousIdentifier value so that we can check uniqueness of the
        identifier over the whole of the workflow.
        '''
        self._previousIdentifier = self._ui.lineEditIdentifier.text()
        self._previousLocation = self._ui.lineEditLocation.text()
        config = {}
        config['identifier'] = self._ui.lineEditIdentifier.text()
        config['Location'] = self._ui.lineEditLocation.text()
        return config

    def setConfig(self, config):
        '''
        Set the current value of the configuration for the dialog.  Also
        set the _previousIdentifier value so that we can check uniqueness of the
        identifier over the whole of the workflow.
        '''
        self._previousIdentifier = config['identifier']
        self._previousLocation = config['Location']
        self._ui.lineEditIdentifier.setText(config['identifier'])
        self._ui.lineEditLocation.setText(config['Location'])

    def _locationButtonClicked(self):
        location = QtGui.QFileDialog.getExistingDirectory(self, 'Select Location', self._previousLocation)
        if location:
            self._previousLocation = location
            self._ui.lineEditLocation.setText(os.path.relpath(location, self._workflow_location))

