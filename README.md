# ugreen_upk_exctract

This is a tiny python script for excracting **UGREEN** NAS `*.upk` files.

UPK files can be found here: [https://nas.ugreen.com/pages/downloads](https://nas.ugreen.com/pages/downloads)

📦 UPK File Format Specification

The UPK (Ugreen Package) file format is a custom binary packaging format used for bundling multiple objects of varying types (e.g., images, public keys, compressed archives) into a single container. 

🔖 File Header

Each valid .upk file must begin with the following fixed header:

UGREEN-PKG-FORMAT

This string is used to validate the integrity and format of the UPK file. The file is considered invalid if the header does not match exactly.

🧱 Object Structure

Each UPK file is composed of a sequence of typed objects with the following structure:

`<type>:<length>:<data>`

    <type>: A 3-character ASCII identifier (e.g., ico, ugb, pub).

    <length>: Length of the following binary data (as an integer in ASCII), followed by a colon.

    <data>: Raw binary payload of the object.

🔍 Parsing Order

    Read the 3-character type identifier until the first colon (:).

    Read the length of the data (until the next colon).

    Read and process the exact number of bytes specified by the length field.

🧾 Supported Object Types

|Type|	Description
|----|-----------------
|sig|	package signature - unknown format
|ico|	PNG icon image (typically a logo or branding asset).
|ugb|	Embedded LZMA-compressed .tar archive; may contain scripts, executables, or nested packages.
|pub|	Base64-encoded public key. The data is Base64-decoded during processing.
|obj|	Generic binary object (functionality undefined in code but possible to extend).

📂 UGB Sub-Package Format

A ugb object is a special case: it's a LZMA-compressed tar archive that is extracted in memory. It contains files such as:

    Shell scripts (uninstall.sh)

    Additional compressed packages (.ugb files themselves)

🔁 Nested Extraction

ugb files can recursively contain more .ugb files. The process to unpack is:

```bash
tar -xvzf archive.tar.gz        # Extract initial UPK payload
mv file.ugb file.ugb.xz         # Rename to standard .xz extension
unxz file.ugb.xz                # Decompress using LZMA
tar -xvf file.ugb               # Extract the inner tar archive
```

The provided script automates this using lzma and tarfile Python modules.

🛠️ Extraction Workflow

    UPK file is opened and validated using the fixed header.

    Each object is parsed one-by-one:

        Data is saved as <type>.<type> (e.g., ico.ico, ugb.ugb) in the output directory.

        If the object is a ugb, it is automatically extracted using the extract_ugb() function.

    The outer UPK file may be deleted after processing (this is optional and based on context).

🖥️ CLI Usage Example

python upk_extractor.py archive.upk ./output/

    archive.upk — path to the .upk file.

    ./output/ — optional output directory (default: ./out/).

🧰 Dependencies

    Python ≥ 3.6

    Standard libraries:

        os, tarfile, lzma, base64, shutil, logging, io, sys
