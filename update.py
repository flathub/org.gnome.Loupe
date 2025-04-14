#!/usr/bin/env python3

import subprocess
import sys
import yaml
import urllib.request
import tarfile
from pathlib import Path
import io
import tempfile

def __main__():
    print("Updating Flatpak modules", file=sys.stderr)

    subprocess.check_call(["flatpak", "run", "org.flathub.flatpak-external-data-checker", "--edit-only", "org.gnome.Loupe.yml"])

    with open('org.gnome.Loupe.yml') as f:
        manifest = yaml.safe_load(f)

    loupe_tarball_url = manifest['modules'][-1]['sources'][0]['url']
    update_rust_deps(loupe_tarball_url)

def update_rust_deps(url):
    print("Updating Rust dependencies from", file=sys.stderr)
    print(f" - <{url}>", file=sys.stderr)
    
    tar =  urllib.request.urlopen(url).read()
    archive = tarfile.open(fileobj=io.BytesIO(tar))
    lock_path = archive.getnames()[0] + '/' + 'Cargo.lock'
    lock_data = archive.extractfile(lock_path).read(-1)

    with tempfile.NamedTemporaryFile() as f:
        f.write(lock_data)
        subprocess.check_call(["./flatpak-builder-tools/cargo/flatpak-cargo-generator.py", f.name])

__main__()
