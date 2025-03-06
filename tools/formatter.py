import subprocess


def _format_project():
    usort_rc = subprocess.call("poetry run usort format xyz tests tools", shell=True)
    docformatter_rc = subprocess.call(
        "poetry run docformatter --in-place -r xyz/ tools/", shell=True
    )
    black_rc = subprocess.call("poetry run black xyz/ tools/ tests/", shell=True)
    return any([usort_rc, docformatter_rc, black_rc])


if __name__ == "__main__":
    exit(_format_project())
