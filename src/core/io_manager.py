# Built-in modules
from pathlib import Path

def scan_path(path : Path, glob: str = '*'):
    
    for f in path.iterdir():

        if f.is_dir():
            pass
        elif f.is_file():
            pass
        yield f

def add_prefix_suffix(filepath: Path,
                      prefix: str = None,
                      suffix: str = None) -> Path:
    """Add a prefix and/or a suffix to a file name"""

    # Check if the prefix has a underscore character in it, add it if not.
    if prefix is not None and prefix.endswith('_') is True:
        prefix =  prefix + '_'
    elif prefix is None:
        prefix = ''

    # Check if the suffix has a underscore character in it, add it if not.
    if suffix is not None and suffix.startswith('_') is True:
        suffix =  '_' + suffix
    elif suffix is None:
        suffix = ''

    return filepath.with_stem(prefix + filepath.stem + suffix)

def rename_file_duplicate(filepath: Path, zero_fill: int):
    instance_count = len(sorted(filepath.glob(filepath.stem+ "_*" + filepath.suffix)))
    instance_next = f"_{instance_count + 1}"
    instance_suffix = instance_next.zfill(zero_fill)
    
    return add_prefix_suffix(filepath, suffix=instance_suffix), instance_count

def write_file(data: str | bytes | bytearray,
               filepath: Path,
               mode: int = 0,
               overwrite: bool = False) -> bool:
    """    
    Parameters
    ----------
    data: Any
        Data to write in the file.\n
    filepath: Path
        Where to file will be output.\n
    mode: int
        Define the writing mode.
        `0` is corresponding to `text`
        `1` is corresponding to `bytes`\n
    overwrite: bool
        Confirm whether or not you want to overwrite an existing file.\n
    """

    if overwrite:
        match mode:
            case 0:
                writing_mode = 'wt'
            case 1:
                writing_mode = 'wb'
    else:
        match mode:
            case 0:
                writing_mode = 'xt'
            case 1:
                writing_mode = 'x'

    with filepath.open(mode=writing_mode) as f:
        f.write(data)
        f.close()
    
    return filepath.is_file()

def load_file(filepath: Path, mode: int = 0) -> str | bytes | bytearray :
    match mode:
        case 0:
            with filepath.open(mode='rt') as f:
                f.read()
        case 1:
            with filepath.open(mode='rb') as f:
                f.seek(0)
                f.read()