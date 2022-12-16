import typer
from pathlib import Path
import nd2
from tifffile import imwrite

"""
Small CLI interface to convert nd2 files in a given folder into tiff stacks.
"""
def main(
    image_folder: str,
    output_folder: str = typer.Option(None, help="Output folder")
):
    """
    Convert nd2 to tiff
    
    Parameters
    ----------
    image_folder: str
        path to folder containing nd2 files
    output_folder: str
        path to output folder. If not given, a folder called 'converted' will be created in the input folder.
    """
    
    nd2_dir = Path(image_folder)
    if output_folder is None:
        out_dir = nd2_dir.joinpath('converted')
        if not out_dir.exists():
            out_dir.mkdir()
    else:
        out_dir = Path(output_folder)
    nd2_files = list(nd2_dir.glob('*.nd2'))
    for f in nd2_files:
        print(f"Converting {f}")
        my_array = nd2.imread(f)#, dask=True)     
        imwrite(out_dir.joinpath(f.stem+".tiff"), my_array, bigtiff=True)
    

if __name__ == "__main__":
    typer.run(main)