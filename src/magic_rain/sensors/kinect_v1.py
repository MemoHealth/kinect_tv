"""Depth-only adapter for the Microsoft Kinect SDK 1.8 installed on Windows."""

import ctypes as ct
import sys
from ctypes import wintypes as win
from math import ceil
from time import monotonic

import numpy as np
from numpy.typing import NDArray

from .base import SensorFrame, SensorHealth

WIDTH, HEIGHT = 320, 240
USES_DEPTH = 0x20
IMAGE_DEPTH = 4
RESOLUTION_320X240 = 1
NO_FRAME = 0x83010001
DISCONNECTED = {0x83010014, 0x83010015, 0x8301027F, 0x8007048F}
LOAD_LIBRARY_SEARCH_SYSTEM32 = 0x800


class SensorError(RuntimeError):
    def __init__(self, status: SensorHealth, detail: str) -> None:
        super().__init__(detail)
        self.status = status


class _ImageFrame(ct.Structure):
    _fields_ = [
        ("timestamp_ms", ct.c_int64),
        ("frame_number", ct.c_uint32),
        ("image_type", ct.c_int),
        ("resolution", ct.c_int),
        ("texture", ct.c_void_p),
        ("flags", ct.c_uint32),
        ("view_area", ct.c_int32 * 3),
    ]


class _LockedRect(ct.Structure):
    _fields_ = [("pitch", ct.c_int), ("size", ct.c_int), ("bits", ct.c_void_p)]


def _check(operation: str, result: int) -> None:
    if result == 0:
        return
    code = result & 0xFFFFFFFF
    status = (
        SensorHealth.NO_DEVICE if code in DISCONNECTED else SensorHealth.DRIVER_ERROR
    )
    raise SensorError(status, f"{operation} (0x{code:08X})")


def _load_runtime():
    if sys.platform != "win32":
        raise SensorError(SensorHealth.DRIVER_ERROR, "Kinect SDK 1.8 kräver Windows.")
    try:
        dll = ct.WinDLL("Kinect10.dll", winmode=LOAD_LIBRARY_SEARCH_SYSTEM32)
        dll.NuiInitialize.argtypes = [win.DWORD]
        dll.NuiShutdown.argtypes = []
        dll.NuiShutdown.restype = None
        dll.NuiImageStreamOpen.argtypes = [
            ct.c_int, ct.c_int, win.DWORD, win.DWORD, win.HANDLE, ct.POINTER(win.HANDLE)
        ]
        dll.NuiImageStreamGetNextFrame.argtypes = [
            win.HANDLE, win.DWORD, ct.POINTER(ct.POINTER(_ImageFrame))
        ]
        dll.NuiImageStreamReleaseFrame.argtypes = [win.HANDLE, ct.POINTER(_ImageFrame)]
    except (OSError, AttributeError) as error:
        raise SensorError(
            SensorHealth.DRIVER_ERROR, "Kinect SDK 1.8 kunde inte laddas."
        ) from error
    return dll


def _decode_depth(buffer, pitch: int) -> NDArray[np.uint16]:
    if pitch < WIDTH * 2 or len(buffer) < (HEIGHT - 1) * pitch + WIDTH * 2:
        raise SensorError(SensorHealth.DRIVER_ERROR, "Felaktig djupbild från Kinect.")
    packed = np.ndarray(
        (HEIGHT, WIDTH), dtype="<u2", buffer=buffer, strides=(pitch, 2)
    )
    depth_mm = packed >> 3
    depth_mm[(depth_mm == 0x0FFF) | (depth_mm == 0x1FFF)] = 0
    return depth_mm


def _copy_depth(texture: int | None) -> NDArray[np.uint16]:
    if not texture:
        raise SensorError(SensorHealth.DRIVER_ERROR, "Kinect gav en tom djupbild.")
    # INuiFrameTexture inherits the three IUnknown slots. See SDK NuiSensor.h.
    table = ct.cast(texture, ct.POINTER(ct.POINTER(ct.c_void_p))).contents
    lock = ct.WINFUNCTYPE(
        ct.c_long, ct.c_void_p, ct.c_uint, ct.POINTER(_LockedRect),
        ct.c_void_p, win.DWORD
    )(table[5])
    unlock = ct.WINFUNCTYPE(ct.c_long, ct.c_void_p, ct.c_uint)(table[7])
    rect = _LockedRect()
    _check("LockRect", lock(texture, 0, ct.byref(rect), None, 0))
    try:
        if not rect.bits or rect.size <= 0:
            raise SensorError(SensorHealth.DRIVER_ERROR, "Kinect gav en tom djupbild.")
        raw = (ct.c_ubyte * rect.size).from_address(rect.bits)
        return _decode_depth(raw, rect.pitch)
    finally:
        _check("UnlockRect", unlock(texture, 0))


class KinectV1Sensor:
    """The process-wide SDK stream. Use one instance on the calling thread."""

    def __init__(self) -> None:
        self._dll = None
        self._stream = win.HANDLE()
        self._health = SensorHealth.NO_FRAMES
        self._frame_number: int | None = None
        self._dropped = 0
        self.device_timestamp_ms: int | None = None

    def start(self) -> None:
        if self._dll is not None:
            return
        try:
            dll = _load_runtime()
            _check("NuiInitialize", dll.NuiInitialize(USES_DEPTH))
            try:
                _check(
                    "NuiImageStreamOpen",
                    dll.NuiImageStreamOpen(
                        IMAGE_DEPTH, RESOLUTION_320X240, 0, 2, None,
                        ct.byref(self._stream)
                    ),
                )
            except BaseException:
                dll.NuiShutdown()
                raise
        except SensorError as error:
            self._health = error.status
            raise
        self._dll = dll
        self._health = SensorHealth.NO_FRAMES
        self._frame_number = None
        self._dropped = 0
        self.device_timestamp_ms = None

    def read_latest(self, timeout_s: float) -> SensorFrame | None:
        if self._dll is None:
            return None
        frame = ct.POINTER(_ImageFrame)()
        timeout_ms = min(0xFFFFFFFE, max(0, ceil(timeout_s * 1000)))
        try:
            result = self._dll.NuiImageStreamGetNextFrame(
                self._stream, timeout_ms, ct.byref(frame)
            )
            if result == 1 or result & 0xFFFFFFFF == NO_FRAME:
                self._health = SensorHealth.NO_FRAMES
                return None
            _check("NuiImageStreamGetNextFrame", result)
            if not frame:
                raise SensorError(
                    SensorHealth.DRIVER_ERROR, "Kinect gav ingen bildpekare."
                )
            timestamp = monotonic()
            try:
                image = frame.contents
                depth = _copy_depth(image.texture)
                number = image.frame_number
                self.device_timestamp_ms = image.timestamp_ms
            finally:
                _check(
                    "NuiImageStreamReleaseFrame",
                    self._dll.NuiImageStreamReleaseFrame(self._stream, frame),
                )
        except SensorError as error:
            self._health = error.status
            raise
        if self._frame_number is not None:
            advance = (number - self._frame_number) & 0xFFFFFFFF
            if 1 < advance < 0x80000000:
                self._dropped += advance - 1
        self._frame_number = number
        self._health = SensorHealth.OK
        return SensorFrame(
            timestamp, depth, None, WIDTH, HEIGHT, "kinect_v1", self._dropped
        )

    def health(self) -> SensorHealth:
        return self._health

    def stop(self) -> None:
        if self._dll is not None:
            self._dll.NuiShutdown()
            self._dll = None
            self._stream = win.HANDLE()
        self._health = SensorHealth.NO_FRAMES
