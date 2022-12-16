# nd2tiff

This is a small tool to convert Nikon nd2 files in a given folder to tiff stacks. It uses the [nd2](https://github.com/tlambert03/nd2) package to read nd2 files and [tifffile](https://github.com/cgohlke/tifffile) to save them as tiff.

## Installation

To run the script, you need a functional Python and the [nd2](https://github.com/tlambert03/nd2) and [tifffile](https://github.com/cgohlke/tifffile) packages. To run the CLI you will also need [typer](https://github.com/tiangolo/typer). To simplify installation, we recommend to use conda and then to create the appropriate environment using the [environment.yml](https://raw.githubusercontent.com/guiwitz/BernMICscripts/master/nd2tiff/environment.yml) file:

```bash
conda env create -f environment.yml
```

This will create an environment called ```nd2convert``` that you can activate with:

```bash
conda activate nd2convert
```

Then save the [nd2tiff.py](https://raw.githubusercontent.com/guiwitz/BernMICscripts/master/nd2tiff/nd2tiff.py) file to your computer. Open a terminal and move where you just save the file.


## Usage

To run conversion, you only need to specify the path to the folder containing your nd2 files. By default this will create a subfolder called ```converted``` in the same location. You can execute conversion with:

```bash
python nd2tiff.py /path/to/folder/with/nd2files
```

If you want to save the converted files to a specific location, you can point to an existing folder with the ```output_folder``` option:

```bash
python nd2tiff.py /path/to/folder/with/nd2files --output-folder path/to/my/existing/output/folder
```

## Notes

The tiff files are save in bigtiff format to allow conversion of files larger than 4Gb.
