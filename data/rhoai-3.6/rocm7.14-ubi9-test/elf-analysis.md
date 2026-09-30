# ELF Analysis: rocm7.14-ubi9-test

## Summary

| Category | Count | % |
|:---|---:|---:|
| **Total packages** | **1539** |  |
| &ensp;Purelib (pure Python) | 1273 | 82.7% |
| &ensp;Platlib (native code) | 266 | 17.3% |
| &ensp;Manylinux + bundleable | 198 | 12.9% |
| &ensp;&ensp;Manylinux-only | 185 | 12.0% |
| &ensp;&ensp;Could be bundled | 12 | 0.8% |
| &ensp;&ensp;Pre-built (manylinux) | 1 | 0.1% |
| &ensp;Platform-dependent | 67 | 4.4% |
| &ensp;&ensp;Accelerator-specific | 16 | 1.0% |
| &ensp;&ensp;Unbundleable | 50 | 3.2% |
| &ensp;&ensp;Undecided | 0 | 0.0% |
| &ensp;&ensp;Unknown | 1 | 0.1% |
| &ensp;No ELF data (other) | 4 | 0.3% |
| **Purelib + manylinux + bundleable** | **1471** | **95.6%** |
| **Platform/accel + other** | **68** | **4.4%** |

## Charts

```mermaid
%%{init: {"theme": "base", "themeVariables": {"xyChart": {"plotColorPalette": "#0072B2, #009E73, #D55E00, #999999"}}}}%%
xychart-beta
    title "rocm7.14-ubi9-test -- package overview"
    x-axis ["purelib", "manylinux + bundleable", "platform/accel", "no ELF data (other)"]
    y-axis "Packages"
    bar [1273, 198, 67, 4]
```

## External Dependencies

| Library | Count | Projects |
|:---|---:|:---|
| libcrypto.so.3 | 12 | c2pa-python, cmake, cryptography, grpcio, maturin, pyarrow, pymssql, ray-haproxy, runai-model-streamer-azure, runai-model-streamer-s3, sccache, yara-python |
| libssl.so.3 | 11 | c2pa-python, cmake, cryptography, grpcio, maturin, pyarrow, pymssql, ray-haproxy, runai-model-streamer-azure, runai-model-streamer-s3, sccache |
| libamdhip64.so.7 | 10 | amd-aiter, aotriton, ctranslate2, detectron2, flash-attn, flydsl, tensorflow-rocm, torch, torchvision, vllm |
| libgomp.so.1 | 10 | bitsandbytes, faiss-cpu, lightgbm, numba, pennylane-lightning, scikit-learn, scikit-network, simsimd, torch, xgboost |
| libjpeg.so.62 | 6 | docling-parse, opencv-python, opencv-python-headless, pillow, torchcodec, torchvision |
| libopenblasp.so.0 | 6 | numpy, opencv-python, opencv-python-headless, scipy, scs, sparsediffpy |
| libbz2.so.1 | 5 | pyarrow, python-libsbml, selenium, uv, uv-build |
| libavcodec.so.60 | 4 | av, opencv-python, opencv-python-headless, torchcodec |
| libavformat.so.60 | 4 | av, opencv-python, opencv-python-headless, torchcodec |
| libavutil.so.58 | 4 | av, opencv-python, opencv-python-headless, torchcodec |
| libhipblas.so.3 | 4 | bitsandbytes, ctranslate2, torch, vllm |
| liblzma.so.5 | 4 | aotriton, maturin, torch, uv-build |
| libopenjp2.so.7 | 4 | docling-parse, opencv-python, opencv-python-headless, pillow |
| libpng16.so.16 | 4 | opencv-python, opencv-python-headless, torchcodec, torchvision |
| libre2.so.9 | 4 | grpcio, onnxruntime, onnxruntime-migraphx, pyarrow |
| librocrand.so.1 | 4 | bitsandbytes, torch, torchcodec, vllm |
| libswscale.so.7 | 4 | av, opencv-python, opencv-python-headless, torchcodec |
| libwebp.so.7 | 4 | opencv-python, opencv-python-headless, pillow, torchvision |
| libavdevice.so.60 | 3 | av, opencv-python, torchcodec |
| libcurl.so.4 | 3 | pyarrow, runai-model-streamer-azure, runai-model-streamer-s3 |
| libhiprand.so.1 | 3 | bitsandbytes, ctranslate2, torch |
| libhsa-runtime64.so.1 | 3 | tensorflow-rocm, tilelang, torch |
| liblz4.so.1 | 3 | lz4, memray, pyarrow |
| libopenblaso.so.0 | 3 | ctranslate2, faiss-cpu, torch |
| librocm_smi64.so.1 | 3 | tensorflow-rocm, torch, vllm |
| librocsolver.so.0 | 3 | tensorflow-rocm, torch, torchcodec |
| libtiff.so.5 | 3 | opencv-python, opencv-python-headless, pillow |
| libwebpdemux.so.2 | 3 | opencv-python, opencv-python-headless, pillow |
| libwebpmux.so.3 | 3 | opencv-python, opencv-python-headless, pillow |
| libavfilter.so.9 | 2 | av, torchcodec |
| libffi.so.8 | 2 | cffi, pandoc-rhai |
| libfreetype.so.6 | 2 | docling-parse, pillow |
| libgdal.so.36 | 2 | pyogrio, rasterio |
| libgssapi_krb5.so.2 | 2 | gssapi, pymssql |
| libhipblaslt.so.1 | 2 | bitsandbytes, torch |
| libhipfft.so.0 | 2 | tensorflow-rocm, torch |
| libhipsolver.so.1 | 2 | tensorflow-rocm, torch |
| libhipsparse.so.4 | 2 | tensorflow-rocm, torch |
| libhipsparselt.so.0 | 2 | tensorflow-rocm, torch |
| liblcms2.so.2 | 2 | docling-parse, pillow |
| libmariadb.so.3 | 2 | mariadb, mysqlclient |
| libnuma.so.1 | 2 | tensorflow-rocm, torch |
| libpq.so.5 | 2 | psycopg-c, psycopg2 |
| librccl.so.1 | 2 | tensorflow-rocm, torch |
| libswresample.so.4 | 2 | av, torchcodec |
| libtinfo.so.6 | 2 | cmake, llvmlite |
| libunwind.so.8 | 2 | memray, ray |
| libxml2.so.2 | 2 | lxml, runai-model-streamer-azure |
| libzstd.so.1 | 2 | llvmlite, pyarrow |
| libMIOpen.so.1 | 1 | torch |
| libamd_comgr.so.3 | 1 | tensorflow-rocm |
| libcrypt.so.2 | 1 | ray-haproxy |
| libdebuginfod.so.1 | 1 | memray |
| libeccodes.so.0.1 | 1 | pygrib |
| libev.so.4 | 1 | cassandra-driver |
| libexslt.so.0 | 1 | lxml |
| libgeos_c.so.1 | 1 | shapely |
| libgfortran.so.5 | 1 | scipy |
| libgmp.so.10 | 1 | pandoc-rhai |
| libhdf5.so.310 | 1 | h5py |
| libhdf5_hl.so.310 | 1 | h5py |
| libhipfftw.so.0 | 1 | tensorflow-rocm |
| libhiprtc.so.7 | 1 | torch |
| libk5crypto.so.3 | 1 | krb5 |
| libkrb5.so.3 | 1 | krb5 |
| liblept.so.5 | 1 | tesserocr |
| libloguru.so.2 | 1 | docling-parse |
| libmpi.so.40 | 1 | torch |
| libmpi_cxx.so.40 | 1 | torch |
| libncurses.so.6 | 1 | cmake |
| libnetcdf.so.19 | 1 | netcdf4 |
| libodbc.so.2 | 1 | pyodbc |
| libomp.so | 1 | ctranslate2 |
| libpcre2-8.so.0 | 1 | ray-haproxy |
| libpcre2-posix.so.3 | 1 | ray-haproxy |
| libproj.so.25 | 1 | pyproj |
| librocblas.so.5 | 1 | torch |
| librocprofiler-register.so.0 | 1 | tensorflow-rocm |
| librocprofiler-sdk.so.1 | 1 | torch |
| libroctx64.so.4 | 1 | torch |
| libsnappy.so.1 | 1 | pyarrow |
| libtbb.so.2 | 1 | prophet |
| libtesseract.so.4 | 1 | tesserocr |
| libthrift-0.24.0.so | 1 | pyarrow |
| libutf8proc.so.2 | 1 | pyarrow |
| libuuid.so.1 | 1 | coremltools |
| libxslt.so.1 | 1 | lxml |
| libyaml-0.so.2 | 1 | pyyaml |
| libzip.so.5 | 1 | tacozip |
| libzmq.so.5 | 1 | pyzmq |

90 unique libraries across 218 project references

## Inter-wheel Dependencies

| Library | Provided by | Required by |
|:---|:---|:---|
| libc10.so | torch | amd-aiter, amd-quark, detectron2, flash-attn, torchao, torchaudio, torchcodec, torchvision, vllm |
| libc10_hip.so | torch | amd-aiter, detectron2, flash-attn, torchao, torchvision, vllm |
| libtorch.so | torch | amd-aiter, detectron2, torchcodec, vllm |
| libtorch_cpu.so | torch | amd-aiter, amd-quark, detectron2, flash-attn, torchao, torchaudio, torchcodec, torchvision, vllm |
| libtorch_hip.so | torch | amd-aiter, flash-attn, torchao, torchcodec, torchvision, vllm |
| libtorch_python.so | torch | amd-aiter, detectron2, flash-attn |
| libtvm_ffi.so | apache-tvm-ffi | tilelang, xgrammar |
| libz3.so.4.15 | z3-solver | tilelang |

8 shared libraries provided by wheels and used by other wheels

## Dependency Complexity

### Manylinux-only (185 packages)

These packages only depend on manylinux baseline libraries
and/or libraries provided by other wheels in the index.

aiohttp, aiokafka, annoy, apache-tvm-ffi, argon2-cffi-bindings, array-record, ast-serialize, asyncmy, asyncpg, backports-zstd, base2048, bcrypt, biotite, biotraj, blake3, blis, brotli, cachebox, caio, cartopy, cbor2, cftime, chromadb, clarabel, clickhouse-connect, contourpy, coverage, cvxpy, cymem, cysignals, cython, debugpy, dm-tree, duckdb, dumb-init, eval-hub-server, fastar, fastavro, fastsafetensors, fasttext-predict, fastuuid, frozenlist, gevent, geventhttpclient, goodpoints, google-re2, greenlet, grpcio-tools, hf-transfer, hf-xet, highspy, hiredis, hnswlib, httptools, instanttensor, jaxlib, jiter, jpype1, jsonnet, jsonpath-rust-bindings, kernels, kernels-data, kiwisolver, kornia-rs, lancedb, lapx, lazy-object-proxy, libcst, librt, lintrunner, llguidance, markupsafe, matplotlib, minify-html, ml-dtypes, mmh3, modelexpress, msgpack, msgspec, multidict, murmurhash, nh3, numcodecs, numexpr, nvtx, obstore, onnx, onnxsim, openai-harmony, openalgo, openshell, optree, oracledb, orjson, ormsgpack, osqp, outlines-core, pandas, patchelf, peewee, pendulum, phik, pinecone, polars, posix-ipc, preshed, propcache, protobuf, psutil, pulp, py-rust-stemmers, py-spy, pybase64, pyclipper, pycocotools, pycrdt, pycryptodome, pycryptodomex, pydantic-core, pydantic-monty-client, pydantic-monty-runtime, pymongo, pynacl, pysqlite3, python-rapidjson, pytokens, pywavelets, pyzstd, qdldl, rapidfuzz, regex, rfc3161-client, rignore, ripgrep, river, rpds-py, ruff, runai-model-streamer, runai-model-streamer-gcs, rustworkx, safetensors, scikit-image, sentencepiece, setproctitle, shap, simplejson, snowflake-connector-python, soxr, spacy, speechrecognition, sqlalchemy, srsly, statsmodels, stringzilla, tensorboard-data-server, tensordict, tensorstore, thinc, thriftpy2, tiktoken, tlparse, tokenizers, tornado, tree-sitter, tree-sitter-c, tree-sitter-javascript, tree-sitter-languages, tree-sitter-python, tree-sitter-typescript, triton, ujson, uuid-utils, uvloop, wandb, watchfiles, wcwidth, websockets, wordcloud, wrapt, xgrammar, xxhash, yarl, z3-solver, zope-interface, zstandard

### Could become manylinux by bundling (12 packages)

All external deps are vendorable -- bundling them would make
these wheels manylinux-compatible.

| Package | Libraries |
|:---|:---|
| cassandra-driver | libev.so.4 |
| mariadb | libmariadb.so.3 |
| mysqlclient | libmariadb.so.3 |
| onnxruntime | libre2.so.9 |
| onnxruntime-migraphx | libre2.so.9 |
| prophet | libtbb.so.2 |
| psycopg-c | libpq.so.5 |
| psycopg2 | libpq.so.5 |
| pygrib | libeccodes.so.0.1 |
| pyyaml | libyaml-0.so.2 |
| pyzmq | libzmq.so.5 |
| tacozip | libzip.so.5 |

### AI accelerator-specific (16 packages)

Depend on CUDA, ROCm, or PyTorch runtime libraries.
These must be provided by the accelerator platform.

| Package | Additional libraries |
|:---|:---|
| amd-aiter | libamdhip64.so.7 |
| amd-quark |  |
| aotriton | libamdhip64.so.7, liblzma.so.5 |
| bitsandbytes | libgomp.so.1, libhipblas.so.3, libhipblaslt.so.1, libhiprand.so.1, librocrand.so.1 |
| ctranslate2 | libamdhip64.so.7, libhipblas.so.3, libhiprand.so.1, libomp.so, libopenblaso.so.0 |
| detectron2 | libamdhip64.so.7 |
| flash-attn | libamdhip64.so.7 |
| flydsl | libamdhip64.so.7 |
| tensorflow-rocm | libamd_comgr.so.3, libamdhip64.so.7, libhipfft.so.0, libhipfftw.so.0, libhipsolver.so.1, libhipsparse.so.4, libhipsparselt.so.0, libhsa-runtime64.so.1, libnuma.so.1, librccl.so.1, librocm_smi64.so.1, librocprofiler-register.so.0, librocsolver.so.0 |
| tilelang | libhsa-runtime64.so.1 |
| torch | libMIOpen.so.1, libamdhip64.so.7, libgomp.so.1, libhipblas.so.3, libhipblaslt.so.1, libhipfft.so.0, libhiprand.so.1, libhiprtc.so.7, libhipsolver.so.1, libhipsparse.so.4, libhipsparselt.so.0, libhsa-runtime64.so.1, liblzma.so.5, libmpi.so.40, libmpi_cxx.so.40, libnuma.so.1, libopenblaso.so.0, librccl.so.1, librocblas.so.5, librocm_smi64.so.1, librocprofiler-sdk.so.1, librocrand.so.1, librocsolver.so.0, libroctx64.so.4 |
| torchao |  |
| torchaudio |  |
| torchcodec | libavcodec.so.60, libavdevice.so.60, libavfilter.so.9, libavformat.so.60, libavutil.so.58, libjpeg.so.62, libpng16.so.16, librocrand.so.1, librocsolver.so.0, libswresample.so.4, libswscale.so.7 |
| torchvision | libamdhip64.so.7, libjpeg.so.62, libpng16.so.16, libwebp.so.7 |
| vllm | libamdhip64.so.7, libhipblas.so.3, librocm_smi64.so.1, librocrand.so.1 |

### Unbundleable external dependencies (50 packages)

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
| docling-parse | libfreetype.so.6, libjpeg.so.62, liblcms2.so.2, libopenjp2.so.7 (+ libloguru.so.2) |
| faiss-cpu | libgomp.so.1, libopenblaso.so.0 |
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
| pyarrow | libbz2.so.1, libcrypto.so.3, libcurl.so.4, liblz4.so.1, libsnappy.so.1, libssl.so.3, libzstd.so.1 (+ libre2.so.9, libthrift-0.24.0.so, libutf8proc.so.2) |
| pymssql | libcrypto.so.3, libgssapi_krb5.so.2, libssl.so.3 |
| pyodbc | libodbc.so.2 |
| pyogrio | libgdal.so.36 |
| pyproj | libproj.so.25 |
| python-libsbml | libbz2.so.1 |
| rasterio | libgdal.so.36 |
| ray | libunwind.so.8 |
| ray-haproxy | libcrypt.so.2, libcrypto.so.3, libssl.so.3 (+ libpcre2-8.so.0, libpcre2-posix.so.3) |
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

### Unknown external dependencies (1 packages)

External deps not present in any classification list.

| Package | Count | Libraries |
|:---|---:|:---|
| coremltools | 1 | libuuid.so.1 |

**Total:** 264 packages with ELF dependencies (185 manylinux-only, 12 bundleable, 16 accelerator, 50 unbundleable, 0 undecided, 1 unknown)

## Packages without ELF Data (5)

Platlib packages that ship platform-specific wheels but have no
fromager-elf-requires/provides metadata. These are typically
pre-built upstream wheels, proprietary binary blobs, packages
with optional C extensions, or packages built without fromager
instrumentation.

**Pre-built manylinux (1):** soundfile

**Other (4):** dulwich, frozendict, mysql-connector-python, rtree

