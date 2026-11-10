"""Depth and optional mirror color using Microsoft Kinect SDK 1.8."""

import ctypes as ct
import sys
from collections.abc import Callable
from ctypes import wintypes as win
from math import ceil
from time import monotonic

import numpy as np
from numpy.typing import NDArray

from .base import SensorFrame, SensorHealth

WIDTH, HEIGHT = 320, 240
USES_DEPTH = 0x20
USES_COLOR = 0x02
IMAGE_DEPTH = 4
IMAGE_COLOR = 1
RESOLUTION_320X240 = 1
RESOLUTION_640X480 = 2
NO_FRAME = 0x83010001
DISCONNECTED = {0x83010014, 0x83010015, 0x8301027F, 0x8007048F}
LOAD_LIBRARY_SEARCH_SYSTEM32 = 0x800
TILT_MIN = -27
TILT_MAX = 27
RGB_MAX_SKEW_MS = 25
COLOR_SUPPORT_RADIUS = 3


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
        dll.NuiCameraElevationGetAngle.argtypes = [ct.POINTER(win.LONG)]
        dll.NuiCameraElevationSetAngle.argtypes = [win.LONG]
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


def _decode_color(buffer, pitch: int) -> NDArray[np.uint8]:
    width, height = WIDTH * 2, HEIGHT * 2
    if pitch < width * 4 or len(buffer) < (height - 1) * pitch + width * 4:
        raise SensorError(SensorHealth.DRIVER_ERROR, "Felaktig färgbild från Kinect.")
    bgrx = np.ndarray(
        (height, width, 4), dtype=np.uint8, buffer=buffer, strides=(pitch, 4, 1)
    )
    return bgrx[::2, ::2, 2::-1].copy()


def _copy_texture(texture: int | None, decode: Callable) -> NDArray:
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
        return decode(raw, rect.pitch)
    finally:
        _check("UnlockRect", unlock(texture, 0))


def _copy_depth(texture: int | None) -> NDArray[np.uint16]:
    return _copy_texture(texture, _decode_depth)


class _ColorRegistration:
    def __init__(self, dll) -> None:
        create = dll.NuiCreateSensorByIndex
        create.argtypes = [ct.c_int, ct.POINTER(ct.c_void_p)]
        self._sensor = ct.c_void_p()
        _check("NuiCreateSensorByIndex", create(0, ct.byref(self._sensor)))
        if not self._sensor:
            raise SensorError(SensorHealth.DRIVER_ERROR, "Kinect saknar färgmappning.")
        # INuiSensor slots 2 and 13 (Release and frame mapping) in SDK NuiSensor.h.
        table = ct.cast(self._sensor, ct.POINTER(ct.POINTER(ct.c_void_p))).contents
        self._release = ct.WINFUNCTYPE(win.ULONG, ct.c_void_p)(table[2])
        self._map = ct.WINFUNCTYPE(
            ct.c_long, ct.c_void_p, ct.c_int, ct.c_int,
            win.DWORD, ct.c_void_p, win.DWORD, ct.c_void_p,
        )(table[13])

    def coordinates(self, depth: NDArray[np.uint16]) -> NDArray[np.int32] | None:
        # At an unmeasured edge, project at the closest nearby playable depth.
        # The foreground tracker still requires a verified foreground neighbour.
        radius = COLOR_SUPPORT_RADIUS
        valid = np.where((depth >= 850) & (depth <= 3800), depth, 4095)
        rows = np.pad(valid, ((0, 0), (radius, radius)), constant_values=4095)
        nearby = np.minimum.reduce(
            [rows[:, i:i + WIDTH] for i in range(2 * radius + 1)]
        )
        columns = np.pad(nearby, ((radius, radius), (0, 0)), constant_values=4095)
        nearby = np.minimum.reduce(
            [columns[i:i + HEIGHT] for i in range(2 * radius + 1)]
        )
        packed = nearby << 3
        mapped = np.empty((HEIGHT, WIDTH, 2), dtype=np.int32)
        if self._map(
            self._sensor, RESOLUTION_640X480, RESOLUTION_320X240,
            packed.size, packed.ctypes.data, mapped.size, mapped.ctypes.data,
        ) != 0:
            return None
        # The mirror decoder keeps every second RGB pixel in both directions.
        mapped //= 2
        return mapped

    def close(self) -> None:
        self._release(self._sensor)


class KinectV1Sensor:
    """The process-wide SDK stream. Use one instance on the calling thread."""

    def __init__(self, *, color: bool = False) -> None:
        self._dll = None
        self._stream = win.HANDLE()
        self._color_stream = win.HANDLE()
        self._want_color = color
        self._registration: _ColorRegistration | None = None
        self._latest_color: tuple[int, NDArray[np.uint8]] | None = None
        self._health = SensorHealth.NO_FRAMES
        self._frame_number: int | None = None
        self._dropped = 0
        self.device_timestamp_ms: int | None = None

    def start(self) -> None:
        if self._dll is not None:
            return
        try:
            dll = _load_runtime()
            try:
                self._open(dll, color=self._want_color)
            except SensorError:
                if not self._want_color:
                    raise
                self._open(dll, color=False)
        except SensorError as error:
            self._health = error.status
            raise
        self._dll = dll
        if self._color_stream:
            try:
                self._registration = _ColorRegistration(dll)
            except (SensorError, AttributeError):
                pass
        self._health = SensorHealth.NO_FRAMES
        self._frame_number = None
        self._dropped = 0
        self.device_timestamp_ms = None

    def _open(self, dll, *, color: bool) -> None:
        flags = USES_DEPTH | USES_COLOR if color else USES_DEPTH
        _check("NuiInitialize", dll.NuiInitialize(flags))
        self._stream = win.HANDLE()
        self._color_stream = win.HANDLE()
        try:
            _check(
                "NuiImageStreamOpen",
                dll.NuiImageStreamOpen(
                    IMAGE_DEPTH, RESOLUTION_320X240, 0, 2, None, ct.byref(self._stream)
                ),
            )
            if color:
                _check(
                    "NuiImageStreamOpen color",
                    dll.NuiImageStreamOpen(
                        IMAGE_COLOR, RESOLUTION_640X480, 0, 2, None,
                        ct.byref(self._color_stream)
                    ),
                )
        except BaseException:
            dll.NuiShutdown()
            raise

    def _read_color(self) -> tuple[int, NDArray[np.uint8]] | None:
        if not self._color_stream:
            return None
        frame = ct.POINTER(_ImageFrame)()
        result = self._dll.NuiImageStreamGetNextFrame(
            self._color_stream, 0, ct.byref(frame)
        )
        if result != 0 or not frame:
            return None
        color = None
        try:
            image = frame.contents
            color = image.timestamp_ms, _copy_texture(image.texture, _decode_color)
        except SensorError:
            pass
        finally:
            result = self._dll.NuiImageStreamReleaseFrame(self._color_stream, frame)
        if result != 0:
            self._color_stream = win.HANDLE()
            self._latest_color = None
            return None
        return color

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
        latest = self._read_color()
        if latest is not None:
            self._latest_color = latest
        color = latest[1] if latest is not None else None
        coordinates = None
        if self._latest_color is not None and self._registration is not None:
            color_time, paired_color = self._latest_color
            if abs(color_time - self.device_timestamp_ms) <= RGB_MAX_SKEW_MS:
                coordinates = self._registration.coordinates(depth)
                color = paired_color
        return SensorFrame(
            timestamp, depth, color, WIDTH, HEIGHT, "kinect_v1",
            self._dropped, coordinates,
        )

    def health(self) -> SensorHealth:
        return self._health

    def tilt_angle(self) -> int:
        if self._dll is None:
            raise SensorError(SensorHealth.NO_DEVICE, "Kinect är frånkopplad.")
        angle = win.LONG()
        result = self._dll.NuiCameraElevationGetAngle(ct.byref(angle))
        _check("NuiCameraElevationGetAngle", result)
        return angle.value

    def tilt_to(self, angle: int) -> None:
        if self._dll is None:
            raise SensorError(SensorHealth.NO_DEVICE, "Kinect är frånkopplad.")
        bounded = min(TILT_MAX, max(TILT_MIN, angle))
        result = self._dll.NuiCameraElevationSetAngle(bounded)
        _check("NuiCameraElevationSetAngle", result)

    def stop(self) -> None:
        if self._registration is not None:
            self._registration.close()
            self._registration = None
        self._latest_color = None
        if self._dll is not None:
            self._dll.NuiShutdown()
            self._dll = None
            self._stream = win.HANDLE()
            self._color_stream = win.HANDLE()
        self._health = SensorHealth.NO_FRAMES
