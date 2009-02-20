#! /usr/bin/env python3

"""
basegraph.py

Written by Geremy Condra

Licensed under the GNU GPLv3

Released 15 Feb 2009

This module contains Graphine's base hypergraph represenatation.
"""

# Copyright (C) 2009 Geremy Condra and OpenMigration, LLC
#
# This file is part of Graphine.
# 
# Graphine is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Graphine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Graphine.  If not, see <http://www.gnu.org/licenses/>.

class InitializationError(Exception): pass

class DeletionError(Exception): pass

class OperationError(Exception): pass

class ContainerInitializationError(InitializationError): pass

class ContainerDeletionError(DeletionError): pass

class ContainerOperationError(OperationError): pass

class GraphInitializationError(InitializationError): pass

class GraphDeletionError(DeletionError): pass

class GraphOperationError(OperationError): pass

class NodeInitializationError(InitializationError): pass

class NodeDeletionError(DeletionError): pass

class NodeOperationError(OperationError): pass

class EdgeInitializationError(InitializationError): pass

class EdgeDeletionError(DeletionError): pass

class EdgeOperationError(OperationError): pass

