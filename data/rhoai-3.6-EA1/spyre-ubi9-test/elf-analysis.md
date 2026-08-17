# ELF Analysis: spyre-ubi9-test

## Summary

| Category | Count | % |
|:---|---:|---:|
| **Total packages** | **813** |  |
| &ensp;Purelib (pure Python) | 661 | 81.3% |
| &ensp;Platlib (native code) | 152 | 18.7% |
| &ensp;Manylinux + bundleable | 114 | 14.0% |
| &ensp;&ensp;Manylinux-only | 107 | 13.2% |
| &ensp;&ensp;Could be bundled | 5 | 0.6% |
| &ensp;&ensp;Pre-built (manylinux) | 2 | 0.2% |
| &ensp;Platform-dependent | 35 | 4.3% |
| &ensp;&ensp;Accelerator-specific | 2 | 0.2% |
| &ensp;&ensp;Unbundleable | 33 | 4.1% |
| &ensp;&ensp;Undecided | 0 | 0.0% |
| &ensp;&ensp;Unknown | 0 | 0.0% |
| &ensp;No ELF data (other) | 4 | 0.5% |
| **Purelib + manylinux + bundleable** | **775** | **95.3%** |
| **Platform/accel + other** | **38** | **4.7%** |

## Charts

```mermaid
%%{init: {"theme": "base", "themeVariables": {"xyChart": {"plotColorPalette": "#0072B2, #009E73, #D55E00, #999999"}}}}%%
xychart-beta
    title "spyre-ubi9-test -- package overview"
    x-axis ["purelib", "manylinux + bundleable", "platform/accel", "no ELF data (other)"]
    y-axis "Packages"
    bar [661, 114, 35, 4]
```

## External Dependencies

| Library | Count | Projects |
|:---|---:|:---|
| libgomp.so.1 | 7 | faiss-cpu, lightgbm, numba, scikit-learn, scikit-network, torch, xgboost |
| libcrypto.so.3 | 6 | cmake, cryptography, grpcio, pyarrow, sccache, yara-python |
| libssl.so.3 | 5 | cmake, cryptography, grpcio, pyarrow, sccache |
| libbz2.so.1 | 4 | daft, pyarrow, uv, uv-build |
| libjpeg.so.62 | 3 | opencv-python-headless, pillow, torchvision |
| libopenblasp.so.0 | 3 | numpy, opencv-python-headless, scipy |
| libre2.so.9 | 3 | grpcio, onnxruntime, pyarrow |
| libwebp.so.7 | 3 | opencv-python-headless, pillow, torchvision |
| libfreetype.so.6 | 2 | matplotlib, pillow |
| liblz4.so.1 | 2 | lz4, pyarrow |
| libopenblaso.so.0 | 2 | faiss-cpu, torch |
| libopenjp2.so.7 | 2 | opencv-python-headless, pillow |
| libpng16.so.16 | 2 | opencv-python-headless, torchvision |
| libtiff.so.5 | 2 | opencv-python-headless, pillow |
| libwebpdemux.so.2 | 2 | opencv-python-headless, pillow |
| libwebpmux.so.3 | 2 | opencv-python-headless, pillow |
| libzstd.so.1 | 2 | llvmlite, pyarrow |
| libavcodec.so.60 | 1 | opencv-python-headless |
| libavformat.so.60 | 1 | opencv-python-headless |
| libavutil.so.58 | 1 | opencv-python-headless |
| libcurl.so.4 | 1 | pyarrow |
| libeccodes.so.0.1 | 1 | pygrib |
| libexslt.so.0 | 1 | lxml |
| libffi.so.8 | 1 | cffi |
| libgdal.so.36 | 1 | pyogrio |
| libgeos_c.so.1 | 1 | shapely |
| libgfortran.so.5 | 1 | scipy |
| libgssapi_krb5.so.2 | 1 | gssapi |
| libhdf5.so.310 | 1 | h5py |
| libhdf5_hl.so.310 | 1 | h5py |
| libk5crypto.so.3 | 1 | krb5 |
| libkrb5.so.3 | 1 | krb5 |
| liblcms2.so.2 | 1 | pillow |
| liblzma.so.5 | 1 | uv-build |
| libmariadb.so.3 | 1 | mariadb |
| libmpi.so.40 | 1 | torch |
| libmpi_cxx.so.40 | 1 | torch |
| libncurses.so.6 | 1 | cmake |
| libnetcdf.so.19 | 1 | netcdf4 |
| libnuma.so.1 | 1 | torch |
| libproj.so.25 | 1 | pyproj |
| libqhull_r.so.7 | 1 | matplotlib |
| libsnappy.so.1 | 1 | pyarrow |
| libswscale.so.7 | 1 | opencv-python-headless |
| libtbb.so.2 | 1 | prophet |
| libthrift-0.15.0.so | 1 | pyarrow |
| libthrift-0.24.0.so | 1 | pyarrow |
| libtinfo.so.6 | 1 | cmake |
| libunwind.so.8 | 1 | ray |
| libutf8proc.so.2 | 1 | pyarrow |
| libxml2.so.2 | 1 | lxml |
| libxslt.so.1 | 1 | lxml |
| libzmq.so.5 | 1 | pyzmq |

53 unique libraries across 88 project references

## Inter-wheel Dependencies

| Library | Provided by | Required by |
|:---|:---|:---|
| libc10.so | torch | torchvision |
| libtorch_cpu.so | torch | torchaudio, torchvision |
| libtvm_ffi.so | apache-tvm-ffi | xgrammar |

3 shared libraries provided by wheels and used by other wheels

## Dependency Complexity

### Manylinux-only (107 packages)

These packages only depend on manylinux baseline libraries
and/or libraries provided by other wheels in the index.

aiohttp, aiokafka, annoy, apache-tvm-ffi, argon2-cffi-bindings, asyncmy, backports-zstd, blake3, blis, brotli, cachebox, cbor2, cftime, contourpy, cymem, cython, debugpy, duckdb, eval-hub-server, fastar, fasttext-predict, fastuuid, frozenlist, gevent, geventhttpclient, goodpoints, greenlet, grpcio-tools, hf-xet, hiredis, httptools, jiter, kiwisolver, libcst, llguidance, markupsafe, maturin, minify-html, ml-dtypes, mmh3, msgpack, msgspec, multidict, murmurhash, nh3, numcodecs, numexpr, nvtx, obstore, onnx, openai-harmony, openshell, orjson, ormsgpack, outlines-core, pandas, patchelf, peewee, phik, polars, preshed, propcache, protobuf, psutil, py-rust-stemmers, py-spy, pybase64, pycryptodomex, pydantic-core, pydantic-monty, pydantic-monty-client, pydantic-monty-runtime, python-rapidjson, pywavelets, rapidfuzz, regex, rfc3161-client, rignore, rpds-py, safetensors, sentencepiece, setproctitle, spacy, speechrecognition, sqlalchemy, srsly, statsmodels, tensordict, thinc, tiktoken, tokenizers, tornado, tree-sitter, tree-sitter-languages, triton, uuid-utils, uvloop, wandb, watchfiles, websockets, wordcloud, wrapt, xgrammar, xxhash, yarl, zope-interface, zstandard

### Could become manylinux by bundling (5 packages)

All external deps are vendorable -- bundling them would make
these wheels manylinux-compatible.

| Package | Libraries |
|:---|:---|
| mariadb | libmariadb.so.3 |
| onnxruntime | libre2.so.9 |
| prophet | libtbb.so.2 |
| pygrib | libeccodes.so.0.1 |
| pyzmq | libzmq.so.5 |

### AI accelerator-specific (2 packages)

Depend on CUDA, ROCm, or PyTorch runtime libraries.
These must be provided by the accelerator platform.

| Package | Additional libraries |
|:---|:---|
| torchaudio |  |
| torchvision | libjpeg.so.62, libpng16.so.16, libwebp.so.7 |

### Unbundleable external dependencies (33 packages)

At least one external dep must never be bundled (crypto,
system runtime, etc.) and must be provided by the platform.
This includes indirect dependencies (e.g. libmariadb depends
on OpenSSL, libpq depends on OpenSSL + Kerberos).

| Package | Libraries |
|:---|:---|
| cffi | libffi.so.8 |
| cmake | libcrypto.so.3, libncurses.so.6, libssl.so.3, libtinfo.so.6 |
| cryptography | libcrypto.so.3, libssl.so.3 |
| daft | libbz2.so.1 |
| faiss-cpu | libgomp.so.1, libopenblaso.so.0 |
| grpcio | libcrypto.so.3, libssl.so.3 (+ libre2.so.9) |
| gssapi | libgssapi_krb5.so.2 |
| h5py | libhdf5.so.310, libhdf5_hl.so.310 |
| krb5 | libk5crypto.so.3, libkrb5.so.3 |
| lightgbm | libgomp.so.1 |
| llvmlite | libzstd.so.1 |
| lxml | libexslt.so.0, libxml2.so.2, libxslt.so.1 |
| lz4 | liblz4.so.1 |
| matplotlib | libfreetype.so.6 (+ libqhull_r.so.7) |
| netcdf4 | libnetcdf.so.19 |
| numba | libgomp.so.1 |
| numpy | libopenblasp.so.0 |
| opencv-python-headless | libavcodec.so.60, libavformat.so.60, libavutil.so.58, libjpeg.so.62, libopenblasp.so.0, libopenjp2.so.7, libpng16.so.16, libswscale.so.7, libtiff.so.5, libwebp.so.7, libwebpdemux.so.2, libwebpmux.so.3 |
| pillow | libfreetype.so.6, libjpeg.so.62, liblcms2.so.2, libopenjp2.so.7, libtiff.so.5, libwebp.so.7, libwebpdemux.so.2, libwebpmux.so.3 |
| pyarrow | libbz2.so.1, libcrypto.so.3, libcurl.so.4, liblz4.so.1, libsnappy.so.1, libssl.so.3, libzstd.so.1 (+ libre2.so.9, libthrift-0.15.0.so, libthrift-0.24.0.so, libutf8proc.so.2) |
| pyogrio | libgdal.so.36 |
| pyproj | libproj.so.25 |
| ray | libunwind.so.8 |
| sccache | libcrypto.so.3, libssl.so.3 |
| scikit-learn | libgomp.so.1 |
| scikit-network | libgomp.so.1 |
| scipy | libgfortran.so.5, libopenblasp.so.0 |
| shapely | libgeos_c.so.1 |
| torch | libgomp.so.1, libmpi.so.40, libmpi_cxx.so.40, libnuma.so.1, libopenblaso.so.0 |
| uv | libbz2.so.1 |
| uv-build | libbz2.so.1, liblzma.so.5 |
| xgboost | libgomp.so.1 |
| yara-python | libcrypto.so.3 |

**Total:** 147 packages with ELF dependencies (107 manylinux-only, 5 bundleable, 2 accelerator, 33 unbundleable, 0 undecided, 0 unknown)

## Packages without ELF Data (6)

Platlib packages that ship platform-specific wheels but have no
fromager-elf-requires/provides metadata. These are typically
pre-built upstream wheels, proprietary binary blobs, packages
with optional C extensions, or packages built without fromager
instrumentation.

**Pre-built manylinux (2):** intel-cmplr-lib-ur, intel-openmp

**Other (4):** dulwich, pyyaml, torch-nnpa, vllm

