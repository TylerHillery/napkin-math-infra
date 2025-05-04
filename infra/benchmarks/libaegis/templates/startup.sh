#!/bin/bash

# Install necessary dependencies
echo "=== Installing dependencies ==="
sudo dpkg --configure -a
apt-get install -y git curl xz-utils

# Download and install Zig
echo "=== Installing Zig ==="
curl -LO https://ziglang.org/download/0.14.0/zig-linux-x86_64-0.14.0.tar.xz
tar -xf zig-linux-x86_64-0.14.0.tar.xz
mv zig-linux-x86_64-0.14.0 /usr/local/lib/
ln -s /usr/local/lib/zig-linux-x86_64-0.14.0/zig /usr/local/bin/zig

# Clone the libaegis repository
echo "=== Cloning libaegis repository ==="
git clone https://github.com/aegis-aead/libaegis /opt/libaegis
cd /opt/libaegis

# Build the project
echo "=== Building libaegis ==="
export HOME=/root
zig build -Drelease -Dwith-benchmark

# Run the benchmark and save results
echo "=== Running benchmark ==="
sh -c './zig-out/bin/benchmark > benchmark_results.txt'
gsutil cp benchmark_results.txt gs://{{ bucket_name }}/{{ benchmark_name }}/results.txt