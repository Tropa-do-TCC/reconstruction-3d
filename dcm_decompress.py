import os
import sys

import gdcm


def decompress_slices(dicom_dir:str):
    print(f"Decompressing slices...")

    slices = os.listdir(dicom_dir)

    for slice in slices:
        file_path = f"{dicom_dir}/{slice}"

        reader = gdcm.ImageReader()
        reader.SetFileName(file_path)

        if not reader.Read():
            print(f"Couldn't read {file_path}")
            sys.exit(1)

        change = gdcm.ImageChangeTransferSyntax()
        change.SetTransferSyntax(gdcm.TransferSyntax(
            gdcm.TransferSyntax.ImplicitVRLittleEndian))
        change.SetInput(reader.GetImage())
        if not change.Change():
            sys.exit(1)

        writer = gdcm.ImageWriter()
        writer.SetFileName(file_path)
        writer.SetFile(reader.GetFile())
        writer.SetImage(change.GetOutput())

        if not writer.Write():
            print(f"Couldn't write {file_path}")
            sys.exit(1)
