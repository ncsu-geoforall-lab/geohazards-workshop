# Setup

Pick one option. Option 1 needs only a browser and a GitHub account. Please
do this before the workshop, since conference wifi is not reliable for large
downloads.

## Option 1. GitHub Codespaces (recommended)

1. Sign in to GitHub.
2. Open
   <https://codespaces.new/ncsu-geoforall-lab/geohazards-workshop>
   and create the codespace. The 4-core machine is enough.
3. Wait for the setup to finish. It installs the Python packages and
   downloads the workshop data.
4. Open `notebooks/00_setup_check.ipynb`, select the `.venv` kernel, and run
   all cells. Every check should print `OK`.

A free personal GitHub account includes enough Codespaces hours for the
workshop. Stop the codespace when you are done so it does not use your hours.

## Option 2. Local container

You need Docker and VS Code with the Dev Containers extension.

```bash
git clone https://github.com/ncsu-geoforall-lab/geohazards-workshop.git
code geohazards-workshop
```

Then choose "Reopen in Container" and continue from step 3 above.

## Option 3. Native install

Use this only if you already run GRASS. The `r.dem` tools need
**GRASS 8.5 or newer**.

1. Install GRASS 8.5 from <https://grass.osgeo.org/download/>.
2. Install the workshop version of the `r.dem` toolset (v1.1.0, which adds
   `r.dem.dod`) from a GRASS session:

   ```bash
   curl -fsSL https://github.com/ncsu-geoforall-lab/r.dem/archive/refs/tags/v1.1.0.tar.gz | tar -xz
   g.extension extension=r.dem url=r.dem-1.1.0/src
   ```

   This compiles two C tools, so you need a C compiler and `make`. On Windows,
   use Option 1 or 2 instead.
3. Install the Python packages into the Python that GRASS uses:

   ```bash
   python3 -m pip install numpy scipy pandas matplotlib ipykernel
   ```

4. Get the data and run the setup check:

   ```bash
   git clone https://github.com/ncsu-geoforall-lab/geohazards-workshop.git
   cd geohazards-workshop
   bash scripts/fetch_data.sh
   ```

   Then open `notebooks/00_setup_check.ipynb` in Jupyter and run all cells.

## Help

Open an issue at
<https://github.com/ncsu-geoforall-lab/geohazards-workshop/issues>.
