# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AdministracaoUsuarios
                                 A QGIS plugin
 Esse plugin oferece um formulário para cadastro e atualização de usuários.
                              -------------------
        begin                : 2018-06-26
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Carlos Maia
        email                : carlos.teixeira@terracap.df.gov.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys

# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from administracao_usuarios_dialog import AdministracaoUsuariosDialog
import os.path
import getpass
import psycopg2
import uuid
import hashlib

id = 0
nome = ""
senha = ""
NovoUsuario = False
username = ""

class AdministracaoUsuarios:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'AdministracaoUsuarios_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = AdministracaoUsuariosDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Administração de Usuários')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'AdministracaoUsuarios')
        self.toolbar.setObjectName(u'AdministracaoUsuarios')

        self.dlg.checkBox.clicked.connect(self.click_check)
        self.dlg.pushButton_save.clicked.connect(self.click_save)
        self.dlg.lineEdit_3.textChanged.connect(self.NaoConf_Hide)
        self.dlg.lineEdit_4.textChanged.connect(self.NaoConf_Hide)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('AdministracaoUsuarios', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        #self.dlg = AdministracaoUsuariosDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToDatabaseMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")
        self.add_action(
            icon_path,
            text=self.tr(u'Administração de Usuários'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginDatabaseMenu(
                self.tr(u'&Administração de Usuários'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def click_check(self):

        if self.dlg.checkBox.isChecked():
            self.dlg.lineEdit.setEnabled(True)
            self.dlg.lineEdit_3.setEnabled(True)
            self.dlg.lineEdit_3.setFocus(True)
            self.dlg.label_4.show()
            self.dlg.label_4.setText("Nova Senha:")
            self.dlg.label_4.move(30,107)
            self.dlg.lineEdit_4.show()
            self.dlg.label_6.show()
            self.dlg.lineEdit_5.show()
            self.dlg.pushButton_save.setEnabled(True)
        else:
            self.dlg.lineEdit.setEnabled(False)
            self.dlg.lineEdit_3.setEnabled(False)
            self.dlg.label_4.hide()
            self.dlg.label_4.setText("Confirmar Senha:")
            self.dlg.label_4.move(8,107)
            self.dlg.lineEdit_4.hide()
            self.dlg.lineEdit_3.clear()
            self.dlg.lineEdit_4.clear()
            self.dlg.label_6.hide()
            self.dlg.lineEdit_5.clear()
            self.dlg.lineEdit_5.hide()
            self.dlg.pushButton_save.setEnabled(False)


    def click_save(self):
        global id
        global NovoUsuario
        global username

        NomeTexto = self.dlg.lineEdit.text().upper()
        SenhaDigitada = self.dlg.lineEdit_3.text()
        NovaSenha = ""

        if NovoUsuario:
            ConfirmarSenha = self.dlg.lineEdit_4.text()
        else:
            NovaSenha = self.dlg.lineEdit_4.text()
            ConfirmarSenha = self.dlg.lineEdit_5.text()

        if NomeTexto == "":
            QMessageBox.warning(None, self.tr(u'Atenção!'), u'O campo Nome precisa estar preenchido.')
        elif SenhaDigitada == "":
            QMessageBox.warning(None, self.tr(u'Atenção!'), u'O campo Senha precisa estar preenchido.')
        elif NovaSenha == "" and NovoUsuario == False:
            QMessageBox.warning(None, self.tr(u'Atenção!'), u'O campo Nova Senha precisa estar preenchido.')
        elif ConfirmarSenha == "":
            QMessageBox.warning(None, self.tr(u'Atenção!'), u'O campo Confirmar Senha precisa estar preenchido.')
        elif SenhaDigitada != ConfirmarSenha and NovoUsuario:
            self.dlg.label_5.move(230,107)
            self.dlg.label_5.show()
        elif NovaSenha != ConfirmarSenha and NovoUsuario == False:
            self.dlg.label_5.move(230,134)
            self.dlg.label_5.show()
        else:
            self.dlg.lineEdit.setEnabled(False)
            self.dlg.checkBox.setChecked(False)
            self.dlg.lineEdit_3.clear()
            self.dlg.lineEdit_3.setEnabled(False)
            self.dlg.lineEdit_4.clear()
            self.dlg.lineEdit_4.hide()
            self.dlg.label_4.hide()
            self.dlg.lineEdit_5.clear()
            self.dlg.lineEdit_5.hide()
            self.dlg.label_6.hide()
            hashed_password = self.hash_password(SenhaDigitada)
            if self.existeMat(username):
                global senha
                if self.check_password(senha, SenhaDigitada):
                    hashed_NovaSenha = self.hash_password(NovaSenha)
                    if self.UpdateUsuario(NomeTexto, NovaSenha, hashed_NovaSenha, SenhaDigitada, username):
                        QMessageBox.information(None, self.tr(u'Informação!'), u'Dados salvos com êxito.')
                        self.dlg.lineEdit.setText(NomeTexto)
                    else:
                        QMessageBox.warning(None, self.tr(u'Erro!'), u'Dados não atualizados.')
                else:
                    QMessageBox.warning(None, self.tr(u'Erro!'), u'Senha não confere com o Banco de Dados.')
            else:
                if self.InsertResTec(id, NomeTexto, SenhaDigitada, hashed_password, username):
                    QMessageBox.information(None, self.tr(u'Informação!'), u'Dados salvos com êxito.')
                    self.dlg.lineEdit.setText(NomeTexto)
                    self.dlg.checkBox.show()
                    NovoUsuario = False
                else:
                    QMessageBox.warning(None, self.tr(u'Erro!'), u'Dados não inseridos.')
                    self.dlg.lineEdit.setEnabled(True)
                    self.dlg.lineEdit_3.setEnabled(True)
                    self.dlg.lineEdit_3.clear()
                    self.dlg.label_4.show()
                    self.dlg.lineEdit_4.show()
                    self.dlg.lineEdit_4.clear()
                    self.dlg.pushButton_save.setEnabled(True)
                    NovoUsuario = True


    def UpdateUsuario(self, nome, NovaSenha, hashed_NovaSenha, SenhaDigitada, matricula):
        #sql = """UPDATE responsavel_tecnico SET nome = %s, senha = %s WHERE matricula = %s"""
        sql = """UPDATE usuarios SET nome = %s, senha = %s WHERE matricula = %s"""

        try:
            #conn = psycopg2.connect("dbname='db_nirf_7' user='" + matricula + "' host='10.50.5.106' password='" + SenhaDigitada + "'")
            conn = psycopg2.connect("dbname='controle_usuarios' user='" + matricula + "' host='10.50.5.106' password='" + SenhaDigitada + "'")
            cur = conn.cursor()
            cur.execute(sql, (nome, NovaSenha, matricula))
            conn.commit()
            cur.close ()

            if self.UpdateResTec(nome, matricula, hashed_NovaSenha, NovaSenha):
                executado = True
            else:
                executado = False
        except:
            executado = False
        return executado


    def InsertResTec(self, id, nome, SenhaDigitada, SenhaHashed, matricula):
        #sql = "INSERT INTO responsavel_tecnico (nome, matricula, senha) VALUES ('" + nome + "', '" + matricula + "', '" + SenhaDigitada + "');"
        sql = "INSERT INTO usuarios (nome, matricula, senha) VALUES ('" + nome + "', '" + matricula + "', '" + SenhaDigitada + "');"

        try:

            #conn = psycopg2.connect("dbname='db_nirf_7' user='iniciante' host='10.50.5.106' password='1A9c1E0s2S0o115'")
            conn = psycopg2.connect("dbname='controle_usuarios' user='iniciante' host='10.50.5.106' password='1A9c1E0s2S0o115'")
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()
            cur.close ()

            if self.UpdateResTec(nome, matricula, SenhaHashed, SenhaDigitada):
                executado = True
            else:
                executado = False

        except:
            executado = False
        return executado


    def UpdateResTec(self, nome, matricula, SenhaHashed, SenhaDigitada):
        #sql = """UPDATE responsavel_tecnico SET nome = %s, senha = %s WHERE matricula = %s"""
        sql = """UPDATE usuarios SET nome = %s, senha = %s WHERE matricula = %s"""

        try:
            #conn = psycopg2.connect("dbname='db_nirf_7' user='" + matricula + "' host='10.50.5.106' password='" + SenhaDigitada + "'")
            conn = psycopg2.connect("dbname='controle_usuarios' user='" + matricula + "' host='10.50.5.106' password='" + SenhaDigitada + "'")
            cur = conn.cursor()
            cur.execute(sql, (nome, SenhaHashed, matricula))
            conn.commit()
            cur.close ()

            executado = True
        except:
            executado = False
        return executado


    def existeMat(self, matricula):
        global id
        global nome
        global senha

        existe = False

        try:
            #conn = psycopg2.connect("dbname='db_nirf_7' user='testador' host='10.50.5.106' password='0t1e0s7t2a0d1o5r'")
            conn = psycopg2.connect("dbname='controle_usuarios' user='testador' host='10.50.5.106' password='0t1e0s7t2a0d1o5r'")
            cur = conn.cursor()
            #cur.execute("""SELECT * FROM responsavel_tecnico""")
            cur.execute("""SELECT * FROM usuarios""")
            rows = cur.fetchall()
            for row in rows:
                if matricula == row[2]:
                    id = row[0]
                    if not (row[1] is None):
                        nome = row[1]
                    else:
                        nome = ""
                    if not (row[3] is None):
                        senha = row[3]
                    else:
                        senha = ""
                    existe = True
        except:
            QMessageBox.warning(None, self.tr(u'Atenção!'), u'Não foi possível conectar o Banco de Dados.')


        return existe


    def hash_password(self, password):
        # uuid is used to generate a random number
        #salt = uuid.uuid4().hex
        salt = "C1@7r0l7o1s9M@i@85"
        return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt


    def check_password(self, hashed_password, user_password):
        password, salt = hashed_password.split(':')
        return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()


    def NaoConf_Hide(self):
        self.dlg.label_5.hide()


    def run(self):
        """Run method that performs all the real work"""
        global nome
        global senha
        global NovoUsuario
        global username

        self.dlg.label_5.hide()
        self.dlg.lineEdit.setEnabled(False)
        self.dlg.lineEdit.clear()
        username = getpass.getuser()
        self.dlg.lineEdit_3.setEnabled(False)
        self.dlg.lineEdit_2.setText(username)
        self.dlg.lineEdit_3.clear()
        self.dlg.lineEdit_4.clear()
        self.dlg.label_6.hide()
        self.dlg.lineEdit_5.clear()
        self.dlg.lineEdit_5.hide()
        self.dlg.pushButton_save.setEnabled(False)

        if self.existeMat(username):
            self.dlg.lineEdit.setText(nome)
            self.dlg.label_4.hide()
            self.dlg.lineEdit_4.hide()
            self.dlg.checkBox.show()
            self.dlg.checkBox.setChecked(False)
            NovoUsuario = False

        else:
            self.dlg.checkBox.hide()
            self.dlg.lineEdit.setEnabled(True)
            self.dlg.lineEdit.clear()
            self.dlg.lineEdit_3.setEnabled(True)
            self.dlg.lineEdit_3.clear()
            self.dlg.label_4.show()
            self.dlg.lineEdit_4.show()
            self.dlg.lineEdit_4.clear()
            self.dlg.pushButton_save.setEnabled(True)
            NovoUsuario = True

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
