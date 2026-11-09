"""Execute the notebook in a fresh kernel using this interpreter."""
import sys
from pathlib import Path
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

path=Path(__file__).with_name('results_and_discussion.ipynb')
nb=nbformat.read(path,as_version=4)
km=KernelManager(kernel_name='python3')
km.kernel_spec.argv=[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}']
NotebookClient(nb,km=km,timeout=300,resources={'metadata':{'path':str(path.parent.resolve())}}).execute()
nbformat.write(nb,path)
print('PASS:',path.resolve())
