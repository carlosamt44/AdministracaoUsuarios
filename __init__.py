# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AdministracaoUsuarios
                                 A QGIS plugin
 Esse plugin oferece um formulário para cadastro e atualização de usuários.
                             -------------------
        begin                : 2018-06-26
        copyright            : (C) 2018 by Carlos Maia
        email                : carlos.teixeira@terracap.df.gov.br
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load AdministracaoUsuarios class from file AdministracaoUsuarios.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .administracao_usuarios import AdministracaoUsuarios
    return AdministracaoUsuarios(iface)
