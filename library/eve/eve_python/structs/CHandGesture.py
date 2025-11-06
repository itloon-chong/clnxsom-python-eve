import ctypes
from ctypes_enum import CtypesEnum
from .CBasicStructs import *
from .EveProcessingStatus import *

EVE_MAX_HAND_DETECTIONS = 8

EVE_MAX_DYNAMIC_GESTURE_SEQUENCE = 8

EVE_MAX_CUSTOM_STATIC_GESTURES = 20

EVE_MAX_STATIC_GESTURES = 40

EVE_HAND_LANDMARK_SIZE = 11
EVE_STATIC_GESTURE_SIZE = 23
EVE_DYNAMIC_GESTURE_SIZE = 20

class EveHandLandmark(CtypesEnum):
	EVE_WRIST = 0
	EVE_THUMB_IP = 1
	EVE_THUMB_TIP = 2
	EVE_INDEX_MCP = 3
	EVE_INDEX_TIP = 4
	EVE_MIDDLE_MCP = 5
	EVE_MIDDLE_TIP = 6
	EVE_RING_MCP = 7
	EVE_RING_TIP = 8
	EVE_PINKY_MCP = 9
	EVE_PINKY_TIP = 10
	EVE_HAND_LANDMARK_SIZE = 11

class EveGestureQuality(CtypesEnum):
	EVE_POOR_QUALITY_LOW_CONFIDENCE = 0
	EVE_POOR_QUALITY_HAND_OVER_FACE = 1
	EVE_GOOD_QUALITY = 2

class EveStaticGestureType(CtypesEnum):
	EVE_STATIC_GESTURE_NONE = 0
	EVE_OPEN_HAND = 1
	EVE_OPEN_HAND_LEFT = 2
	EVE_OPEN_HAND_RIGHT = 3
	EVE_CLOSED_HAND = 4
	EVE_POINT_UP = 5
	EVE_POINT_DOWN = 6
	EVE_PINCH = 7
	EVE_THUMBS_UP = 8
	EVE_THUMBS_DOWN = 9
	EVE_THUMBS_LEFT = 10
	EVE_THUMBS_RIGHT = 11
	EVE_RESERVED_STATIC_GESTURE_1 = 12
	EVE_CUSTOM_STATIC_GESTURE_1 = 13
	EVE_CUSTOM_STATIC_GESTURE_2 = 14
	EVE_CUSTOM_STATIC_GESTURE_3 = 15
	EVE_CUSTOM_STATIC_GESTURE_4 = 16
	EVE_CUSTOM_STATIC_GESTURE_5 = 17
	EVE_CUSTOM_STATIC_GESTURE_6 = 18
	EVE_CUSTOM_STATIC_GESTURE_7 = 19
	EVE_CUSTOM_STATIC_GESTURE_8 = 20
	EVE_CUSTOM_STATIC_GESTURE_9 = 21
	EVE_CUSTOM_STATIC_GESTURE_10 = 22
	EVE_STATIC_GESTURE_SIZE = 23

class EveDynamicGestureType(CtypesEnum):
	EVE_DYNAMIC_GESTURE_NONE = 0
	EVE_GRAB = 1
	EVE_FLICK_UP = 2
	EVE_CLICK = 3
	EVE_RESERVED_DYNAMIC_GESTURE_1 = 4
	EVE_RESERVED_DYNAMIC_GESTURE_2 = 5
	EVE_RESERVED_DYNAMIC_GESTURE_3 = 6
	EVE_RESERVED_DYNAMIC_GESTURE_4 = 7
	EVE_RESERVED_DYNAMIC_GESTURE_5 = 8
	EVE_RESERVED_DYNAMIC_GESTURE_6 = 9
	EVE_CUSTOM_DYNAMIC_GESTURE_1 = 10
	EVE_CUSTOM_DYNAMIC_GESTURE_2 = 11
	EVE_CUSTOM_DYNAMIC_GESTURE_3 = 12
	EVE_CUSTOM_DYNAMIC_GESTURE_4 = 13
	EVE_CUSTOM_DYNAMIC_GESTURE_5 = 14
	EVE_CUSTOM_DYNAMIC_GESTURE_6 = 15
	EVE_CUSTOM_DYNAMIC_GESTURE_7 = 16
	EVE_CUSTOM_DYNAMIC_GESTURE_8 = 17
	EVE_CUSTOM_DYNAMIC_GESTURE_9 = 18
	EVE_CUSTOM_DYNAMIC_GESTURE_10 = 19
	EVE_DYNAMIC_GESTURE_SIZE = 20

class EveStaticGesture(ctypes.Structure):
	_fields_ = [
		("handId", ctypes.c_int),
		("isMainUserHand", ctypes.c_int),
		("type", ctypes.c_int),
		("confidence", ctypes.c_float),
		("quality", ctypes.c_int),
	]

class EveStaticGestures(ctypes.Structure):
	_fields_ = [
		("count", ctypes.c_uint),
		("gestures", EveStaticGesture * EVE_MAX_HAND_DETECTIONS),
	]

class EveStaticGestureDefinition(ctypes.Structure):
	_fields_ = [
		("gestureType", ctypes.c_int),
		("id", ctypes.c_uint),
		("landmarksMap", CPoint2f * EVE_HAND_LANDMARK_SIZE),
	]

class EveDynamicGesture(ctypes.Structure):
	_fields_ = [
		("handId", ctypes.c_int),
		("isMainUserHand", ctypes.c_int),
		("type", ctypes.c_int),
		("quality", ctypes.c_int),
	]

class EveDynamicGestures(ctypes.Structure):
	_fields_ = [
		("count", ctypes.c_uint),
		("gestures", EveDynamicGesture * EVE_MAX_HAND_DETECTIONS),
	]

class EveDynamicGestureDefinition(ctypes.Structure):
	_fields_ = [
		("gestureType", ctypes.c_int),
		("sequenceCount", ctypes.c_uint),
		("gestureSequence", ctypes.c_int * EVE_MAX_DYNAMIC_GESTURE_SEQUENCE),
	]

class EveSingleHandDetection(ctypes.Structure):
	_fields_ = [
		("id", ctypes.c_int),
		("boundingBox", CRect2iWH),
		("boundingBoxScore", ctypes.c_float),
		("landmarksICS", CPoint2f * EVE_HAND_LANDMARK_SIZE),
		("validationScore", ctypes.c_float),
		("inPlaneAngle", ctypes.c_float),
		("depth", ctypes.c_float),
		("isMainUserHand", ctypes.c_int),
		("isInCurrentFrame", ctypes.c_int),
	]

class EveHandDetections(ctypes.Structure):
	_fields_ = [
		("status", ctypes.c_int),
		("hasFaceROI", ctypes.c_int),
		("faceROI", CRect2fWH),
		("detectedHandCount", ctypes.c_uint),
		("hands", EveSingleHandDetection * EVE_MAX_HAND_DETECTIONS),
	]

