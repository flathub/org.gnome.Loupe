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

    loupe_tarball_url = module_tarball(manifest, "loupe")
    update_rust_deps(loupe_tarball_url, "loupe")

    glycin_tarball_url = module_tarball(manifest, "glycin-loaders")
    update_rust_deps(glycin_tarball_url, "glycin-loaders")

def update_rust_deps(url, name):
    print(f"Updating Rust dependencies for {name} from", file=sys.stderr)
    print(f" - <{url}>", file=sys.stderr)
    
    tar =  urllib.request.urlopen(url).read()
    archive = tarfile.open(fileobj=io.BytesIO(tar))
    lock_path = archive.getnames()[0] + '/' + 'Cargo.lock'
    lock_data = archive.extractfile(lock_path).read(-1)

    with tempfile.NamedTemporaryFile() as f:
        f.write(lock_data)
        subprocess.check_call(["./flatpak-builder-tools/cargo/flatpak-cargo-generator.py" ,f"--output=generated-sources-{name}.json", f.name])

def module_tarball(manifest, module_name):
    return next(module for module in manifest['modules'] if module['name'] == module_name)['sources'][0]['url']

__main__()
