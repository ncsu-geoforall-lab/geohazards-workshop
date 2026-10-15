FROM osgeo/grass-gis:8.5.0-ubuntu

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.9.6 /uv /uvx /bin/

# Install r.dem from OSGeo/grass-addons into a shared addon path so it is
# available to every user and survives the workspace mount.
ENV GRASS_ADDON_BASE=/opt/grass-addons
RUN grass --tmp-project XY --exec g.extension extension=r.dem prefix=$GRASS_ADDON_BASE

CMD ["/bin/bash"]
