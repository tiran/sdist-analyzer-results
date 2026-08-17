# ELF Analysis: rocm7.1-ubi9-test

## Summary

| Category | Count | % |
|:---|---:|---:|
| **Total packages** | **377** |  |
| &ensp;Purelib (pure Python) | 285 | 75.6% |
| &ensp;Platlib (native code) | 92 | 24.4% |
| &ensp;Manylinux + bundleable | 61 | 16.2% |
| &ensp;&ensp;Manylinux-only | 57 | 15.1% |
| &ensp;&ensp;Could be bundled | 3 | 0.8% |
| &ensp;&ensp;Pre-built (manylinux) | 1 | 0.3% |
| &ensp;Platform-dependent | 31 | 8.2% |
| &ensp;&ensp;Accelerator-specific | 9 | 2.4% |
| &ensp;&ensp;Unbundleable | 22 | 5.8% |
| &ensp;&ensp;Undecided | 0 | 0.0% |
| &ensp;&ensp;Unknown | 0 | 0.0% |
| **Purelib + manylinux + bundleable** | **346** | **91.8%** |
| **Platform/accel + other** | **31** | **8.2%** |

## Charts

```mermaid
%%{init: {"theme": "base", "themeVariables": {"xyChart": {"plotColorPalette": "#0072B2, #009E73, #D55E00"}}}}%%
xychart-beta
    title "rocm7.1-ubi9-test -- package overview"
    x-axis ["purelib", "manylinux + bundleable", "platform/accel"]
    y-axis "Packages"
    bar [285, 61, 31]
```

## External Dependencies

| Library | Count | Projects |
|:---|---:|:---|
| libamdhip64.so.7 | 6 | amd-aiter, aotriton, flash-attn, torch, torchvision, vllm |
| libgomp.so.1 | 5 | bitsandbytes, numba, scikit-learn, simsimd, torch |
| libcrypto.so.3 | 4 | cmake, cryptography, grpcio, pyarrow |
| librocrand.so.1 | 4 | bitsandbytes, torch, torchaudio, vllm |
| libssl.so.3 | 4 | cmake, cryptography, grpcio, pyarrow |
| libavcodec.so.60 | 3 | av, opencv-python-headless, torchvision |
| libavformat.so.60 | 3 | av, opencv-python-headless, torchvision |
| libavutil.so.58 | 3 | av, opencv-python-headless, torchvision |
| libbz2.so.1 | 3 | pyarrow, uv, uv-build |
| libhipblas.so.3 | 3 | bitsandbytes, torch, vllm |
| libhipblaslt.so.1 | 3 | bitsandbytes, torch, vllm |
| libjpeg.so.62 | 3 | opencv-python-headless, pillow, torchvision |
| liblzma.so.5 | 3 | aotriton, torch, uv-build |
| libopenblasp.so.0 | 3 | numpy, opencv-python-headless, scipy |
| libswscale.so.7 | 3 | av, opencv-python-headless, torchvision |
| libwebp.so.7 | 3 | opencv-python-headless, pillow, torchvision |
| libgdal.so.36 | 2 | pyogrio, rasterio |
| libhiprand.so.1 | 2 | bitsandbytes, torch |
| libhipsparse.so.4 | 2 | bitsandbytes, torch |
| libopenjp2.so.7 | 2 | opencv-python-headless, pillow |
| libpng16.so.16 | 2 | opencv-python-headless, torchvision |
| libre2.so.9 | 2 | grpcio, pyarrow |
| librocsolver.so.0 | 2 | torch, torchaudio |
| libswresample.so.4 | 2 | av, torchvision |
| libtiff.so.5 | 2 | opencv-python-headless, pillow |
| libtinfo.so.6 | 2 | cmake, llvmlite |
| libwebpdemux.so.2 | 2 | opencv-python-headless, pillow |
| libwebpmux.so.3 | 2 | opencv-python-headless, pillow |
| libMIOpen.so.1 | 1 | torch |
| libavdevice.so.60 | 1 | av |
| libavfilter.so.9 | 1 | av |
| libcurl.so.4 | 1 | pyarrow |
| libffi.so.8 | 1 | cffi |
| libfreetype.so.6 | 1 | pillow |
| libgeos_c.so.1 | 1 | shapely |
| libgfortran.so.5 | 1 | scipy |
| libhdf5.so.310 | 1 | h5py |
| libhdf5_hl.so.310 | 1 | h5py |
| libhipfft.so.0 | 1 | torch |
| libhiprtc.so.7 | 1 | torch |
| libhipsolver.so.1 | 1 | torch |
| libhipsparselt.so.0 | 1 | torch |
| liblcms2.so.2 | 1 | pillow |
| liblz4.so.1 | 1 | pyarrow |
| libmpi.so.40 | 1 | torch |
| libmpi_cxx.so.40 | 1 | torch |
| libncurses.so.6 | 1 | cmake |
| libnetcdf.so.19 | 1 | netcdf4 |
| libnuma.so.1 | 1 | torch |
| libopenblaso.so.0 | 1 | torch |
| libproj.so.25 | 1 | pyproj |
| librccl.so.1 | 1 | torch |
| librocblas.so.5 | 1 | torch |
| libroctracer64.so.4 | 1 | torch |
| libroctx64.so.4 | 1 | torch |
| libsnappy.so.1 | 1 | pyarrow |
| libthrift-0.15.0.so | 1 | pyarrow |
| libutf8proc.so.2 | 1 | pyarrow |
| libyaml-0.so.2 | 1 | pyyaml |
| libzip.so.5 | 1 | tacozip |
| libzmq.so.5 | 1 | pyzmq |
| libzstd.so.1 | 1 | pyarrow |

62 unique libraries across 114 project references

## Inter-wheel Dependencies

| Library | Provided by | Required by |
|:---|:---|:---|
| libc10.so | torch | amd-aiter, flash-attn, torchao, torchvision, vllm |
| libc10_hip.so | torch | amd-aiter, flash-attn, torchao, torchvision, vllm |
| libtorch.so | torch | amd-aiter, torchaudio, vllm |
| libtorch_cpu.so | torch | amd-aiter, flash-attn, torchao, torchaudio, torchvision, vllm |
| libtorch_hip.so | torch | amd-aiter, flash-attn, torchao, torchaudio, torchvision, vllm |
| libtorch_python.so | torch | amd-aiter, flash-attn, torchaudio |
| libtvm_ffi.so | apache-tvm-ffi | xgrammar |

7 shared libraries provided by wheels and used by other wheels

## Dependency Complexity

### Manylinux-only (57 packages)

These packages only depend on manylinux baseline libraries
and/or libraries provided by other wheels in the index.

aiohttp, apache-tvm-ffi, blake3, cartopy, cbor2, cftime, contourpy, cython, duckdb, fastar, frozenlist, hf-xet, hiredis, httptools, jiter, kiwisolver, kornia-rs, libcst, llguidance, markupsafe, matplotlib, maturin, ml-dtypes, msgspec, multidict, numcodecs, obstore, onnx, openai-harmony, outlines-core, pandas, patchelf, propcache, protobuf, psutil, pybase64, pydantic-core, regex, rignore, rpds-py, safetensors, scikit-image, sentencepiece, setproctitle, soxr, stringzilla, tiktoken, tokenizers, triton, uvloop, watchfiles, websockets, wrapt, xgrammar, xxhash, yarl, zstandard

### Could become manylinux by bundling (3 packages)

All external deps are vendorable -- bundling them would make
these wheels manylinux-compatible.

| Package | Libraries |
|:---|:---|
| pyyaml | libyaml-0.so.2 |
| pyzmq | libzmq.so.5 |
| tacozip | libzip.so.5 |

### AI accelerator-specific (9 packages)

Depend on CUDA, ROCm, or PyTorch runtime libraries.
These must be provided by the accelerator platform.

| Package | Additional libraries |
|:---|:---|
| amd-aiter | libamdhip64.so.7 |
| aotriton | libamdhip64.so.7, liblzma.so.5 |
| bitsandbytes | libgomp.so.1, libhipblas.so.3, libhipblaslt.so.1, libhiprand.so.1, libhipsparse.so.4, librocrand.so.1 |
| flash-attn | libamdhip64.so.7 |
| torch | libMIOpen.so.1, libamdhip64.so.7, libgomp.so.1, libhipblas.so.3, libhipblaslt.so.1, libhipfft.so.0, libhiprand.so.1, libhiprtc.so.7, libhipsolver.so.1, libhipsparse.so.4, libhipsparselt.so.0, liblzma.so.5, libmpi.so.40, libmpi_cxx.so.40, libnuma.so.1, libopenblaso.so.0, librccl.so.1, librocblas.so.5, librocrand.so.1, librocsolver.so.0, libroctracer64.so.4, libroctx64.so.4 |
| torchao |  |
| torchaudio | librocrand.so.1, librocsolver.so.0 |
| torchvision | libamdhip64.so.7, libavcodec.so.60, libavformat.so.60, libavutil.so.58, libjpeg.so.62, libpng16.so.16, libswresample.so.4, libswscale.so.7, libwebp.so.7 |
| vllm | libamdhip64.so.7, libhipblas.so.3, libhipblaslt.so.1, librocrand.so.1 |

### Unbundleable external dependencies (22 packages)

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
| grpcio | libcrypto.so.3, libssl.so.3 (+ libre2.so.9) |
| h5py | libhdf5.so.310, libhdf5_hl.so.310 |
| llvmlite | libtinfo.so.6 |
| netcdf4 | libnetcdf.so.19 |
| numba | libgomp.so.1 |
| numpy | libopenblasp.so.0 |
| opencv-python-headless | libavcodec.so.60, libavformat.so.60, libavutil.so.58, libjpeg.so.62, libopenblasp.so.0, libopenjp2.so.7, libpng16.so.16, libswscale.so.7, libtiff.so.5, libwebp.so.7, libwebpdemux.so.2, libwebpmux.so.3 |
| pillow | libfreetype.so.6, libjpeg.so.62, liblcms2.so.2, libopenjp2.so.7, libtiff.so.5, libwebp.so.7, libwebpdemux.so.2, libwebpmux.so.3 |
| pyarrow | libbz2.so.1, libcrypto.so.3, libcurl.so.4, liblz4.so.1, libsnappy.so.1, libssl.so.3, libzstd.so.1 (+ libre2.so.9, libthrift-0.15.0.so, libutf8proc.so.2) |
| pyogrio | libgdal.so.36 |
| pyproj | libproj.so.25 |
| rasterio | libgdal.so.36 |
| scikit-learn | libgomp.so.1 |
| scipy | libgfortran.so.5, libopenblasp.so.0 |
| shapely | libgeos_c.so.1 |
| simsimd | libgomp.so.1 |
| uv | libbz2.so.1 |
| uv-build | libbz2.so.1, liblzma.so.5 |

**Total:** 91 packages with ELF dependencies (57 manylinux-only, 3 bundleable, 9 accelerator, 22 unbundleable, 0 undecided, 0 unknown)

## Packages without ELF Data (1)

Platlib packages that ship platform-specific wheels but have no
fromager-elf-requires/provides metadata. These are typically
pre-built upstream wheels, proprietary binary blobs, packages
with optional C extensions, or packages built without fromager
instrumentation.

**Pre-built manylinux (1):** soundfile

