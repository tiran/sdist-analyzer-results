# ELF Analysis: combined

## Summary

| Category | Count | % |
|:---|---:|---:|
| **Total packages** | **1417** |  |
| &ensp;Purelib (pure Python) | 1188 | 83.8% |
| &ensp;Platlib (native code) | 229 | 16.2% |
| &ensp;Manylinux + bundleable | 120 | 8.5% |
| &ensp;&ensp;Manylinux-only | 110 | 7.8% |
| &ensp;&ensp;Could be bundled | 7 | 0.5% |
| &ensp;&ensp;Pre-built (manylinux) | 3 | 0.2% |
| &ensp;Platform-dependent | 32 | 2.3% |
| &ensp;&ensp;Accelerator-specific | 1 | 0.1% |
| &ensp;&ensp;Unbundleable | 31 | 2.2% |
| &ensp;&ensp;Undecided | 0 | 0.0% |
| &ensp;&ensp;Unknown | 0 | 0.0% |
| &ensp;No ELF data (other) | 77 | 5.4% |
| **Purelib + manylinux + bundleable** | **1308** | **92.3%** |
| **Platform/accel + other** | **109** | **7.7%** |

## Charts

```mermaid
%%{init: {"theme": "base", "themeVariables": {"xyChart": {"plotColorPalette": "#0072B2, #009E73, #D55E00, #999999"}}}}%%
xychart-beta
    title "combined -- package overview"
    x-axis ["purelib", "manylinux + bundleable", "platform/accel", "no ELF data (other)"]
    y-axis "Packages"
    bar [1188, 120, 32, 77]
```

## External Dependencies

| Library | Count | Projects |
|:---|---:|:---|
| libcrypto.so.3 | 5 | cmake, cryptography, grpcio, pyarrow, pymssql |
| libssl.so.3 | 5 | cmake, cryptography, grpcio, pyarrow, pymssql |
| libgomp.so.1 | 4 | ctranslate2, faiss-cpu, lightgbm, numba |
| libjpeg.so.62 | 4 | docling-parse, opencv-python, opencv-python-headless, pillow |
| libopenjp2.so.7 | 4 | docling-parse, opencv-python, opencv-python-headless, pillow |
| libavcodec.so.60 | 3 | av, opencv-python, opencv-python-headless |
| libavformat.so.60 | 3 | av, opencv-python, opencv-python-headless |
| libavutil.so.58 | 3 | av, opencv-python, opencv-python-headless |
| libbz2.so.1 | 3 | daft, pyarrow, python-libsbml |
| liblz4.so.1 | 3 | lz4, memray, pyarrow |
| libopenblasp.so.0 | 3 | numpy, opencv-python, opencv-python-headless |
| libre2.so.9 | 3 | grpcio, onnxruntime, pyarrow |
| libswscale.so.7 | 3 | av, opencv-python, opencv-python-headless |
| libtiff.so.5 | 3 | opencv-python, opencv-python-headless, pillow |
| libwebp.so.7 | 3 | opencv-python, opencv-python-headless, pillow |
| libwebpdemux.so.2 | 3 | opencv-python, opencv-python-headless, pillow |
| libwebpmux.so.3 | 3 | opencv-python, opencv-python-headless, pillow |
| libavdevice.so.60 | 2 | av, opencv-python |
| libffi.so.8 | 2 | cffi, pandoc-rhai |
| libfreetype.so.6 | 2 | docling-parse, pillow |
| libgssapi_krb5.so.2 | 2 | gssapi, pymssql |
| liblcms2.so.2 | 2 | docling-parse, pillow |
| libmariadb.so.3 | 2 | mariadb, mysqlclient |
| libopenblaso.so.0 | 2 | ctranslate2, faiss-cpu |
| libpng16.so.16 | 2 | opencv-python, opencv-python-headless |
| libsnappy.so.1 | 2 | openvino, pyarrow |
| libtbb.so.2 | 2 | openvino, prophet |
| libzstd.so.1 | 2 | llvmlite, pyarrow |
| libavfilter.so.9 | 1 | av |
| libc10.so | 1 | detectron2 |
| libcurl.so.4 | 1 | pyarrow |
| libdebuginfod.so.1 | 1 | memray |
| libeccodes.so.0.1 | 1 | pygrib |
| libev.so.4 | 1 | cassandra-driver |
| libexslt.so.0 | 1 | lxml |
| libgdal.so.36 | 1 | pyogrio |
| libgmp.so.10 | 1 | pandoc-rhai |
| libhdf5.so.310 | 1 | h5py |
| libhdf5_hl.so.310 | 1 | h5py |
| libk5crypto.so.3 | 1 | krb5 |
| libkrb5.so.3 | 1 | krb5 |
| libloguru.so.2 | 1 | docling-parse |
| libncurses.so.6 | 1 | cmake |
| libnetcdf.so.19 | 1 | netcdf4 |
| libodbc.so.2 | 1 | pyodbc |
| libpq.so.5 | 1 | psycopg2 |
| libproj.so.25 | 1 | pyproj |
| libswresample.so.4 | 1 | av |
| libthrift-0.24.0.so | 1 | pyarrow |
| libtinfo.so.6 | 1 | cmake |
| libtorch_cpu.so | 1 | detectron2 |
| libtorch_python.so | 1 | detectron2 |
| libunwind.so.8 | 1 | memray |
| libutf8proc.so.2 | 1 | pyarrow |
| libxml2.so.2 | 1 | lxml |
| libxslt.so.1 | 1 | lxml |

56 unique libraries across 108 project references

## Dependency Complexity

### Manylinux-only (110 packages)

These packages only depend on manylinux baseline libraries
and/or libraries provided by other wheels in the index.

aiohttp, aiokafka, annoy, apache-tvm-ffi, argon2-cffi-bindings, array-record, ast-serialize, asyncmy, asyncpg, backports-zstd, base2048, bcrypt, biotite, biotraj, blake3, blis, brotli, cachebox, caio, cartopy, cbor2, cftime, chromadb, clickhouse-connect, contourpy, coreforecast, coverage, cymem, cysignals, cython, debugpy, dm-tree, duckdb, fastar, fastavro, fasttext-predict, fastuuid, frozenlist, gevent, geventhttpclient, goodpoints, google-re2, greenlet, grpcio-tools, hf-xet, hiredis, hnswlib, httptools, jiter, jpype1, kernels-data, kiwisolver, kornia-rs, lancedb, lapx, lazy-object-proxy, libcst, librt, llguidance, markupsafe, matplotlib, maturin, minify-html, ml-dtypes, mmh3, msgpack, msgspec, multidict, murmurhash, nh3, numcodecs, numexpr, nvtx, obstore, onnx, openai-harmony, openalgo, openshell, optree, oracledb, orjson, ormsgpack, outlines-core, pandas, patchelf, peewee, pendulum, phik, pinecone, polars, posix-ipc, preshed, propcache, protobuf, psutil, py-rust-stemmers, py-spy, pybase64, pyclipper, pycocotools, pycrdt, pycryptodome, pycryptodomex, pydantic-core, pydantic-monty-client, pydantic-monty-runtime, pymongo, pynacl, pysqlite3, python-rapidjson

### Could become manylinux by bundling (7 packages)

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

### AI accelerator-specific (1 packages)

Depend on CUDA, ROCm, or PyTorch runtime libraries.
These must be provided by the accelerator platform.

| Package | Additional libraries |
|:---|:---|
| detectron2 | libc10.so, libtorch_cpu.so, libtorch_python.so |

### Unbundleable external dependencies (31 packages)

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
| faiss-cpu | libgomp.so.1, libopenblaso.so.0 |
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
| openvino | libsnappy.so.1 (+ libtbb.so.2) |
| pandoc-rhai | libffi.so.8, libgmp.so.10 |
| pillow | libfreetype.so.6, libjpeg.so.62, liblcms2.so.2, libopenjp2.so.7, libtiff.so.5, libwebp.so.7, libwebpdemux.so.2, libwebpmux.so.3 |
| pyarrow | libbz2.so.1, libcrypto.so.3, libcurl.so.4, liblz4.so.1, libsnappy.so.1, libssl.so.3, libzstd.so.1 (+ libre2.so.9, libthrift-0.24.0.so, libutf8proc.so.2) |
| pymssql | libcrypto.so.3, libgssapi_krb5.so.2, libssl.so.3 |
| pyodbc | libodbc.so.2 |
| pyogrio | libgdal.so.36 |
| pyproj | libproj.so.25 |
| python-libsbml | libbz2.so.1 |

**Total:** 149 packages with ELF dependencies (110 manylinux-only, 7 bundleable, 1 accelerator, 31 unbundleable, 0 undecided, 0 unknown)

## Packages without ELF Data (80)

Platlib packages that ship platform-specific wheels but have no
fromager-elf-requires/provides metadata. These are typically
pre-built upstream wheels, proprietary binary blobs, packages
with optional C extensions, or packages built without fromager
instrumentation.

**Pre-built manylinux (3):** intel-cmplr-lib-ur, intel-openmp, soundfile

**Other (77):** dulwich, eval-hub-server, frozendict, mysql-connector-python, pytokens, pywavelets, pyyaml, pyzmq, rapidfuzz, rasterio, ray, regex, rfc3161-client, rignore, ripgrep, river, rpds-py, rtree, ruff, safetensors, sccache, scikit-image, scikit-learn, scikit-network, scipy, selenium, sentencepiece, setproctitle, shap, shapely, simsimd, snowflake-connector-python, soxr, spacy, sqlalchemy, srsly, statsforecast, statsmodels, stringzilla, tensordict, tensorflow-cpu, tesserocr, thinc, tiktoken, tokenizers, torch, torchaudio, torchcodec, torchvision, tornado, tree-sitter, tree-sitter-c, tree-sitter-javascript, tree-sitter-languages, tree-sitter-python, tree-sitter-typescript, triton, ujson, uuid-utils, uv, uv-build, uvloop, vllm, wandb, watchfiles, websockets, wordcloud, wrapt, xformers, xgboost, xgrammar, xxhash, yara-python, yarl, zentorch, zope-interface, zstandard

