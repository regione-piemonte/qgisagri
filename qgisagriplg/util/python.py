# -*- coding: utf-8 -*-
"""pyUtilclass

Description
-----------

Utility class to operate with Python processes.

Libraries/Modules
-----------------

- None.
    
Notes
-----

- None.

TODO
----

- None.

Author(s)
---------

- Created by Sandro Moretti on 12/06/2022.

Copyright (c) 2019 CSI Piemonte.

Members
-------
"""
import os
import shutil
import subprocess
from PyQt5.QtCore import QCoreApplication
    
# 
#-----------------------------------------------------------
class PyUtilWarning(Exception):
    """Base class for other exceptions"""

# 
#-----------------------------------------------------------
class pyUtil:
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def _tr(message):
        return QCoreApplication.translate('pyUtil', message)
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def getPlatformPythonExe(for_venv=False):
        if os.name == 'nt':
            if not for_venv:
                return shutil.which("python")
            python_name = "python.exe"
            python_dir = "Scripts/" if for_venv else ''
        else:
            if not for_venv:
                return shutil.which("python3")
            python_name = "python3"
            python_dir = "bin/" if for_venv else ''
        
        return f"{python_dir}{python_name}"
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def createVenv(venv_path: str, module_lst: list, arch_file='') -> bool:
        """Utility method to create a new Python virtual environment.
        
        :param venv_path: directory in which to create the virtual environment.
        :type venv_path: str
        
        :param module_lst: list of module(names) to install.
        :type module_lst: list
        """
        
        # init
        venv_path = os.path.normpath(str(venv_path))
        python_venv_bin = os.path.normpath(os.path.join(venv_path, pyUtil.getPlatformPythonExe(for_venv=True)))
        batch_path = os.path.normpath(os.path.join(os.path.dirname(python_venv_bin), "activate.bat"))
        
        module_lst = module_lst or []
        
        
        # check if folder exists
        if os.path.isdir(venv_path):
            raise PyUtilWarning(f"{pyUtil._tr('Ambiente virtuale Python già presente')}")
        
        
        if arch_file:
            # uncompress virtual environment 
            import zipfile
            arch_file = os.path.normpath(str(arch_file))
            arch_path = os.path.dirname(arch_file)
            with zipfile.ZipFile(arch_file, 'r') as zip_ref:
                zip_ref.extractall(arch_path)
        """
        else:
            # crete virtual environment (VENV module)
            sys_env = os.environ.copy()
            
            # get Python executable
            python_bin = os.path.join(os.path.os.path.dirname(os.path.os.path.dirname(os.__file__)), "python.exe")
            if not python_bin:
                raise FileNotFoundError(pyUtil._tr("Eseguibile Python non reperito"))
            
            # create Python virtual environment
            # pylint: disable=W1510
            cp = subprocess.run([python_bin, "-m", "venv", venv_path], 
                                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=sys_env)
            #if cp.returncode:
            #    raise RuntimeError(str(cp.stderr))
        """   
        
        # install Python modules
        for module_name in module_lst:
            # pylint: disable=W1510
            cp = subprocess.run([batch_path, "&", "python", "-m", "pip", "install", module_name], 
                                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) #, env=sys_env)
            if cp.returncode:
                raise RuntimeError(str(cp.stderr)) 
        
        return True
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def runExecutable(exe_file: str,
                      exe_args: list=None, 
                      check_result: bool=True) -> bool:
        
        # init
        exe_file = os.path.normpath(str(exe_file))
        exe_path = os.path.dirname(exe_file)
        exe_args = exe_args or []
        cmd_lst = [exe_file] + exe_args
        
        
        if check_result:
            # run process with check
            # pylint: disable=W1510
            cp = subprocess.run(cmd_lst, shell=True, 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, 
                                cwd=exe_path)
            if cp.returncode:
                raise RuntimeError(str(cp.stderr))
        
        else:
            # run process
            #subprocess.run([python_bin, script_file] + script_args, shell=True)
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            p = subprocess.Popen(cmd_lst, startupinfo=si, cwd=exe_path)
            p.returncode = -1
        
        return True
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def runScript(script_file: str, 
                  script_args: list=None, 
                  python_bin: str=None,
                  for_venv: bool=False, 
                  check_result: bool=True) -> bool:
        """Utility method to run a Python script
        
        :param script_file: file path of the script that must be launch.
        :type script_file: str
        
        :param script_args: list of script arguments (optional).
        :type script_args: list
        
        :param python_bin: path of the Python executable binary to use (optional).
        :type python_bin: str
        """
        
        
        # init
        script_file = os.path.normpath(str(script_file))
        
        if not python_bin:
            python_bin = pyUtil.getPlatformPythonExe()
        python_bin = os.path.normpath(str(python_bin))
        python_path = os.path.dirname(python_bin)
        
        script_args = script_args or []
        
        # check if Python executable exists
        if not os.path.isfile(python_bin):
            raise FileNotFoundError(pyUtil._tr("Eseguibile Python non reperito"))
            
        # check if Python script exists
        if not os.path.isfile(script_file):
            raise FileNotFoundError(f"{pyUtil._tr('Eseguibile Python non reperito')}: \n {script_file}")
 
        # run Python script
        if check_result:
            # pylint: disable=W1510
            cp = subprocess.run([python_bin, script_file] + script_args, 
                                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if cp.returncode:
                raise RuntimeError(str(cp.stderr))
        
        else:
            if os.name == 'nt':
                # prepare command list
                cmd_lst = []
                if for_venv:
                    batch_path = os.path.normpath(os.path.join(os.path.dirname(python_bin), "activate.bat"))
                    cmd_lst.append(batch_path)
                    cmd_lst.append("&")
                cmd_lst.append("python")
                
                # append command arguments
                cmd_lst.append(script_file)
                cmd_lst = cmd_lst + script_args
                
                # run process
                #subprocess.run([python_bin, script_file] + script_args, shell=True)
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                p = subprocess.Popen(cmd_lst, startupinfo=si, cwd=python_path)
                p.returncode = -1
                
            else:
                cp = subprocess.run([python_bin, script_file] + script_args)
        
        return True
        
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def installPythonPackage(pkg_name: str) -> bool:
        """Utility method to install a Python Package"""
        
        # check if already installed
        try:
            __import__(pkg_name)
            return True
        except ImportError:
            pass
        
        # Try to install package
        subprocess.check_call([shutil.which('python'), "-m", "pip", "install", pkg_name])
        return True
    