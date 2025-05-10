import os
import tarfile
import lzma
import shutil
import base64
import io
import logging
import sys

def default_on_new_file(path, fn):
    logging.info(f"Extracted {os.path.join(path,fn)}")

def extract_ugb(filename, path='./out', on_new_file=default_on_new_file):
    """
    Extracts a `.tar.gz` archive, decompressing and extracting `.ugb` files (LZMA-compressed tar files) in memory.

    Args:
        filename (str): Path to the `.tar.gz` archive.
        path (str): Directory to extract files to (default is './out').

    Calls `on_new_file()` for each extracted file.

    Example:
        extract_ugb("archive.tar.gz", path='./output')

    #tar -xvzf ugb.ugb
    #    uninstall.sh
    #    com.ugreen.downloadmgr.ugb
    #
    #  mv com.ugreen.downloadmgr.ugb com.ugreen.downloadmgr.ugb.xz
    #  unxz com.ugreen.downloadmgr.ugb.xz
    #  tar -xvf com.ugreen.downloadmgr.ugb
    """
    # Step 1: Extract ugb.ugb (gzip-compressed tar)
    with tarfile.open(filename, "r:gz") as tar:
        for member in tar.getmembers():
            if member.name.endswith(".ugb"):
                # Step 1: Extract (LZMA-compressed files (typically .xz)
                file_obj = tar.extractfile(member)
                with lzma.open(file_obj) as xz_in:
                    with tarfile.open(fileobj=xz_in, mode="r:") as inner_tar:
                        for m in inner_tar.getmembers():
                            inner_tar.extract(m, path=path)
                            on_new_file(path, m.name)
            else:
                tar.extract(member, path=path)
                on_new_file(path, member.name)
    os.remove(filename) # clean up

class UPKExctactor:

    __header = b'UGREEN-PKG-FORMAT'

    def __init__(self, fn, workdir='./out'):
        assert fn.endswith('.upk'), "File must end with .upk"
        self.__workdir = workdir
        self.i = 0
        self.d = open(fn, 'rb').read()
        self.__read_header()
        logging.debug(f"File {fn} size:{len(self.d)}b")

    def __read_header(self):
        head_len = len(self.__header)
        assert len(self.d) > head_len and self.d[0:head_len] == self.__header, f"File is not a valid UPK file"
        self.i = head_len

    def read_object(self):

        def read_until(c):
            b = self.i
            while  self.i < len(self.d) and chr(self.d[self.i]) != c:
                self.i += 1
            self.i += 1
            return self.d[b:self.i-1]

        # read type (3 characters)
        _type = read_until(':') # ico/png/obj/ugb
        if not _type:
            logging.debug("end of file")
            return False
        assert len(_type)==3, f"len {len(_type)} != 3"
        _type = _type.decode('utf-8','backslashreplace')

        # read len (raw integeter)
        _len = int(read_until(':'))

        # save data to file
        self.__process_object(_type, _len)
        self.i += _len

        return True

    def __process_object(self, _type, _len):

        logging.info(f">> upk next {_type} {_len}b")

        out_fn = os.path.join(self.__workdir, f"{_type}.{_type}")

        with open(out_fn, 'wb') as out_file:
            out_file.write(self.d[self.i:self.i+_len])

        if _type == 'pub':
            logging.debug('this is a public key...')
            data = self.d[self.i:self.i+_len]
            decoded_data = base64.b64decode(data)
            logging.debug(decoded_data)
        elif _type == "ico":
            logging.debug('this is a png image...')
        elif _type == "ugb":
            extract_ugb(out_fn, path=self.__workdir)

if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    # arg1 - input file
    f = os.sys.argv[1] if len(sys.argv) > 1 else 'afc859cb-5ddb-4267-8832-caf0cb29fd32.upk'
    assert os.path.exists(f), f"File {f} not found"
    # arg2 - output directory
    workdir = os.sys.argv[2] if len(sys.argv) > 2 else './out/'
    os.makedirs(workdir, exist_ok=True)

    # process the file
    extractor = UPKExctactor(f, workdir=workdir)
    while extractor.read_object():
        pass
