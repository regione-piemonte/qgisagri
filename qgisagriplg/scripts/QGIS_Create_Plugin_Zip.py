# imports
import os
from os.path import basename #, dirname
import configparser
import zipfile
import glob

# constants
#QGIS_AGRI_DIR = "C:/Users/MRTSDR71E/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/qgis_agri/scripts"
QGIS_AGRI_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if os.path.basename( QGIS_AGRI_DIR ) != 'qgis_agri':
    raise Exception( f"Percorso del plugin invalido: {QGIS_AGRI_DIR}" )
    
#
#-----------------------------------------------------------
class QgisPluginPacker:
    """Utility class to create a QGIS plugin archive"""
    
    def __init__(self):
        """Constructor"""
        self._exclude_dirs = set([
            '.git', 
            '__pycache__',
            r'qgis_agri\buildfiles',
            r'qgis_agri\scripts',
            r'qgis_agri\help\qgis_agri_venv',
            r'qgis_agri\conf\PROD',
            r'qgis_agri\conf\TEST',
            r'qgis_agri\styles\old',
            r'qgis_agri\data\old',
            r'qgis_agri\env\venv',
            r'qgis_agri\env\qgis_agri_ext_browser'
        ])
        
        self._exclude_files = set([
            r'qgis_agri\.gitignore',
            r'qgis_agri\build.xml',
            r'qgis_agri\conf\config_test.yaml',
            r'qgis_agri\conf\config_test_col.yaml',
            r'qgis_agri\conf\config_test_pa_ref.yaml',
            r'qgis_agri\conf\config_up_019.yaml',
            r'qgis_agri\conf\config_ut_o19.yaml',
            r'qgis_agri\conf\profiles.yaml'
        ])
        
        self._replace_files = {
            r'qgis_agri\conf\profiles.yaml': r'qgis_agri\conf\PROD\profiles.yaml'
        }
        

    def get_metadata(self, plgDirName):
        """Return plugin metadata"""
        filePath = os.path.join(plgDirName, 'metadata.txt')

        metadata = configparser.ConfigParser()
        with open(filePath) as f:
            metadata.read_file(f)
            
        result = {}
        result['name'] = metadata.get('general', 'name')
        result['version'] = metadata.get('general', 'version')
        result['description'] = metadata.get('general', 'description')
        result['homepage'] = metadata.get('general', 'homepage')
        result['qgis_minimum_version'] = metadata.get('general', 'qgisMinimumVersion')
        result['author'] = metadata.get('general', 'author').replace('&', '&amp;')
        
        return result


    def pack(self, plgFolder, destFolder, plgName=None):
        """Create plugin archive"""
        # init
        plgPath = os.path.join( plgFolder, '..' )
        empty_dirs = []
        
        # check if present SQLITE temp DB
        dataPath = os.path.join( plgFolder, "data" )
        numDbFiles = len( glob.glob( f"{dataPath}/*.sqlite" ) )
        if numDbFiles == 0:
            print( "ERRORE: nessun DB SQLITE reperito!!!!!!" )
            return False
        elif numDbFiles > 1:
            print( "ERRORE: presenti piu DB SQLITE, probabilmente una lavorazione non è stata completata!!!!!!" )
            return False
        
        # get plugin metadata
        plg_metadata = self.get_metadata( plgFolder )
        plg_name = plgName if plgName else plg_metadata.get( 'name' )
        plg_version = plg_metadata.get( 'version' )
        
        # compose zip file name
        zipfilePath = os.path.join(
            destFolder, 
            "{}.{}.zip".format( plg_name, plg_version ))
        
        ##print(zipfilePath)
        ##print(plg_metadata)
        
        # create a ZipFile object
        with zipfile.ZipFile(zipfilePath, 'w', zipfile.ZIP_DEFLATED) as zipObj:
            # loop plugin folder
            for folderName, subfolders, filenames in os.walk(plgFolder, topdown=True):
                # exclude folder
                folderRelName = os.path.relpath( folderName, plgPath )
                if folderRelName in self._exclude_dirs:
                    subfolders[:] = []
                    continue
                    
                # exclude sub folder    
                subfolders[:] = [d for d in subfolders if d not in self._exclude_dirs]
                
                print(folderRelName)
                
                # write files
                n_file = 0
                for filename in filenames:
                    # count files
                    n_file += 1
                    
                    #create complete filepath of file in directory
                    filePath = os.path.join( folderName, filename )
                    fileRelPath = os.path.relpath( filePath, plgPath )
                    
                    # exclude file
                    if fileRelPath in self._exclude_files:
                        continue
                    ###print(fileRelPath)
                    
                    # add file to zip
                    zipObj.write( filePath, fileRelPath )
                    
                # write folder
                if not n_file:
                    zfi = zipfile.ZipInfo( folderRelName + "\\" )
                    zfi.external_attr = 16
                    zipObj.writestr( zfi, '' )
                    
            # add replaced files
            for fileToPath, fileFromPath in self._replace_files.items():
                # add file to zip
                fileFromFullPath = os.path.join( plgPath, fileFromPath )
                zipObj.write( fileFromFullPath, fileToPath )
                print( "==> Sostituito file '{}' con '{}'".format( fileToPath, fileFromPath ) )
                
        # exit successfully
        print( "Creato archivio: {}".format( zipfilePath ) )
        return True
    
    def pack_files(self, 
                   plgFolder: str, 
                   destFolder: str, 
                   fileRelNames: list, 
                   plgName: str=None, 
                   postFixName:str ='extra') -> bool :
        """Create plugin archive"""
        # init
        plgPath = os.path.join( plgFolder, '..' )
        empty_dirs = []
        
        # get plugin metadata
        plg_metadata = self.get_metadata( plgFolder )
        plg_name = plgName if plgName else plg_metadata.get( 'name' )
        plg_version = plg_metadata.get( 'version' )
        
        # compose zip file name
        zipfilePath = os.path.join(
            destFolder, 
            "{}.{}___{}.zip".format( plg_name, plg_version, postFixName ))
        
        # create a ZipFile object
        with zipfile.ZipFile( zipfilePath, 'w', zipfile.ZIP_DEFLATED ) as zipObj:
            # write files
            for fileRelPath in fileRelNames:
                # add file to zip
                filePath = os.path.join( plgFolder, fileRelPath )
                zipObj.write( filePath, basename(fileRelPath) )
                print( fileRelPath )
                
        # exit successfully
        print( "Creato archivio: {}".format( zipfilePath ) )
        return True
 
######################################################################## 
plg_packer = QgisPluginPacker()

print( os.linesep.join([
    "------------------------------",
    "  CREA ARCHIVIO PLUGIN QGIS   ",
    "------------------------------",
]))

res = plg_packer.pack( QGIS_AGRI_DIR, 'D:/', plgName='qgis_agri' )
print( "Risultato: {}".format(res))

if res:
    print( os.linesep.join([
        "--------------------------------------------",
        "  CREA ARCHIVIO CONFIGURAZIONE PLUGIN QGIS  ",
        "--------------------------------------------",
    ]))
    res = plg_packer.pack_files(
            QGIS_AGRI_DIR, 
            'D:/',
            [
                r'conf\config_test.yaml',
                r'conf\config_test_col.yaml',
                r'conf\config_test_pa_ref.yaml',
                r'conf\config_up_019.yaml',
                r'conf\config_ut_o19.yaml',
                r'conf\profiles.yaml'
            ],
            plgName='qgis_agri',
            postFixName='config_test'
            )
            
    print( "Risultato: {}".format(res))
