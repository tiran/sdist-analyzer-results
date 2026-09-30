# ELF Analysis: cuda12.9-ubi9-test

## Summary

| Category | Count | % |
|:---|---:|---:|
| **Total packages** | **1573** |  |
| &ensp;Purelib (pure Python) | 1294 | 82.3% |
| &ensp;Platlib (native code) | 279 | 17.7% |
| &ensp;Manylinux + bundleable | 204 | 13.0% |
| &ensp;&ensp;Manylinux-only | 190 | 12.1% |
| &ensp;&ensp;Could be bundled | 10 | 0.6% |
| &ensp;&ensp;Pre-built (manylinux) | 4 | 0.3% |
| &ensp;Platform-dependent | 72 | 4.6% |
| &ensp;&ensp;Accelerator-specific | 19 | 1.2% |
| &ensp;&ensp;Unbundleable | 51 | 3.2% |
| &ensp;&ensp;Undecided | 1 | 0.1% |
| &ensp;&ensp;Unknown | 1 | 0.1% |
| &ensp;No ELF data (other) | 6 | 0.4% |
| **Purelib + manylinux + bundleable** | **1498** | **95.2%** |
| **Platform/accel + other** | **75** | **4.8%** |

## Charts

```mermaid
%%{init: {"theme": "base", "themeVariables": {"xyChart": {"plotColorPalette": "#0072B2, #009E73, #D55E00, #999999"}}}}%%
xychart-beta
    title "cuda12.9-ubi9-test -- package overview"
    x-axis ["purelib", "manylinux + bundleable", "platform/accel", "no ELF data (other)"]
    y-axis "Packages"
    bar [1294, 204, 72, 6]
```

## External Dependencies

| Library | Count | Projects |
|:---|---:|:---|
| libcudart.so.12 | 18 | bitsandbytes, causal-conv1d, deep-ep, deep-gemm, detectron2, faiss-cpu, flash-attn, flashinfer-jit-cache, kvcached, mamba-ssm, nixl-cu12, onnxruntime-gpu, pplx-kernels, torchao, torchaudio, torchcodec, torchvision, vllm |
| libcrypto.so.3 | 13 | c2pa-python, cmake, cryptography, grpcio, maturin, pyarrow, pymssql, ray-haproxy, rfc3161-client, runai-model-streamer-azure, runai-model-streamer-s3, sccache, yara-python |
| libtorch_cpu.so | 13 | causal-conv1d, deep-ep, deep-gemm, detectron2, flash-attn, kvcached, mamba-ssm, pplx-kernels, torchao, torchaudio, torchcodec, torchvision, vllm |
| libssl.so.3 | 12 | c2pa-python, cmake, cryptography, grpcio, maturin, pyarrow, pymssql, ray-haproxy, rfc3161-client, runai-model-streamer-azure, runai-model-streamer-s3, sccache |
| libc10.so | 11 | causal-conv1d, deep-ep, deep-gemm, detectron2, flash-attn, kvcached, mamba-ssm, pplx-kernels, torchcodec, torchvision, vllm |
| libc10_cuda.so | 10 | causal-conv1d, deep-ep, deep-gemm, detectron2, flash-attn, mamba-ssm, pplx-kernels, torchcodec, torchvision, vllm |
| libgomp.so.1 | 10 | bitsandbytes, ctranslate2, faiss-cpu, lightgbm, numba, pennylane-lightning, scikit-learn, scikit-network, simsimd, xgboost |
| libtorch_cuda.so | 8 | deep-gemm, flash-attn, pplx-kernels, torchao, torchaudio, torchcodec, torchvision, vllm |
| libtorch_python.so | 8 | causal-conv1d, deep-ep, deep-gemm, detectron2, flash-attn, kvcached, mamba-ssm, vllm |
| libbz2.so.1 | 6 | daft, pyarrow, python-libsbml, selenium, uv, uv-build |
| libjpeg.so.62 | 6 | docling-parse, opencv-python, opencv-python-headless, pillow, torchcodec, torchvision |
| libopenblasp.so.0 | 6 | numpy, opencv-python, opencv-python-headless, scipy, scs, sparsediffpy |
| libcuda.so.1 | 5 | flashinfer-jit-cache, kvcached, pplx-kernels, pyarrow, vllm |
| libavcodec.so.60 | 4 | av, opencv-python, opencv-python-headless, torchcodec |
| libavformat.so.60 | 4 | av, opencv-python, opencv-python-headless, torchcodec |
| libavutil.so.58 | 4 | av, opencv-python, opencv-python-headless, torchcodec |
| libcublas.so.12 | 4 | bitsandbytes, faiss-cpu, flashinfer-jit-cache, onnxruntime-gpu |
| libcublasLt.so.12 | 4 | bitsandbytes, faiss-cpu, flashinfer-jit-cache, onnxruntime-gpu |
| libnvrtc.so.12 | 4 | deep-gemm, flashinfer-jit-cache, torchcodec, vllm |
| libopenjp2.so.7 | 4 | docling-parse, opencv-python, opencv-python-headless, pillow |
| libpng16.so.16 | 4 | opencv-python, opencv-python-headless, torchcodec, torchvision |
| libre2.so.9 | 4 | grpcio, onnxruntime, onnxruntime-gpu, pyarrow |
| libswscale.so.7 | 4 | av, opencv-python, opencv-python-headless, torchcodec |
| libwebp.so.7 | 4 | opencv-python, opencv-python-headless, pillow, torchvision |
| libavdevice.so.60 | 3 | av, opencv-python, torchcodec |
| libcurl.so.4 | 3 | pyarrow, runai-model-streamer-azure, runai-model-streamer-s3 |
| liblz4.so.1 | 3 | lz4, memray, pyarrow |
| libtiff.so.5 | 3 | opencv-python, opencv-python-headless, pillow |
| libtorch.so | 3 | pplx-kernels, torchcodec, vllm |
| libwebpdemux.so.2 | 3 | opencv-python, opencv-python-headless, pillow |
| libwebpmux.so.3 | 3 | opencv-python, opencv-python-headless, pillow |
| libavfilter.so.9 | 2 | av, torchcodec |
| libffi.so.8 | 2 | cffi, pandoc-rhai |
| libfreetype.so.6 | 2 | docling-parse, pillow |
| libgdal.so.36 | 2 | pyogrio, rasterio |
| libgssapi_krb5.so.2 | 2 | gssapi, pymssql |
| liblcms2.so.2 | 2 | docling-parse, pillow |
| liblzma.so.5 | 2 | maturin, uv-build |
| libmariadb.so.3 | 2 | mariadb, mysqlclient |
| libnvjpeg.so.12 | 2 | torchcodec, torchvision |
| libnvshmem_host.so.3 | 2 | deep-ep, pplx-kernels |
| libopenblaso.so.0 | 2 | ctranslate2, faiss-cpu |
| libpq.so.5 | 2 | psycopg-c, psycopg2 |
| libswresample.so.4 | 2 | av, torchcodec |
| libtinfo.so.6 | 2 | cmake, llvmlite |
| libunwind.so.8 | 2 | memray, ray |
| libxml2.so.2 | 2 | lxml, runai-model-streamer-azure |
| libzstd.so.1 | 2 | llvmlite, pyarrow |
| libaio.so.1 | 1 | nixl-cu12 |
| libcrypt.so.2 | 1 | ray-haproxy |
| libcudnn.so.9 | 1 | onnxruntime-gpu |
| libcufft.so.11 | 1 | onnxruntime-gpu |
| libcufile.so.0 | 1 | nixl-cu12 |
| libcurand.so.10 | 1 | onnxruntime-gpu |
| libdebuginfod.so.1 | 1 | memray |
| libeccodes.so.0.1 | 1 | pygrib |
| libev.so.4 | 1 | cassandra-driver |
| libexslt.so.0 | 1 | lxml |
| libgeos_c.so.1 | 1 | shapely |
| libgfortran.so.5 | 1 | scipy |
| libgmp.so.10 | 1 | pandoc-rhai |
| libhdf5.so.310 | 1 | h5py |
| libhdf5_hl.so.310 | 1 | h5py |
| libk5crypto.so.3 | 1 | krb5 |
| libkrb5.so.3 | 1 | krb5 |
| liblept.so.5 | 1 | tesserocr |
| libloguru.so.2 | 1 | docling-parse |
| libnccl.so.2 | 1 | deep-ep |
| libncurses.so.6 | 1 | cmake |
| libnetcdf.so.19 | 1 | netcdf4 |
| libodbc.so.2 | 1 | pyodbc |
| libpcre2-8.so.0 | 1 | ray-haproxy |
| libpcre2-posix.so.3 | 1 | ray-haproxy |
| libproj.so.25 | 1 | pyproj |
| libsnappy.so.1 | 1 | pyarrow |
| libtbb.so.2 | 1 | prophet |
| libtesseract.so.4 | 1 | tesserocr |
| libthrift-0.24.0.so | 1 | pyarrow |
| libucp.so.0 | 1 | nixl-cu12 |
| libucs.so.0 | 1 | nixl-cu12 |
| libutf8proc.so.2 | 1 | pyarrow |
| libuuid.so.1 | 1 | coremltools |
| libxslt.so.1 | 1 | lxml |
| libz3.so | 1 | tilelang |
| libzip.so.5 | 1 | tacozip |
| libzmq.so.5 | 1 | pyzmq |

86 unique libraries across 263 project references

## Inter-wheel Dependencies

| Library | Provided by | Required by |
|:---|:---|:---|
| libtvm_ffi.so | apache-tvm-ffi | tilelang, xgrammar |
| libz3.so.4.15 | z3-solver | tilelang |

2 shared libraries provided by wheels and used by other wheels

## Dependency Complexity

### Manylinux-only (190 packages)

These packages only depend on manylinux baseline libraries
and/or libraries provided by other wheels in the index.

aiohttp, aiokafka, annoy, apache-tvm-ffi, argon2-cffi-bindings, array-record, ast-serialize, asyncmy, asyncpg, backports-zstd, base2048, bcrypt, biotite, biotraj, blake3, blis, brotli, cachebox, caio, cbor2, cftime, chromadb, clarabel, clickhouse-connect, cmarkgfm, contourpy, coverage, cuda-bindings, cuda-core, cuda-tile, cvxpy, cymem, cysignals, cython, debugpy, dm-tree, duckdb, dumb-init, eval-hub-server, fastar, fastavro, fastsafetensors, fasttext-predict, fastuuid, frozenlist, gevent, geventhttpclient, goodpoints, google-re2, greenlet, grpcio-tools, hf-transfer, hf-xet, highspy, hiredis, hnswlib, httptools, instanttensor, jaxlib, jiter, jpype1, jsonnet, jsonpath-rust-bindings, kernels, kernels-data, kiwisolver, kornia-rs, lancedb, lapx, lazy-object-proxy, libcst, librt, lintrunner, llguidance, markupsafe, matplotlib, minify-html, ml-dtypes, mmh3, modelexpress, msgpack, msgspec, multidict, murmurhash, nccl4py, nh3, numcodecs, numexpr, nvidia-cudnn-frontend, nvtx, obstore, onnx, onnxsim, openai-harmony, openalgo, openshell, optree, oracledb, orjson, ormsgpack, osqp, outlines-core, pandas, patchelf, peewee, pendulum, phik, pinecone, polars, posix-ipc, preshed, propcache, protobuf, psutil, pulp, py-rust-stemmers, py-spy, pybase64, pyclipper, pycocotools, pycrdt, pycryptodome, pycryptodomex, pydantic-core, pydantic-monty-client, pydantic-monty-runtime, pymongo, pynacl, pysqlite3, python-rapidjson, pytokens, pywavelets, pyzstd, qdldl, rapidfuzz, regex, rignore, ripgrep, river, rpds-py, ruff, runai-model-streamer, runai-model-streamer-gcs, rustworkx, safetensors, scikit-image, sentencepiece, setproctitle, shap, simplejson, snowflake-connector-python, soxr, spacy, speechrecognition, sqlalchemy, srsly, statsmodels, stringzilla, tensorboard-data-server, tensordict, tensorflow, tensorstore, thinc, thriftpy2, tiktoken, tlparse, tokenizers, tornado, tree-sitter, tree-sitter-c, tree-sitter-javascript, tree-sitter-languages, tree-sitter-python, tree-sitter-typescript, triton, ujson, uuid-utils, uvloop, wandb, watchfiles, wcwidth, websockets, wordcloud, wrapt, xgrammar, xxhash, yarl, z3-solver, zope-interface, zstandard

### Could become manylinux by bundling (10 packages)

All external deps are vendorable -- bundling them would make
these wheels manylinux-compatible.

| Package | Libraries |
|:---|:---|
| cassandra-driver | libev.so.4 |
| mariadb | libmariadb.so.3 |
| mysqlclient | libmariadb.so.3 |
| onnxruntime | libre2.so.9 |
| prophet | libtbb.so.2 |
| psycopg-c | libpq.so.5 |
| psycopg2 | libpq.so.5 |
| pygrib | libeccodes.so.0.1 |
| pyzmq | libzmq.so.5 |
| tacozip | libzip.so.5 |

### AI accelerator-specific (19 packages)

Depend on CUDA, ROCm, or PyTorch runtime libraries.
These must be provided by the accelerator platform.

| Package | Additional libraries |
|:---|:---|
| bitsandbytes | libcublas.so.12, libcublasLt.so.12, libcudart.so.12, libgomp.so.1 |
| causal-conv1d | libc10.so, libc10_cuda.so, libcudart.so.12, libtorch_cpu.so, libtorch_python.so |
| deep-ep | libc10.so, libc10_cuda.so, libcudart.so.12, libnccl.so.2, libnvshmem_host.so.3, libtorch_cpu.so, libtorch_python.so |
| deep-gemm | libc10.so, libc10_cuda.so, libcudart.so.12, libnvrtc.so.12, libtorch_cpu.so, libtorch_cuda.so, libtorch_python.so |
| detectron2 | libc10.so, libc10_cuda.so, libcudart.so.12, libtorch_cpu.so, libtorch_python.so |
| faiss-cpu | libcublas.so.12, libcublasLt.so.12, libcudart.so.12, libgomp.so.1, libopenblaso.so.0 |
| flash-attn | libc10.so, libc10_cuda.so, libcudart.so.12, libtorch_cpu.so, libtorch_cuda.so, libtorch_python.so |
| flashinfer-jit-cache | libcublas.so.12, libcublasLt.so.12, libcuda.so.1, libcudart.so.12, libnvrtc.so.12 |
| kvcached | libc10.so, libcuda.so.1, libcudart.so.12, libtorch_cpu.so, libtorch_python.so |
| mamba-ssm | libc10.so, libc10_cuda.so, libcudart.so.12, libtorch_cpu.so, libtorch_python.so |
| nixl-cu12 | libaio.so.1, libcudart.so.12, libcufile.so.0, libucp.so.0, libucs.so.0 |
| onnxruntime-gpu | libcublas.so.12, libcublasLt.so.12, libcudart.so.12, libcudnn.so.9, libcufft.so.11, libcurand.so.10, libre2.so.9 |
| pplx-kernels | libc10.so, libc10_cuda.so, libcuda.so.1, libcudart.so.12, libnvshmem_host.so.3, libtorch.so, libtorch_cpu.so, libtorch_cuda.so |
| pyarrow | libbz2.so.1, libcrypto.so.3, libcuda.so.1, libcurl.so.4, liblz4.so.1, libre2.so.9, libsnappy.so.1, libssl.so.3, libthrift-0.24.0.so, libutf8proc.so.2, libzstd.so.1 |
| torchao | libcudart.so.12, libtorch_cpu.so, libtorch_cuda.so |
| torchaudio | libcudart.so.12, libtorch_cpu.so, libtorch_cuda.so |
| torchcodec | libavcodec.so.60, libavdevice.so.60, libavfilter.so.9, libavformat.so.60, libavutil.so.58, libc10.so, libc10_cuda.so, libcudart.so.12, libjpeg.so.62, libnvjpeg.so.12, libnvrtc.so.12, libpng16.so.16, libswresample.so.4, libswscale.so.7, libtorch.so, libtorch_cpu.so, libtorch_cuda.so |
| torchvision | libc10.so, libc10_cuda.so, libcudart.so.12, libjpeg.so.62, libnvjpeg.so.12, libpng16.so.16, libtorch_cpu.so, libtorch_cuda.so, libwebp.so.7 |
| vllm | libc10.so, libc10_cuda.so, libcuda.so.1, libcudart.so.12, libnvrtc.so.12, libtorch.so, libtorch_cpu.so, libtorch_cuda.so, libtorch_python.so |

### Unbundleable external dependencies (51 packages)

At least one external dep must never be bundled (crypto,
system runtime, etc.) and must be provided by the platform.
This includes indirect dependencies (e.g. libmariadb depends
on OpenSSL, libpq depends on OpenSSL + Kerberos).

| Package | Libraries |
|:---|:---|
| av | libavcodec.so.60, libavdevice.so.60, libavfilter.so.9, libavformat.so.60, libavutil.so.58, libswresample.so.4, libswscale.so.7 |
| c2pa-python | libcrypto.so.3, libssl.so.3 |
| cffi | libffi.so.8 |
| cmake | libcrypto.so.3, libncurses.so.6, libssl.so.3, libtinfo.so.6 |
| cryptography | libcrypto.so.3, libssl.so.3 |
| ctranslate2 | libgomp.so.1, libopenblaso.so.0 |
| daft | libbz2.so.1 |
| docling-parse | libfreetype.so.6, libjpeg.so.62, liblcms2.so.2, libopenjp2.so.7 (+ libloguru.so.2) |
| grpcio | libcrypto.so.3, libssl.so.3 (+ libre2.so.9) |
| gssapi | libgssapi_krb5.so.2 |
| h5py | libhdf5.so.310, libhdf5_hl.so.310 |
| krb5 | libk5crypto.so.3, libkrb5.so.3 |
| lightgbm | libgomp.so.1 |
| llvmlite | libtinfo.so.6, libzstd.so.1 |
| lxml | libexslt.so.0, libxml2.so.2, libxslt.so.1 |
| lz4 | liblz4.so.1 |
| maturin | libcrypto.so.3, liblzma.so.5, libssl.so.3 |
| memray | libdebuginfod.so.1, liblz4.so.1, libunwind.so.8 |
| netcdf4 | libnetcdf.so.19 |
| numba | libgomp.so.1 |
| numpy | libopenblasp.so.0 |
| opencv-python | libavcodec.so.60, libavdevice.so.60, libavformat.so.60, libavutil.so.58, libjpeg.so.62, libopenblasp.so.0, libopenjp2.so.7, libpng16.so.16, libswscale.so.7, libtiff.so.5, libwebp.so.7, libwebpdemux.so.2, libwebpmux.so.3 |
| opencv-python-headless | libavcodec.so.60, libavformat.so.60, libavutil.so.58, libjpeg.so.62, libopenblasp.so.0, libopenjp2.so.7, libpng16.so.16, libswscale.so.7, libtiff.so.5, libwebp.so.7, libwebpdemux.so.2, libwebpmux.so.3 |
| pandoc-rhai | libffi.so.8, libgmp.so.10 |
| pennylane-lightning | libgomp.so.1 |
| pillow | libfreetype.so.6, libjpeg.so.62, liblcms2.so.2, libopenjp2.so.7, libtiff.so.5, libwebp.so.7, libwebpdemux.so.2, libwebpmux.so.3 |
| pymssql | libcrypto.so.3, libgssapi_krb5.so.2, libssl.so.3 |
| pyodbc | libodbc.so.2 |
| pyogrio | libgdal.so.36 |
| pyproj | libproj.so.25 |
| python-libsbml | libbz2.so.1 |
| rasterio | libgdal.so.36 |
| ray | libunwind.so.8 |
| ray-haproxy | libcrypt.so.2, libcrypto.so.3, libssl.so.3 (+ libpcre2-8.so.0, libpcre2-posix.so.3) |
| rfc3161-client | libcrypto.so.3, libssl.so.3 |
| runai-model-streamer-azure | libcrypto.so.3, libcurl.so.4, libssl.so.3, libxml2.so.2 |
| runai-model-streamer-s3 | libcrypto.so.3, libcurl.so.4, libssl.so.3 |
| sccache | libcrypto.so.3, libssl.so.3 |
| scikit-learn | libgomp.so.1 |
| scikit-network | libgomp.so.1 |
| scipy | libgfortran.so.5, libopenblasp.so.0 |
| scs | libopenblasp.so.0 |
| selenium | libbz2.so.1 |
| shapely | libgeos_c.so.1 |
| simsimd | libgomp.so.1 |
| sparsediffpy | libopenblasp.so.0 |
| tesserocr | liblept.so.5, libtesseract.so.4 |
| uv | libbz2.so.1 |
| uv-build | libbz2.so.1, liblzma.so.5 |
| xgboost | libgomp.so.1 |
| yara-python | libcrypto.so.3 |

### Undecided external dependencies (1 packages)

All external deps are known but not yet classified as
bundleable or unbundleable.

| Package | Libraries |
|:---|:---|
| tilelang | libz3.so |

### Unknown external dependencies (1 packages)

External deps not present in any classification list.

| Package | Count | Libraries |
|:---|---:|:---|
| coremltools | 1 | libuuid.so.1 |

**Total:** 272 packages with ELF dependencies (190 manylinux-only, 10 bundleable, 19 accelerator, 51 unbundleable, 1 undecided, 1 unknown)

## Packages without ELF Data (10)

Platlib packages that ship platform-specific wheels but have no
fromager-elf-requires/provides metadata. These are typically
pre-built upstream wheels, proprietary binary blobs, packages
with optional C extensions, or packages built without fromager
instrumentation.

**Pre-built manylinux (4):** nvidia-cutlass-dsl-libs-base, nvidia-cutlass-dsl-libs-cu12, nvidia-cutlass-dsl-libs-cu13, soundfile

**Other (6):** dulwich, frozendict, mysql-connector-python, pyyaml, rtree, torch

