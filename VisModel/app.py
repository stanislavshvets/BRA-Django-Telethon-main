import multiprocessing
import os
from concurrent.futures import ProcessPoolExecutor

import psutil

from DebugPrinter import DPrint
from HandlerModel import HandlerModel

def main():
    with ProcessPoolExecutor() as pool:
        for file in get_files('Data'):
            pool.submit(convert, file)

def convert(file, frames = 120):
    hm = HandlerModel(
        full_filename=f'Data/{file}',
        frames=frames,
        dprint=DPrint(prefix='GifRender', is_without_repeats=False),
    )

    res = hm.process()

    with open('Videos/' + file + '.mp4', 'wb') as f:
        f.write(res[2].getbuffer())

def get_files(folder_path):
    return [f for f in os.listdir(folder_path) if f.endswith('.obj')]


if __name__ == '__main__':
    main()

