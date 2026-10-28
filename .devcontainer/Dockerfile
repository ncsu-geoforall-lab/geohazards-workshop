FROM osgeo/grass-gis:8.5.0-ubuntu

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# r.dem.lod and r.dem.errprop run under the system Python, not the workshop
# virtual environment. The Ubuntu scipy package is built for NumPy 1, so
# install a NumPy 2 compatible scipy with pip.
RUN python3 -m pip install --no-cache-dir --break-system-packages "scipy>=1.14,<2"

COPY --from=ghcr.io/astral-sh/uv:0.9.6 /uv /uvx /bin/

# Install the pinned r.dem release from ncsu-geoforall-lab/r.dem into a shared
# addon path so it is available to every user and survives the workspace mount.
ARG RDEM_VERSION=1.1.0
ENV GRASS_ADDON_BASE=/opt/grass-addons
RUN curl -fsSL "https://github.com/ncsu-geoforall-lab/r.dem/archive/refs/tags/v${RDEM_VERSION}.tar.gz" \
    | tar -xz -C /tmp \
    && grass --tmp-project XY --exec g.extension extension=r.dem \
    url="/tmp/r.dem-${RDEM_VERSION}/src" prefix="$GRASS_ADDON_BASE" \
    && rm -rf "/tmp/r.dem-${RDEM_VERSION}"

CMD ["/bin/bash"]
