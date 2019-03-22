#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# fwdpy11 documentation build configuration file, created by
# sphinx-quickstart on Mon Mar 20 12:22:19 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
# import subprocess

if (os.environ.get('READTHEDOCS') == "True") is False:
    sys.path.insert(0, os.path.abspath('..'))
else:
    import site
    p = site.getsitepackages()[0]
    sys.path.insert(0, p)

nitpicky = True
nitpick_ignore = [('py:class', 'pybind11_builtins.pybind11_object'),
                  ('py:class', 'fwdpy11._regions.Region'),
                  ('py:class', 'fwdpy11._regions.Sregion'),
                  ('py:class', 'object'),
                  ('py:obj', 'tuple')]
#    subprocess.Popen(['doxygen', 'fwdpp.doxygen'],env=my_env)
# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.doctest',
              'sphinx.ext.todo',
              'sphinx.ext.coverage',
              'sphinx.ext.mathjax',
              'IPython.sphinxext.ipython_console_highlighting',
              'IPython.sphinxext.ipython_directive',
              ]
# 'breathe']

# if (os.environ.get('READTHEDOCS')=="True") is False:
#    my_env=os.environ.copy()
#    my_env["LD_LIBRARY_PATH"]=os.path.join(sys.prefix,'lib')
#    subprocess.Popen(['doxygen', 'fwdpy11.doxygen'],env=my_env)
#    subprocess.Popen(['doxygen', 'fwdpp.doxygen'],env=my_env)
#    breathe_projects={'fwdpy11':'xml','fwdpp':'fwdpp_xml'}
#    breathe_default_project="fwdpy11"
# Add any paths that contain templates here, relative to this directory.
templates_path = ['fwdpy11_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'fwdpy11'
copyright = '2017, Kevin Thornton'
author = 'Kevin Thornton'

# http://stackoverflow.com/questions/5599254/how-to-use-sphinxs-autodoc-to-document-a-classs-init-self-method


def skip(app, what, name, obj, skip, options):
    if name == "__init__":
        return False
    return skip


def setup(app):
    app.connect("autodoc-skip-member", skip)


# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '0.3.1'
# The full version, including alpha/beta/rc tags.
release = '0.3.1'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'default'

if (os.environ.get('READTHEDOCS') == "True") is True:
    html_theme_options = {
        'github_user': 'molpopgen',
        'github_repo': 'fwdpy11',
        #        'github_button':True,
        #        'github_banner':True,
    }

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'fwdpy11doc'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'fwdpy11.tex', 'fwdpy11 Documentation',
     'Kevin Thornton', 'manual'),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'fwdpy11', 'fwdpy11 Documentation',
     [author], 1)
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'fwdpy11', 'fwdpy11 Documentation',
     author, 'fwdpy11', 'One line description of project.',
     'Miscellaneous'),
]
