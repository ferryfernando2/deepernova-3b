#!/usr/bin/env python3
"""
Download and aggregate open-access journal articles from PubMed Central (PMC) OA bulk
until a target corpus size (MB) is reached.

This script connects to ftp.ncbi.nlm.nih.gov:/pub/pmc/oa_bulk,
downloads tar.gz batches, extracts .nxml files, parses <body> text,
and appends plain sentences to `data/journals_corpus.txt` until target size.

Notes:
- Requires network access and sufficient disk space.
- Processing PMC XML is imperfect but produces readable text suitable for training.
- Use responsibly and follow PMC terms of use.

Usage:
    python download_journals.py --target-mb 700 --out data/journals_corpus.txt

"""

import argparse
import ftplib
import io
import os
import tarfile
import xml.etree.ElementTree as ET
from pathlib import Path
from tqdm import tqdm

FTP_HOST = 'ftp.ncbi.nlm.nih.gov'
FTP_DIR = '/pub/pmc/oa_bulk'

# helper: extract visible text from an NXML element
def extract_text_from_nxml_bytes(nxml_bytes):
    try:
        root = ET.fromstring(nxml_bytes)
    except Exception:
        return ""
    texts = []
    # find all body paragraphs
    for body in root.findall('.//body'):
        for p in body.iter():
            if p.text and p.text.strip():
                texts.append(p.text.strip())
            if p.tail and p.tail.strip():
                texts.append(p.tail.strip())
    return '\n'.join(texts)


def list_ftp_files(conn):
    files = []
    conn.cwd(FTP_DIR)
    conn.retrlines('NLST', files.append)
    # Keep only .tar.gz files
    files = [f for f in files if f.endswith('.tar.gz')]
    # sort for stable order
    files.sort()
    return files


def stream_download_and_extract(ftp, filename, out_file, bytes_needed):
    """Download a tar.gz from FTP and extract nxml files incrementally.
    Append extracted text lines to out_file until bytes_needed reached.
    Returns number of bytes written.
    """
    written = 0

    # retrieve file into bytes stream (streaming via retrbinary into buffer)
    print(f"[*] Downloading {filename} (streaming)")
    mem = io.BytesIO()
    def callback(chunk):
        mem.write(chunk)
    ftp.retrbinary('RETR ' + filename, callback)
    mem.seek(0)

    # open tar.gz from bytes
    try:
        with tarfile.open(fileobj=mem, mode='r:gz') as tar:
            members = [m for m in tar.getmembers() if m.name.endswith('.nxml')]
            for m in tqdm(members, desc=f'Extract {filename}', unit='file'):
                if bytes_needed <= 0:
                    break
                try:
                    f = tar.extractfile(m)
                    if f is None:
                        continue
                    content = f.read()
                    text = extract_text_from_nxml_bytes(content)
                    if not text:
                        continue
                    # write to out_file line by line
                    with open(out_file, 'a', encoding='utf-8') as out:
                        # split into sentences/lines
                        for line in text.splitlines():
                            line = line.strip()
                            if len(line) < 30:
                                continue
                            out.write(line + '\n')
                            written += len((line + '\n').encode('utf-8'))
                            bytes_needed -= len((line + '\n').encode('utf-8'))
                            if bytes_needed <= 0:
                                break
                except Exception:
                    continue
    except Exception as e:
        print(f"  [!] Failed to process {filename}: {e}")
    return written


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--target-mb', type=int, default=700, help='Target corpus size in megabytes')
    parser.add_argument('--out', default='data/journals_corpus.txt', help='Output corpus file')
    parser.add_argument('--start-file', default=None, help='Start from specific tar.gz filename')
    args = parser.parse_args()

    target_bytes = args.target_mb * 1024 * 1024
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # current size
    cur_size = out_path.stat().st_size if out_path.exists() else 0
    if cur_size >= target_bytes:
        print(f"Output already >= target ({cur_size} bytes). Nothing to do.")
        return
    bytes_needed = target_bytes - cur_size
    print(f"Target: {args.target_mb} MB ({target_bytes} bytes). Need: {bytes_needed} bytes")

    # connect to ftp
    print(f"Connecting to {FTP_HOST}...")
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login()

    files = list_ftp_files(ftp)
    print(f"Found {len(files)} tar.gz files in PMC OA bulk")

    # if start-file provided, find index
    start_idx = 0
    if args.start_file and args.start_file in files:
        start_idx = files.index(args.start_file)

    total_written = 0
    for i in range(start_idx, len(files)):
        fname = files[i]
        print(f"Processing [{i+1}/{len(files)}]: {fname}")
        written = stream_download_and_extract(ftp, fname, str(out_path), bytes_needed)
        total_written += written
        bytes_needed -= written
        print(f"  -> Written {written} bytes; Remaining: {max(bytes_needed,0)} bytes")
        if bytes_needed <= 0:
            break

    ftp.quit()

    final_size = out_path.stat().st_size
    print(f"\nDone. Final file: {out_path} ({final_size} bytes / {final_size/1024/1024:.2f} MB)")
    print("You can now train with this corpus file.")

if __name__ == '__main__':
    main()
