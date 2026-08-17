# Packages depending on CUDA/ROCm without Torch

Analysis of RHOAI 3.6-EA1 combined index: which packages link against
CUDA or ROCm libraries but do **not** link against any PyTorch C++
runtime library (libtorch\*, libc10\*)?

Of the 30 accelerator-specific packages, **17 link against torch**
(libc10.so, libtorch\_cpu.so, etc. provided by the torch wheel) and
**1 is torch itself**.  The remaining **12 packages** use CUDA or ROCm
directly without the PyTorch runtime:

| Package | Accelerator | Libraries (beyond manylinux baseline) |
|:---|:---|:---|
| aotriton | ROCm | libamdhip64, liblzma |
| bitsandbytes | CUDA + ROCm | libcublas, libcublasLt, libcudart, libcusparse, libnvJitLink, libhipblas, libhipblaslt, libhiprand, libhipsparse, librocrand, libgomp |
| cupy-cuda13x | CUDA | libcublas, libcufft, libcurand, libcusolver, libcusparse, libcusparseLt, libnccl, libnvrtc |
| faiss-cpu | CUDA | libcublas, libcublasLt, libcudart, libgomp, libopenblaso |
| flashinfer-jit-cache | CUDA | libcublas, libcublasLt, libcuda, libcudart, libnvrtc |
| flydsl | ROCm | libamdhip64 |
| nixl-cu12 | CUDA | libcudart, libcufile, libaio, libucp, libucs |
| nixl-cu13 | CUDA | libcudart, libcufile, libaio, libucp, libucs |
| onnxruntime-gpu | CUDA | libcublas, libcublasLt, libcudart, libcudnn, libcufft, libcurand, libre2 |
| pyarrow | CUDA | libcuda, libcrypto, libssl, libcurl, libbz2, liblz4, libre2, libsnappy, libthrift, libutf8proc, libzstd |
| tensorflow-rocm | ROCm | libamd\_comgr, libamdhip64, libhipfft, libhipfftw, libhipsolver, libhipsparse, libhipsparselt, libhsa-runtime64, libnuma, librccl, librocm\_smi64, librocprofiler-register, librocsolver |
| tilelang | ROCm | libhsa-runtime64, libz3 |

**Summary:** 7 CUDA-only, 4 ROCm-only, 1 both (bitsandbytes).
pyarrow's CUDA dependency (libcuda.so.1) is for GPU-accelerated Arrow
buffers and is optional at runtime.
