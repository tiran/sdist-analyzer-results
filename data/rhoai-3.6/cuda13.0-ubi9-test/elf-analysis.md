# ELF Analysis: cuda13.0-ubi9-test

## Summary

| Category | Count | % |
|:---|---:|---:|
| **Total packages** | **1446** |  |
| &ensp;Purelib (pure Python) | 1201 | 83.1% |
| &ensp;Platlib (native code) | 245 | 16.9% |
| &ensp;Manylinux + bundleable | 176 | 12.2% |
| &ensp;&ensp;Manylinux-only | 163 | 11.3% |
| &ensp;&ensp;Could be bundled | 9 | 0.6% |
| &ensp;&ensp;Pre-built (manylinux) | 4 | 0.3% |
| &ensp;Platform-dependent | 57 | 3.9% |
| &ensp;&ensp;Accelerator-specific | 14 | 1.0% |
| &ensp;&ensp;Unbundleable | 42 | 2.9% |
| &ensp;&ensp;Undecided | 1 | 0.1% |
| &ensp;&ensp;Unknown | 0 | 0.0% |
| &ensp;No ELF data (other) | 14 | 1.0% |
| **Purelib + manylinux + bundleable** | **1377** | **95.2%** |
| **Platform/accel + other** | **69** | **4.8%** |

## Charts

```mermaid
%%{init: {"theme": "base", "themeVariables": {"xyChart": {"plotColorPalette": "#0072B2, #009E73, #D55E00, #999999"}}}}%%
xychart-beta
    title "cuda13.0-ubi9-test -- package overview"
    x-axis ["purelib", "manylinux + bundleable", "platform/accel", "no ELF data (other)"]
    y-axis "Packages"
    bar [1201, 176, 57, 14]
```

## External Dependencies

| Library | Count | Projects |
|:---|---:|:---|
| libcudart.so.13 | 13 | bitsandbytes, causal-conv1d, detectron2, faiss-cpu, flash-attn, kvcached, mamba-ssm, onnxruntime-gpu, torchao, torchaudio, torchcodec, torchvision, vllm |
| libtorch_cpu.so | 10 | causal-conv1d, detectron2, flash-attn, kvcached, mamba-ssm, torchao, torchaudio, torchcodec, torchvision, vllm |
| libgomp.so.1 | 9 | bitsandbytes, ctranslate2, faiss-cpu, lightgbm, numba, scikit-learn, scikit-network, simsimd, xgboost |
| libc10.so | 8 | causal-conv1d, detectron2, flash-attn, kvcached, mamba-ssm, torchcodec, torchvision, vllm |
| libc10_cuda.so | 7 | causal-conv1d, detectron2, flash-attn, mamba-ssm, torchcodec, torchvision, vllm |
| libcrypto.so.3 | 7 | cmake, cryptography, grpcio, pyarrow, pymssql, sccache, yara-python |
| libbz2.so.1 | 6 | daft, pyarrow, python-libsbml, selenium, uv, uv-build |
| libssl.so.3 | 6 | cmake, cryptography, grpcio, pyarrow, pymssql, sccache |
| libtorch_cuda.so | 6 | flash-attn, torchao, torchaudio, torchcodec, torchvision, vllm |
| libtorch_python.so | 6 | causal-conv1d, detectron2, flash-attn, kvcached, mamba-ssm, vllm |
| libjpeg.so.62 | 5 | docling-parse, opencv-python, opencv-python-headless, pillow, torchvision |
| libavcodec.so.60 | 4 | av, opencv-python, opencv-python-headless, torchcodec |
| libavformat.so.60 | 4 | av, opencv-python, opencv-python-headless, torchcodec |
| libavutil.so.58 | 4 | av, opencv-python, opencv-python-headless, torchcodec |
| libopenblasp.so.0 | 4 | numpy, opencv-python, opencv-python-headless, scipy |
| libopenjp2.so.7 | 4 | docling-parse, opencv-python, opencv-python-headless, pillow |
| libre2.so.9 | 4 | grpcio, onnxruntime, onnxruntime-gpu, pyarrow |
| libswscale.so.7 | 4 | av, opencv-python, opencv-python-headless, torchcodec |
| libwebp.so.7 | 4 | opencv-python, opencv-python-headless, pillow, torchvision |
| libavdevice.so.60 | 3 | av, opencv-python, torchcodec |
| libcublas.so.13 | 3 | bitsandbytes, faiss-cpu, onnxruntime-gpu |
| libcublasLt.so.13 | 3 | bitsandbytes, faiss-cpu, onnxruntime-gpu |
| libcuda.so.1 | 3 | kvcached, pyarrow, vllm |
| liblz4.so.1 | 3 | lz4, memray, pyarrow |
| libpng16.so.16 | 3 | opencv-python, opencv-python-headless, torchvision |
| libtiff.so.5 | 3 | opencv-python, opencv-python-headless, pillow |
| libwebpdemux.so.2 | 3 | opencv-python, opencv-python-headless, pillow |
| libwebpmux.so.3 | 3 | opencv-python, opencv-python-headless, pillow |
| libavfilter.so.9 | 2 | av, torchcodec |
| libffi.so.8 | 2 | cffi, pandoc-rhai |
| libfreetype.so.6 | 2 | docling-parse, pillow |
| libgdal.so.36 | 2 | pyogrio, rasterio |
| libgssapi_krb5.so.2 | 2 | gssapi, pymssql |
| liblcms2.so.2 | 2 | docling-parse, pillow |
| libmariadb.so.3 | 2 | mariadb, mysqlclient |
| libnvrtc.so.13 | 2 | torchcodec, vllm |
| libopenblaso.so.0 | 2 | ctranslate2, faiss-cpu |
| libswresample.so.4 | 2 | av, torchcodec |
| libtorch.so | 2 | torchcodec, vllm |
| libunwind.so.8 | 2 | memray, ray |
| libzstd.so.1 | 2 | llvmlite, pyarrow |
| libcudnn.so.9 | 1 | onnxruntime-gpu |
| libcufft.so.12 | 1 | onnxruntime-gpu |
| libcurand.so.10 | 1 | onnxruntime-gpu |
| libcurl.so.4 | 1 | pyarrow |
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
| liblzma.so.5 | 1 | uv-build |
| libncurses.so.6 | 1 | cmake |
| libnetcdf.so.19 | 1 | netcdf4 |
| libnvjpeg.so.13 | 1 | torchvision |
| libodbc.so.2 | 1 | pyodbc |
| libpq.so.5 | 1 | psycopg2 |
| libproj.so.25 | 1 | pyproj |
| libpython3.12.so.1.0 | 1 | torchcodec |
| libsnappy.so.1 | 1 | pyarrow |
| libtbb.so.2 | 1 | prophet |
| libtesseract.so.4 | 1 | tesserocr |
| libthrift-0.24.0.so | 1 | pyarrow |
| libtinfo.so.6 | 1 | cmake |
| libutf8proc.so.2 | 1 | pyarrow |
| libxml2.so.2 | 1 | lxml |
| libxslt.so.1 | 1 | lxml |
| libz3.so | 1 | tilelang |
| libzip.so.5 | 1 | tacozip |
| libzmq.so.5 | 1 | pyzmq |

77 unique libraries across 204 project references

## Inter-wheel Dependencies

| Library | Provided by | Required by |
|:---|:---|:---|
| libtvm_ffi.so | apache-tvm-ffi | tilelang, xgrammar |
| libz3.so.4.15 | z3-solver | tilelang |

2 shared libraries provided by wheels and used by other wheels

## Dependency Complexity

### Manylinux-only (163 packages)

These packages only depend on manylinux baseline libraries
and/or libraries provided by other wheels in the index.

aiohttp, aiokafka, annoy, apache-tvm-ffi, argon2-cffi-bindings, array-record, ast-serialize, asyncmy, asyncpg, backports-zstd, base2048, bcrypt, biotite, biotraj, blake3, blis, brotli, cachebox, caio, cbor2, cftime, chromadb, clickhouse-connect, contourpy, coverage, cuda-bindings, cuda-tile, cymem, cysignals, cython, debugpy, dm-tree, duckdb, fastar, fastavro, fastsafetensors, fasttext-predict, fastuuid, frozenlist, gevent, geventhttpclient, goodpoints, google-re2, greenlet, grpcio-tools, hf-transfer, hf-xet, hiredis, hnswlib, httptools, jiter, jpype1, kernels-data, kiwisolver, kornia-rs, lancedb, lapx, lazy-object-proxy, libcst, librt, llguidance, markupsafe, matplotlib, maturin, minify-html, ml-dtypes, mmh3, msgpack, msgspec, multidict, murmurhash, nh3, numcodecs, numexpr, nvidia-cudnn-frontend, nvtx, obstore, onnx, openai-harmony, openalgo, openshell, optree, oracledb, orjson, ormsgpack, outlines-core, pandas, patchelf, peewee, pendulum, phik, pinecone, polars, posix-ipc, preshed, propcache, protobuf, psutil, py-rust-stemmers, py-spy, pybase64, pyclipper, pycocotools, pycrdt, pycryptodome, pycryptodomex, pydantic-core, pydantic-monty-client, pydantic-monty-runtime, pymongo, pynacl, pysqlite3, python-rapidjson, pytokens, pywavelets, rapidfuzz, regex, rfc3161-client, rignore, ripgrep, river, rpds-py, ruff, runai-model-streamer, safetensors, scikit-image, sentencepiece, setproctitle, shap, snowflake-connector-python, soxr, spacy, speechrecognition, sqlalchemy, srsly, statsmodels, stringzilla, tensordict, thinc, tiktoken, tokenizers, tornado, tree-sitter, tree-sitter-c, tree-sitter-javascript, tree-sitter-languages, tree-sitter-python, tree-sitter-typescript, triton, ujson, uuid-utils, uvloop, wandb, watchfiles, websockets, wordcloud, wrapt, xgrammar, xxhash, yarl, z3-solver, zope-interface, zstandard

### Could become manylinux by bundling (9 packages)

All external deps are vendorable -- bundling them would make
these wheels manylinux-compatible.

| Package | Libraries |
|:---|:---|
| cassandra-driver | libev.so.4 |
| mariadb | libmariadb.so.3 |
| mysqlclient | libmariadb.so.3 |
| onnxruntime | libre2.so.9 |
| prophet | libtbb.so.2 |
| psycopg2 | libpq.so.5 |
| pygrib | libeccodes.so.0.1 |
| pyzmq | libzmq.so.5 |
| tacozip | libzip.so.5 |

### AI accelerator-specific (14 packages)

Depend on CUDA, ROCm, or PyTorch runtime libraries.
These must be provided by the accelerator platform.

| Package | Additional libraries |
|:---|:---|
| bitsandbytes | libcublas.so.13, libcublasLt.so.13, libcudart.so.13, libgomp.so.1 |
| causal-conv1d | libc10.so, libc10_cuda.so, libcudart.so.13, libtorch_cpu.so, libtorch_python.so |
| detectron2 | libc10.so, libc10_cuda.so, libcudart.so.13, libtorch_cpu.so, libtorch_python.so |
| faiss-cpu | libcublas.so.13, libcublasLt.so.13, libcudart.so.13, libgomp.so.1, libopenblaso.so.0 |
| flash-attn | libc10.so, libc10_cuda.so, libcudart.so.13, libtorch_cpu.so, libtorch_cuda.so, libtorch_python.so |
| kvcached | libc10.so, libcuda.so.1, libcudart.so.13, libtorch_cpu.so, libtorch_python.so |
| mamba-ssm | libc10.so, libc10_cuda.so, libcudart.so.13, libtorch_cpu.so, libtorch_python.so |
| onnxruntime-gpu | libcublas.so.13, libcublasLt.so.13, libcudart.so.13, libcudnn.so.9, libcufft.so.12, libcurand.so.10, libre2.so.9 |
| pyarrow | libbz2.so.1, libcrypto.so.3, libcuda.so.1, libcurl.so.4, liblz4.so.1, libre2.so.9, libsnappy.so.1, libssl.so.3, libthrift-0.24.0.so, libutf8proc.so.2, libzstd.so.1 |
| torchao | libcudart.so.13, libtorch_cpu.so, libtorch_cuda.so |
| torchaudio | libcudart.so.13, libtorch_cpu.so, libtorch_cuda.so |
| torchcodec | libavcodec.so.60, libavdevice.so.60, libavfilter.so.9, libavformat.so.60, libavutil.so.58, libc10.so, libc10_cuda.so, libcudart.so.13, libnvrtc.so.13, libpython3.12.so.1.0, libswresample.so.4, libswscale.so.7, libtorch.so, libtorch_cpu.so, libtorch_cuda.so |
| torchvision | libc10.so, libc10_cuda.so, libcudart.so.13, libjpeg.so.62, libnvjpeg.so.13, libpng16.so.16, libtorch_cpu.so, libtorch_cuda.so, libwebp.so.7 |
| vllm | libc10.so, libc10_cuda.so, libcuda.so.1, libcudart.so.13, libnvrtc.so.13, libtorch.so, libtorch_cpu.so, libtorch_cuda.so, libtorch_python.so |

### Unbundleable external dependencies (42 packages)

At least one external dep must never be bundled (crypto,
system runtime, etc.) and must be provided by the platform.
This includes indirect dependencies (e.g. libmariadb depends
on OpenSSL, libpq depends on OpenSSL + Kerberos).

| Package | Libraries |
|:---|:---|
| av | libavcodec.so.60, libavdevice.so.60, libavfilter.so.9, libavformat.so.60, libavutil.so.58, libswresample.so.4, libswscale.so.7 |
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
| llvmlite | libzstd.so.1 |
| lxml | libexslt.so.0, libxml2.so.2, libxslt.so.1 |
| lz4 | liblz4.so.1 |
| memray | libdebuginfod.so.1, liblz4.so.1, libunwind.so.8 |
| netcdf4 | libnetcdf.so.19 |
| numba | libgomp.so.1 |
| numpy | libopenblasp.so.0 |
| opencv-python | libavcodec.so.60, libavdevice.so.60, libavformat.so.60, libavutil.so.58, libjpeg.so.62, libopenblasp.so.0, libopenjp2.so.7, libpng16.so.16, libswscale.so.7, libtiff.so.5, libwebp.so.7, libwebpdemux.so.2, libwebpmux.so.3 |
| opencv-python-headless | libavcodec.so.60, libavformat.so.60, libavutil.so.58, libjpeg.so.62, libopenblasp.so.0, libopenjp2.so.7, libpng16.so.16, libswscale.so.7, libtiff.so.5, libwebp.so.7, libwebpdemux.so.2, libwebpmux.so.3 |
| pandoc-rhai | libffi.so.8, libgmp.so.10 |
| pillow | libfreetype.so.6, libjpeg.so.62, liblcms2.so.2, libopenjp2.so.7, libtiff.so.5, libwebp.so.7, libwebpdemux.so.2, libwebpmux.so.3 |
| pymssql | libcrypto.so.3, libgssapi_krb5.so.2, libssl.so.3 |
| pyodbc | libodbc.so.2 |
| pyogrio | libgdal.so.36 |
| pyproj | libproj.so.25 |
| python-libsbml | libbz2.so.1 |
| rasterio | libgdal.so.36 |
| ray | libunwind.so.8 |
| sccache | libcrypto.so.3, libssl.so.3 |
| scikit-learn | libgomp.so.1 |
| scikit-network | libgomp.so.1 |
| scipy | libgfortran.so.5, libopenblasp.so.0 |
| selenium | libbz2.so.1 |
| shapely | libgeos_c.so.1 |
| simsimd | libgomp.so.1 |
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

**Total:** 229 packages with ELF dependencies (163 manylinux-only, 9 bundleable, 14 accelerator, 42 unbundleable, 1 undecided, 0 unknown)

## Packages without ELF Data (18)

Platlib packages that ship platform-specific wheels but have no
fromager-elf-requires/provides metadata. These are typically
pre-built upstream wheels, proprietary binary blobs, packages
with optional C extensions, or packages built without fromager
instrumentation.

**Pre-built manylinux (4):** flashinfer-jit-cache, nvidia-cutlass-dsl-libs-base, nvidia-cutlass-dsl-libs-cu13, soundfile

**Other (14):** cartopy, cupy-cuda13x, deep-ep, deep-gemm, dulwich, eval-hub-server, frozendict, mysql-connector-python, nixl-cu13, pplx-kernels, pyyaml, rtree, torch, xformers

