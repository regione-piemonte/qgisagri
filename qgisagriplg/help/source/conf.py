# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import datetime
#sys.path.insert(0, os.path.abspath('../..'))

sys.path.insert(0, "C:/Program Files/QGIS 3.4/apps/Python37/python37.zip")
sys.path.insert(0, "C:/Program Files/QGIS 3.4/apps/Python37/DLLs")
sys.path.insert(0, "C:/Program Files/QGIS 3.4/apps/Python37/lib")
sys.path.insert(0, "C:/Program Files/QGIS 3.4/apps/Python37")
###############C:/Users/MRTSDR71E/AppData/Roaming/Python/Python37/site-packages
sys.path.insert(0, "C:/Program Files/QGIS 3.4/apps/Python37/lib/site-packages")
sys.path.insert(0, "C:/Program Files/QGIS 3.4/apps/Python37/lib/site-packages/win32")
sys.path.insert(0, "C:/Program Files/QGIS 3.4/apps/Python37/lib/site-packages/win32/lib")
sys.path.insert(0, "C:/Program Files/QGIS 3.4/apps/Python37/lib/site-packages/Pythonwin")

sys.path.insert(0, 'C:/Program Files/QGIS 3.4/apps/qgis-ltr/python/')

sys.path.insert(0, os.path.abspath('../../../')+'/')
#sys.path.insert(0, os.path.join(os.path.abspath('../../../'),'qgis_agri'))
sys.setrecursionlimit(1500)


# -- Project information -----------------------------------------------------

_today = datetime.datetime.today()
project = 'QGIS Agri'
copyright = f'{_today.year}, CSI Piemonte'
author = 'Sandro Moretti'

# The short X.Y version.
version = '0.2'

# The full version, including alpha/beta/rc tags
release = '0.2'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',  # include documentation from docstrings
    'sphinx.ext.doctest',  # >>> examples
    'sphinx.ext.extlinks',  # for :pr:, :issue:, :commit:
    'sphinx.ext.autosectionlabel',  # use :ref:`Heading` for any heading
    'sphinx.ext.todo',  # Todo headers and todo:: directives
    'sphinx.ext.mathjax',  # LaTeX style math
    'sphinx.ext.viewcode',  # view code links
    'sphinx.ext.napoleon',  # for NumPy style docstrings
    'sphinx.ext.intersphinx',  # external links
    'sphinx.ext.autosummary',  # autosummary directive
    'rinoh.frontend.sphinx',
    #'nbsphinx',
]

# Give *lots* of time for cell execution!
# Note nbsphinx compiles *all* notebooks in docs unless excluded
nbsphinx_timeout = 300

# Make nbsphinx detect jupytext
nbsphinx_custom_formats = {
    '.py': ['jupytext.reads', {'fmt': 'py:percent'}],
}

# Set InlineBackend params in case nbsphinx skips ones in config.py
# Not necessary because config.py configures the backend.
# nbsphinx_execute_arguments = [
#     "--InlineBackend.figure_formats={'svg'}",
#     "--InlineBackend.rc={'figure.dpi': 100}",
# ]

# For now do not run doctest tests, these are just to show syntax
# and expected output may be graphical
doctest_test_doctest_blocks = ''

# Generate stub pages whenever ::autosummary directive encountered
# This way don't have to call sphinx-autogen manually
autosummary_generate = True

# Use automodapi tool, created by astropy people. See:
# https://sphinx-automodapi.readthedocs.io/en/latest/automodapi.html#overview
# Normally have to *enumerate* function names manually. This will document
# them automatically. Just be careful, if you use from x import *, to exclude
# them in the automodapi:: directive
automodapi_toctreedirnm = 'api'  # create much better URL for the page
automodsumm_inherited_members = False

# Logo
#html_logo = '_static/qgis_agri.png'

# Turn off code and image links for embedded mpl plots
# plot_html_show_source_link = False
# plot_html_show_formats = False

# One of 'class', 'both', or 'init'
# The 'both' concatenates class and __init__ docstring
# See: http://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
autoclass_content = 'both'

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False  # proplot imports everything in top-level namespace

# Napoleon options
# See: http://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
# * use_param is set to False so that we can put multiple "parameters"
#   on one line -- for example 'xlocator, ylocator : locator-spec, optional'
# * use_keyword is set to False because we do not want separate 'Keyword Arguments'
#   section and have same issue for multiple keywords.
# * use_ivar and use_rtype are set to False for (presumably) style consistency
#   with the above options set to False.
napoleon_use_ivar = False
napoleon_use_param = False
napoleon_use_keyword = False
napoleon_use_rtype = False
napoleon_numpy_docstring = True
napoleon_google_docstring = False
napoleon_include_init_with_doc = False  # move init doc to 'class' doc
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True

# Fix duplicate class member documentation from autosummary + numpydoc
# See: https://github.com/phn/pytpm/issues/3#issuecomment-12133978
numpydoc_show_class_members = False


# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    '_build', '_templates', '_themes', 'conf.py',
]

# Role
# default family is py, but can also set default role so don't need
# :func:`name`, :module:`name`, etc.
default_role = 'py:obj'

# set up the types of member to check that are documented
# add additional docstring
additional_docstrings = {
    'qgis_agri.resources': """
                           Plugin resources (PyQt5)
    
                           Resource object code
                              
                           Created by: The Resource Compiler for PyQt5 (Qt v5.11.2)
                           """,
}

##
def autodoc_skip_member(app, what, name, obj, skip, options):
    exclusions = ('__weakref__',  # special-members
                  '__doc__', '__module__', '__dict__',  # undoc-members
                  )
    
    qualname = getattr(obj, '__qualname__', '')    
    if qualname is None:
        print("'{}' is Noneeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee".format(name))
                  
    if name.endswith('__') and name.startswith('__'):
        return True
        
    exclude = name in exclusions
    return exclude
    
def autodoc_process_signature(app, what, name, obj, options, signature, return_annotation):
    return modified_signature, modified_return_annotation
    # will be rendered to method(modified_signature) -> modified_return_annotation
    
def autodoc_process_docstring(app, what, name, obj, options, lines):
    print ("What: {}".format(what))
    print ("Name: {}".format(name))
    print ("Options: {}".format(options))
    if name in additional_docstrings:
        lines.extend( [x.strip() for x in additional_docstrings[name].splitlines()] )
    
    if what == 'method':     
        method_name = name.split('.')[-1]
        if method_name.startswith("_"):
            lines.insert(0, """
                            `Private method`
                            """)
        
    if len(lines)==0:
        # modify the docstring so the rendered output is highlights the omission
        lines.append( ".. Warning:: {} '{}' undocumented".format(what, name) )


def setup(app):
    app.connect('autodoc-process-docstring', autodoc_process_docstring);
    #app.connect("autodoc-process-signature", autodoc_process_signature)
    app.connect('autodoc-skip-member', autodoc_skip_member)

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
#html_theme = 'alabaster'
html4_writer = True
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'logo_only': True,
    'display_version': False,
    'collapse_navigation': True,
    'navigation_depth': 4,
    'prev_next_buttons_location': 'bottom',  # top and bottom
}

#
html_show_sphinx = False

# If true, the reST sources are included in the HTML build as _sources/name. 
# The default is True.
html_copy_source = False


# If true (and html_copy_source is true as well), links to the reST sources 
# will be added to the sidebar. The default is True.
html_show_sourcelink = False

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = [
    'css/custom.css',
]

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
# The paper size ('letterpaper' or 'a4paper').
'papersize': 'a4paper',

# The font size ('10pt', '11pt' or '12pt').
'pointsize': '11pt',

# Latex figure (float) alignment
'figure_align': 'htbp',

# Don't mangle with UTF-8 chars
'inputenc': '',
'utf8extra': '',

# Additional stuff for the LaTeX preamble.
'preamble': '''
% Use some font with UTF-8 support with XeLaTeX
    \\usepackage{fontspec}
    \\setsansfont{DejaVu Sans}
    \\setromanfont{DejaVu Serif}
    \\setmonofont{DejaVu Sans Mono}
 '''
}