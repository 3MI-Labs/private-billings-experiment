# Use the official Ubuntu base image
FROM ubuntu:22.04

# Set environment variables to non-interactive (this prevents some prompts)
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary dependencies for OpenFHE and JupyterLab
RUN apt-get update && apt-get install -y \
    cmake \
    git \
    build-essential \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
    sudo \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install PyBind11
RUN python3 -m pip install "pybind11[global]"
	
# Install JupyterLab
# RUN python3 -m pip install --no-cache-dir jupyterlab

# Clone and build OpenFHE-development
RUN git clone https://github.com/openfheorg/openfhe-development.git \
    && cd openfhe-development \
    && mkdir build \
    && cd build \
    && cmake -DBUILD_UNITTESTS=OFF -DBUILD_EXAMPLES=OFF -DBUILD_BENCHMARKS=OFF .. \
    && make -j$(nproc) \
    && make install

# Assume that OpenFHE installs libraries into /usr/local/lib
# Update LD_LIBRARY_PATH to include this directory
ENV LD_LIBRARY_PATH=/usr/local/lib:${LD_LIBRARY_PATH}

# Clone and build OpenFHE-Python
RUN git clone https://github.com/openfheorg/openfhe-python.git \
    && cd openfhe-python \
    && git checkout 87700c2c250ff39eaaa5cbe4daed3e5cb5d9b726 \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make -j$(nproc) \
    && make install

ENV PYTHONPATH=/usr/lib/python3/dist-packages:${PYTHONPATH}

# Install the private-billings repository
COPY deps/private-billings private-billings/
RUN python3 -m pip install private-billings/
ENV PYTHONPATH=private-billings/src:${PYTHONPATH}

# Install the private-billlings dependencies
COPY deps/private-billings/requirements.txt ./
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Copy in the source code
COPY src ./src
COPY docker/launch.py ./launch.py

# Copy in the data sets
COPY data ./data

# Setup an app user so the container doesn't run as the root user
RUN useradd app
USER app

CMD python3 ./launch.py
