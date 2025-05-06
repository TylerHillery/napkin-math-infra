# Overview
The purpose of this repository is to provide the infrastructure necessary to measure and benchmark common programming operations for the Napkin Math project. Napkin Math is a resource aimed at helping engineers estimate the performance of systems using first principles thinking.

For more information about Napkin Math, check out the [main repository](https://github.com/sirupsen/napkin-math) and watch this [talk](https://www.youtube.com/watch?v=IxkSlnrRFqc).

## Details
Each stack is equal to one benchmark expect for the `shared` stack which contains shared resources across all benchmarks (e.g. GCS Bucket for results). The stack gets dynamically imported so it's required to create a `benchmark/{{ BENCHMARK_NAME }}/{{ BENCHMARK_NAME}}.py` file where you create a `define_resources()` function. This then needs to be added into the `__init__.py` so it can be import at the top level module. The define resources is required to also run the benchmark and save the results to `gs://{{ bucket_name }}/{{ benchmark_name }}/results.txt`.

The [benchmark.yml](./.github/workflows/benchmark.yml) file is what kicks of the benchmark where the stack name (a.k.a the benchmark) is a required input. This runs `pulumi up` and then polls for the results file. Once the file is found it downloads it and uploads as an artifact. The `cleanup` job will run after the `benchmark` regardless if it's successful or not to spin down any resources that were provisioned for the benchmark.