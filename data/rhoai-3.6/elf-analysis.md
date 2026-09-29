# ELF Analysis: combined

## Summary

| Category | Count | % |
|:---|---:|---:|
| **Total packages** | **1502** |  |
| &ensp;Purelib (pure Python) | 1239 | 82.5% |
| &ensp;Platlib (native code) | 263 | 17.5% |
| &ensp;Manylinux + bundleable | 187 | 12.5% |
| &ensp;&ensp;Manylinux-only | 171 | 11.4% |
| &ensp;&ensp;Could be bundled | 11 | 0.7% |
| &ensp;&ensp;Pre-built (manylinux) | 5 | 0.3% |
| &ensp;Platform-dependent | 73 | 4.9% |
| &ensp;&ensp;Accelerator-specific | 28 | 1.9% |
| &ensp;&ensp;Unbundleable | 45 | 3.0% |
| &ensp;&ensp;Undecided | 0 | 0.0% |
| &ensp;&ensp;Unknown | 0 | 0.0% |
| &ensp;No ELF data (other) | 8 | 0.5% |
| **Purelib + manylinux + bundleable** | **1426** | **94.9%** |
| **Platform/accel + other** | **76** | **5.1%** |

## Charts

```mermaid
%%{init: {"theme": "base", "themeVariables": {"xyChart": {"plotColorPalette": "#0072B2, #009E73, #D55E00, #999999"}}}}%%
xychart-beta
    title "combined -- package overview"
    x-axis ["purelib", "manylinux + bundleable", "platform/accel", "no ELF data (other)"]
    y-axis "Packages"
    bar [1239, 187, 73, 8]
```

## External Dependencies

| Library | Count | Projects |
|:---|---:|:---|
| libcudart.so.12 | 18 | bitsandbytes, causal-conv1d, deep-ep, deep-gemm, detectron2, faiss-cpu, flash-attn, flashinfer-jit-cache, kvcached, mamba-ssm, nixl-cu12, onnxruntime-gpu, pplx-kernels, torchao, torchaudio, torchcodec, torchvision, vllm |
| libcudart.so.13 | 13 | bitsandbytes, causal-conv1d, detectron2, faiss-cpu, flash-attn, kvcached, mamba-ssm, onnxruntime-gpu, torchao, torchaudio, torchcodec, torchvision, vllm |
| libgomp.so.1 | 11 | bitsandbytes, ctranslate2, faiss-cpu, lightgbm, numba, scikit-learn, scikit-network, simsimd, torch, xgboost, zentorch |
| libamdhip64.so.7 | 10 | amd-aiter, aotriton, ctranslate2, detectron2, flash-attn, flydsl, tensorflow-rocm, torch, torchvision, vllm |
| libc10_cuda.so | 10 | causal-conv1d, deep-ep, deep-gemm, detectron2, flash-attn, mamba-ssm, pplx-kernels, torchcodec, torchvision, vllm |
| libcrypto.so.3 | 9 | cmake, cryptography, grpcio, pyarrow, pymssql, runai-model-streamer-azure, runai-model-streamer-s3, sccache, yara-python |
| libssl.so.3 | 8 | cmake, cryptography, grpcio, pyarrow, pymssql, runai-model-streamer-azure, runai-model-streamer-s3, sccache |
| libtorch_cuda.so | 8 | deep-gemm, flash-attn, pplx-kernels, torchao, torchaudio, torchcodec, torchvision, vllm |
| libbz2.so.1 | 6 | daft, pyarrow, python-libsbml, selenium, uv, uv-build |
| libcuda.so.1 | 5 | flashinfer-jit-cache, kvcached, pplx-kernels, pyarrow, vllm |
| libjpeg.so.62 | 5 | docling-parse, opencv-python, opencv-python-headless, pillow, torchvision |
| libre2.so.9 | 5 | grpcio, onnxruntime, onnxruntime-gpu, onnxruntime-migraphx, pyarrow |
| libavcodec.so.60 | 4 | av, opencv-python, opencv-python-headless, torchcodec |
| libavformat.so.60 | 4 | av, opencv-python, opencv-python-headless, torchcodec |
| libavutil.so.58 | 4 | av, opencv-python, opencv-python-headless, torchcodec |
| libcublas.so.12 | 4 | bitsandbytes, faiss-cpu, flashinfer-jit-cache, onnxruntime-gpu |
| libcublasLt.so.12 | 4 | bitsandbytes, faiss-cpu, flashinfer-jit-cache, onnxruntime-gpu |
| libhipblas.so.3 | 4 | bitsandbytes, ctranslate2, torch, vllm |
| libnvrtc.so.12 | 4 | deep-gemm, flashinfer-jit-cache, torchcodec, vllm |
| libopenblasp.so.0 | 4 | numpy, opencv-python, opencv-python-headless, scipy |
| libopenjp2.so.7 | 4 | docling-parse, opencv-python, opencv-python-headless, pillow |
| librocrand.so.1 | 4 | bitsandbytes, torch, torchcodec, vllm |
| libswscale.so.7 | 4 | av, opencv-python, opencv-python-headless, torchcodec |
| libwebp.so.7 | 4 | opencv-python, opencv-python-headless, pillow, torchvision |
| libavdevice.so.60 | 3 | av, opencv-python, torchcodec |
| libcublas.so.13 | 3 | bitsandbytes, faiss-cpu, onnxruntime-gpu |
| libcublasLt.so.13 | 3 | bitsandbytes, faiss-cpu, onnxruntime-gpu |
| libcurl.so.4 | 3 | pyarrow, runai-model-streamer-azure, runai-model-streamer-s3 |
| libfreetype.so.6 | 3 | docling-parse, matplotlib, pillow |
| libhiprand.so.1 | 3 | bitsandbytes, ctranslate2, torch |
| liblz4.so.1 | 3 | lz4, memray, pyarrow |
| liblzma.so.5 | 3 | aotriton, torch, uv-build |
| libnuma.so.1 | 3 | tensorflow-rocm, torch, vllm |
| libopenblaso.so.0 | 3 | ctranslate2, faiss-cpu, torch |
| libpng16.so.16 | 3 | opencv-python, opencv-python-headless, torchvision |
| librocsolver.so.0 | 3 | tensorflow-rocm, torch, torchcodec |
| libtiff.so.5 | 3 | opencv-python, opencv-python-headless, pillow |
| libwebpdemux.so.2 | 3 | opencv-python, opencv-python-headless, pillow |
| libwebpmux.so.3 | 3 | opencv-python, opencv-python-headless, pillow |
| libavfilter.so.9 | 2 | av, torchcodec |
| libffi.so.8 | 2 | cffi, pandoc-rhai |
| libgdal.so.36 | 2 | pyogrio, rasterio |
| libgssapi_krb5.so.2 | 2 | gssapi, pymssql |
| libhipblaslt.so.1 | 2 | bitsandbytes, torch |
| libhipfft.so.0 | 2 | tensorflow-rocm, torch |
| libhipsolver.so.1 | 2 | tensorflow-rocm, torch |
| libhipsparse.so.4 | 2 | tensorflow-rocm, torch |
| libhipsparselt.so.0 | 2 | tensorflow-rocm, torch |
| libhsa-runtime64.so.1 | 2 | tensorflow-rocm, tilelang |
| liblcms2.so.2 | 2 | docling-parse, pillow |
| libmariadb.so.3 | 2 | mariadb, mysqlclient |
| libnvrtc.so.13 | 2 | torchcodec, vllm |
| libnvshmem_host.so.3 | 2 | deep-ep, pplx-kernels |
| librccl.so.1 | 2 | tensorflow-rocm, torch |
| libsnappy.so.1 | 2 | openvino, pyarrow |
| libswresample.so.4 | 2 | av, torchcodec |
| libtbb.so.2 | 2 | openvino, prophet |
| libunwind.so.8 | 2 | memray, ray |
| libxml2.so.2 | 2 | lxml, runai-model-streamer-azure |
| libzstd.so.1 | 2 | llvmlite, pyarrow |
| libMIOpen.so.1 | 1 | torch |
| libaio.so.1 | 1 | nixl-cu12 |
| libamd_comgr.so.3 | 1 | tensorflow-rocm |
| libcudnn.so.9 | 1 | onnxruntime-gpu |
| libcufft.so.11 | 1 | onnxruntime-gpu |
| libcufft.so.12 | 1 | onnxruntime-gpu |
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
| libhipfftw.so.0 | 1 | tensorflow-rocm |
| libhiprtc.so.7 | 1 | torch |
| libk5crypto.so.3 | 1 | krb5 |
| libkrb5.so.3 | 1 | krb5 |
| liblept.so.5 | 1 | tesserocr |
| libloguru.so.2 | 1 | docling-parse |
| libmpi.so.40 | 1 | torch |
| libmpi_cxx.so.40 | 1 | torch |
| libnccl.so.2 | 1 | deep-ep |
| libncurses.so.6 | 1 | cmake |
| libnetcdf.so.19 | 1 | netcdf4 |
| libnvjpeg.so.12 | 1 | torchvision |
| libnvjpeg.so.13 | 1 | torchvision |
| libodbc.so.2 | 1 | pyodbc |
| libomp.so | 1 | ctranslate2 |
| libpq.so.5 | 1 | psycopg2 |
| libproj.so.25 | 1 | pyproj |
| libpython3.12.so.1.0 | 1 | torchcodec |
| libqhull_r.so.7 | 1 | matplotlib |
| librocblas.so.5 | 1 | torch |
| librocm_smi64.so.1 | 1 | tensorflow-rocm |
| librocprofiler-register.so.0 | 1 | tensorflow-rocm |
| libroctracer64.so.4 | 1 | torch |
| libroctx64.so.4 | 1 | torch |
| libtesseract.so.4 | 1 | tesserocr |
| libthrift-0.15.0.so | 1 | pyarrow |
| libthrift-0.24.0.so | 1 | pyarrow |
| libtinfo.so.6 | 1 | cmake |
| libucp.so.0 | 1 | nixl-cu12 |
| libucs.so.0 | 1 | nixl-cu12 |
| libutf8proc.so.2 | 1 | pyarrow |
| libxslt.so.1 | 1 | lxml |
| libyaml-0.so.2 | 1 | pyyaml |
| libz3.so | 1 | tilelang |
| libzip.so.5 | 1 | tacozip |
| libzmq.so.5 | 1 | pyzmq |

113 unique libraries across 296 project references

## Inter-wheel Dependencies

| Library | Provided by | Required by |
|:---|:---|:---|
| libc10.so | torch | amd-aiter, amd-quark, causal-conv1d, deep-ep, deep-gemm, detectron2, flash-attn, kvcached, mamba-ssm, pplx-kernels, torchao, torchaudio, torchcodec, torchvision, vllm, zentorch |
| libc10_hip.so | torch | amd-aiter, detectron2, flash-attn, torchao, torchvision, vllm |
| libtorch.so | torch | amd-aiter, amd-quark, detectron2, pplx-kernels, torchao, torchaudio, torchcodec, torchvision, vllm, zentorch |
| libtorch_cpu.so | torch | amd-aiter, amd-quark, causal-conv1d, deep-ep, deep-gemm, detectron2, flash-attn, kvcached, mamba-ssm, pplx-kernels, torchao, torchaudio, torchcodec, torchvision, vllm, zentorch |
| libtorch_hip.so | torch | amd-aiter, flash-attn, torchao, torchcodec, torchvision, vllm |
| libtorch_python.so | torch | amd-aiter, causal-conv1d, deep-ep, deep-gemm, detectron2, flash-attn, kvcached, mamba-ssm, vllm, zentorch |
| libtvm_ffi.so | apache-tvm-ffi | tilelang, xgrammar |
| libz3.so.4.15 | z3-solver | tilelang |

8 shared libraries provided by wheels and used by other wheels

## Dependency Complexity

### Manylinux-only (171 packages)

These packages only depend on manylinux baseline libraries
and/or libraries provided by other wheels in the index.

aiohttp, aiokafka, annoy, apache-tvm-ffi, argon2-cffi-bindings, array-record, ast-serialize, asyncmy, asyncpg, backports-zstd, base2048, bcrypt, biotite, biotraj, blake3, blis, brotli, cachebox, caio, cartopy, cbor2, cftime, chromadb, clickhouse-connect, cmarkgfm, contourpy, coreforecast, coverage, cuda-bindings, cuda-tile, cymem, cysignals, cython, debugpy, dm-tree, duckdb, eval-hub-server, fastar, fastavro, fastsafetensors, fasttext-predict, fastuuid, frozenlist, gevent, geventhttpclient, goodpoints, google-re2, greenlet, grpcio-tools, hf-transfer, hf-xet, hiredis, hnswlib, httptools, jiter, jpype1, kernels-data, kiwisolver, kornia-rs, lancedb, lapx, lazy-object-proxy, libcst, librt, llguidance, markupsafe, maturin, minify-html, ml-dtypes, mmh3, msgpack, msgspec, multidict, murmurhash, nh3, numcodecs, numexpr, nvidia-cudnn-frontend, nvtx, obstore, onnx, openai-harmony, openalgo, openshell, optree, oracledb, orjson, ormsgpack, outlines-core, pandas, patchelf, peewee, pendulum, phik, pinecone, polars, posix-ipc, preshed, propcache, protobuf, psutil, py-rust-stemmers, py-spy, pybase64, pyclipper, pycocotools, pycrdt, pycryptodome, pycryptodomex, pydantic-core, pydantic-monty, pydantic-monty-client, pydantic-monty-runtime, pymongo, pynacl, pysqlite3, python-rapidjson, pytokens, pywavelets, rapidfuzz, regex, rfc3161-client, rignore, ripgrep, river, rpds-py, ruff, runai-model-streamer, runai-model-streamer-gcs, safetensors, scikit-image, sentencepiece, setproctitle, shap, snowflake-connector-python, soxr, spacy, speechrecognition, sqlalchemy, srsly, statsforecast, statsmodels, stringzilla, tensordict, tensorflow, tensorflow-cpu, thinc, tiktoken, tokenizers, tornado, tree-sitter, tree-sitter-c, tree-sitter-javascript, tree-sitter-languages, tree-sitter-python, tree-sitter-typescript, triton, ujson, uuid-utils, uvloop, wandb, watchfiles, websockets, wordcloud, wrapt, xgrammar, xxhash, yarl, z3-solver, zope-interface, zstandard

### Could become manylinux by bundling (11 packages)

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
| psycopg2 | libpq.so.5 |
| pygrib | libeccodes.so.0.1 |
| pyyaml | libyaml-0.so.2 |
| pyzmq | libzmq.so.5 |
| tacozip | libzip.so.5 |

### AI accelerator-specific (28 packages)

Depend on CUDA, ROCm, or PyTorch runtime libraries.
These must be provided by the accelerator platform.

| Package | Additional libraries |
|:---|:---|
| amd-aiter | libamdhip64.so.7 |
| amd-quark |  |
| aotriton | libamdhip64.so.7, liblzma.so.5 |
| bitsandbytes | libcublas.so.12, libcublas.so.13, libcublasLt.so.12, libcublasLt.so.13, libcudart.so.12, libcudart.so.13, libgomp.so.1, libhipblas.so.3, libhipblaslt.so.1, libhiprand.so.1, librocrand.so.1 |
| causal-conv1d | libc10_cuda.so, libcudart.so.12, libcudart.so.13 |
| ctranslate2 | libamdhip64.so.7, libgomp.so.1, libhipblas.so.3, libhiprand.so.1, libomp.so, libopenblaso.so.0 |
| deep-ep | libc10_cuda.so, libcudart.so.12, libnccl.so.2, libnvshmem_host.so.3 |
| deep-gemm | libc10_cuda.so, libcudart.so.12, libnvrtc.so.12, libtorch_cuda.so |
| detectron2 | libamdhip64.so.7, libc10_cuda.so, libcudart.so.12, libcudart.so.13 |
| faiss-cpu | libcublas.so.12, libcublas.so.13, libcublasLt.so.12, libcublasLt.so.13, libcudart.so.12, libcudart.so.13, libgomp.so.1, libopenblaso.so.0 |
| flash-attn | libamdhip64.so.7, libc10_cuda.so, libcudart.so.12, libcudart.so.13, libtorch_cuda.so |
| flashinfer-jit-cache | libcublas.so.12, libcublasLt.so.12, libcuda.so.1, libcudart.so.12, libnvrtc.so.12 |
| flydsl | libamdhip64.so.7 |
| kvcached | libcuda.so.1, libcudart.so.12, libcudart.so.13 |
| mamba-ssm | libc10_cuda.so, libcudart.so.12, libcudart.so.13 |
| nixl-cu12 | libaio.so.1, libcudart.so.12, libcufile.so.0, libucp.so.0, libucs.so.0 |
| onnxruntime-gpu | libcublas.so.12, libcublas.so.13, libcublasLt.so.12, libcublasLt.so.13, libcudart.so.12, libcudart.so.13, libcudnn.so.9, libcufft.so.11, libcufft.so.12, libcurand.so.10, libre2.so.9 |
| pplx-kernels | libc10_cuda.so, libcuda.so.1, libcudart.so.12, libnvshmem_host.so.3, libtorch_cuda.so |
| pyarrow | libbz2.so.1, libcrypto.so.3, libcuda.so.1, libcurl.so.4, liblz4.so.1, libre2.so.9, libsnappy.so.1, libssl.so.3, libthrift-0.15.0.so, libthrift-0.24.0.so, libutf8proc.so.2, libzstd.so.1 |
| tensorflow-rocm | libamd_comgr.so.3, libamdhip64.so.7, libhipfft.so.0, libhipfftw.so.0, libhipsolver.so.1, libhipsparse.so.4, libhipsparselt.so.0, libhsa-runtime64.so.1, libnuma.so.1, librccl.so.1, librocm_smi64.so.1, librocprofiler-register.so.0, librocsolver.so.0 |
| tilelang | libhsa-runtime64.so.1, libz3.so |
| torch | libMIOpen.so.1, libamdhip64.so.7, libgomp.so.1, libhipblas.so.3, libhipblaslt.so.1, libhipfft.so.0, libhiprand.so.1, libhiprtc.so.7, libhipsolver.so.1, libhipsparse.so.4, libhipsparselt.so.0, liblzma.so.5, libmpi.so.40, libmpi_cxx.so.40, libnuma.so.1, libopenblaso.so.0, librccl.so.1, librocblas.so.5, librocrand.so.1, librocsolver.so.0, libroctracer64.so.4, libroctx64.so.4 |
| torchao | libcudart.so.12, libcudart.so.13, libtorch_cuda.so |
| torchaudio | libcudart.so.12, libcudart.so.13, libtorch_cuda.so |
| torchcodec | libavcodec.so.60, libavdevice.so.60, libavfilter.so.9, libavformat.so.60, libavutil.so.58, libc10_cuda.so, libcudart.so.12, libcudart.so.13, libnvrtc.so.12, libnvrtc.so.13, libpython3.12.so.1.0, librocrand.so.1, librocsolver.so.0, libswresample.so.4, libswscale.so.7, libtorch_cuda.so |
| torchvision | libamdhip64.so.7, libc10_cuda.so, libcudart.so.12, libcudart.so.13, libjpeg.so.62, libnvjpeg.so.12, libnvjpeg.so.13, libpng16.so.16, libtorch_cuda.so, libwebp.so.7 |
| vllm | libamdhip64.so.7, libc10_cuda.so, libcuda.so.1, libcudart.so.12, libcudart.so.13, libhipblas.so.3, libnuma.so.1, libnvrtc.so.12, libnvrtc.so.13, librocrand.so.1, libtorch_cuda.so |
| zentorch | libgomp.so.1 |

### Unbundleable external dependencies (45 packages)

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
| matplotlib | libfreetype.so.6 (+ libqhull_r.so.7) |
| memray | libdebuginfod.so.1, liblz4.so.1, libunwind.so.8 |
| netcdf4 | libnetcdf.so.19 |
| numba | libgomp.so.1 |
| numpy | libopenblasp.so.0 |
| opencv-python | libavcodec.so.60, libavdevice.so.60, libavformat.so.60, libavutil.so.58, libjpeg.so.62, libopenblasp.so.0, libopenjp2.so.7, libpng16.so.16, libswscale.so.7, libtiff.so.5, libwebp.so.7, libwebpdemux.so.2, libwebpmux.so.3 |
| opencv-python-headless | libavcodec.so.60, libavformat.so.60, libavutil.so.58, libjpeg.so.62, libopenblasp.so.0, libopenjp2.so.7, libpng16.so.16, libswscale.so.7, libtiff.so.5, libwebp.so.7, libwebpdemux.so.2, libwebpmux.so.3 |
| openvino | libsnappy.so.1 (+ libtbb.so.2) |
| pandoc-rhai | libffi.so.8, libgmp.so.10 |
| pillow | libfreetype.so.6, libjpeg.so.62, liblcms2.so.2, libopenjp2.so.7, libtiff.so.5, libwebp.so.7, libwebpdemux.so.2, libwebpmux.so.3 |
| pymssql | libcrypto.so.3, libgssapi_krb5.so.2, libssl.so.3 |
| pyodbc | libodbc.so.2 |
| pyogrio | libgdal.so.36 |
| pyproj | libproj.so.25 |
| python-libsbml | libbz2.so.1 |
| rasterio | libgdal.so.36 |
| ray | libunwind.so.8 |
| runai-model-streamer-azure | libcrypto.so.3, libcurl.so.4, libssl.so.3, libxml2.so.2 |
| runai-model-streamer-s3 | libcrypto.so.3, libcurl.so.4, libssl.so.3 |
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

**Total:** 255 packages with ELF dependencies (171 manylinux-only, 11 bundleable, 28 accelerator, 45 unbundleable, 0 undecided, 0 unknown)

## Packages without ELF Data (13)

Platlib packages that ship platform-specific wheels but have no
fromager-elf-requires/provides metadata. These are typically
pre-built upstream wheels, proprietary binary blobs, packages
with optional C extensions, or packages built without fromager
instrumentation.

**Pre-built manylinux (5):** intel-cmplr-lib-ur, intel-openmp, nvidia-cutlass-dsl-libs-base, nvidia-cutlass-dsl-libs-cu13, soundfile

**Other (8):** cupy-cuda13x, dulwich, frozendict, mysql-connector-python, nixl-cu13, rtree, torch-nnpa, xformers

