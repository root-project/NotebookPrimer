#!/usr/local/bin/python
import string
import sys
import json
import StringIO
import re

try:
	import nbformat
except ImportError as err:
	print("The Python API Nbformat is not installed. To install it visit https://github.com/jupyter/nbformat. \n OS error: {0}".format(err))
	raise

from nbformat import NotebookNode
try:
    from nbconvert.preprocessors import ExecutePreprocessor
except ImportError as err:
	print("Nbconvert is not installed. To install it use: \n pip install nbconvert \n or visit: http://nbconvert.readthedocs.io/en/latest/install.html. \n OS error: {0}".format(err))
	raise
from StringIO import StringIO
import codecs
from nbformat.v4.nbbase import (
    new_code_cell, new_markdown_cell, new_notebook,
    new_output, new_raw_cell
)
infilename = sys.argv[1]
outfilename = sys.argv[2]
f = open(infilename)
# lines = f.readlines()
# f.close()
# text = "".join(lines)

nb = nbformat.read(infilename, 4)
nb_new = nbformat.NotebookNode()

cells_new=[]
offset=0
reright=0
for cell in nb.cells:
  if cell["cell_type"] == "code":
    if cell["source"] == '%jsroot on':
      offset = -1
    elif cell["source"] == '%jsroot off':
      offset = -1
    else:
      # print cell.execution_count
      # print type(cell.execution_count)
      cells_new.append(new_code_cell(
      source=cell.source,
      metadata=cell.metadata,
      outputs=[],
      execution_count=cell.execution_count+offset))
      # print cell.execution_count+offset
  elif cell["cell_type"] == "markdown":
    if "<img" in cell.source:
        buf = cell.source.split("\"")
        flag = "none"
        src = ""
        alt =""
        width=""
        height=""
        for item in buf:
            if flag is "none":
                if "src" in item:
                    flag = "src"
                elif "alt" in item:
                    flag = "alt"
                elif "width=" in item:
                    flag = "width"
                elif "height=" in item:
                    flag = "height"
            else:
                if flag is "src":
                    src=item
                    flag = "none"
                elif flag is "alt":
                    alt=item
                    flag = "none"
                elif flag is "width":
                    width=item
                    flag = "none"
                elif flag is "height":
                    height=item
                    flag = "none"
        height_check=re.findall(r'\d+', height)
        width_check=re.findall(r'\d+', width)
        if int(height_check[0]) > 300:
            height = "300px" 
        if int(width_check[0]) > 400:
            width = "400px" 
        elif int(width_check[0]) < 400 and int(width_check[0]) > 100:
            width = "100px" 
        cells_new.append(new_markdown_cell(
        source="\\begin{figure} \n \centering \includegraphics[width=" + width +",height="+ height + "]{"+ src +"} \n \caption{" + alt +"} \n \end{figure}",
        metadata=cell.metadata))
        reright=1
    elif reright==1:
        cells_new.append(new_markdown_cell(
        source="\\raggedright",
        metadata=cell.metadata))
        reright=0
        cells_new.append(new_markdown_cell(
        source=cell.source,
        metadata=cell.metadata))
    else:
        cells_new.append(new_markdown_cell(
        source=cell.source,
        metadata=cell.metadata))
  else:
    cells_new.append(new_raw_cell(
    source=cell.source,
    metadata=cell.metadata))

  # print cell.cell_type

nb_new = new_notebook(cells=cells_new,
    metadata=nb.metadata,
    nbformat=nb.nbformat,
    nbformat_minor=nb.nbformat_minor
)

with codecs.open(outfilename, encoding='utf-8', mode='w') as out:
    nbformat.write(nb_new, out)

