from cvat.apps.engine.models import TrackedShape
import cv2
import copy
from cvat.settings.base import DATA_ROOT
import os, fnmatch
from cvat.apps.engine.frame_provider import FrameProvider
from cvat.apps.engine.models import Task as TaskModel
from PIL import Image
import numpy as np


def rectangle_to_cv_bbox(rectangle_points):
	"""
	Convert the CVAT rectangle points (serverside) to a OpenCV rectangle.
	:param tuple rectangle_points: Tuple of form (x1,y1,x2,y2)
	:return: Form (x1, y1, width, height)
	"""
	# Dimensions must be ints, otherwise tracking throws a exception
	return (int(rectangle_points[0]), int(rectangle_points[1]),
			int(rectangle_points[2] - rectangle_points[0]),
			int(rectangle_points[3] - rectangle_points[1]))

def cv_bbox_to_rectangle(cv_bbox):
	"""
	Convert the OpenCV bounding box points to a CVAT rectangle points.
	:param tuple cv_bbox: Form (x1, y1, width, height)
	:return: Form (x1,y1,x2,y2)
	"""
	return (cv_bbox[0], cv_bbox[1], cv_bbox[0] + cv_bbox[2], cv_bbox[1] + cv_bbox[3])


def make_image_list(jid, start_frame, stop_frame):
	
	db_task = TaskModel.objects.get(pk=jid)
	# Get image list
	image_list = FrameProvider(db_task.data)
	image_list = image_list.get_frames(image_list.Quality.ORIGINAL)
	count = 0
	for img in image_list:
		if count >= start_frame and count <= stop_frame:
			pil_image = Image.open(img[0])
			opencvImage = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
			yield count, opencvImage
		count +=1
		if count > stop_frame:
			break

class RectangleTracker:
	trackerTypes = ['BOOSTING', 'MIL', 'KCF', 'CSRT', 'MEDIANFLOW', 'TLD',
		'MOSSE', 'GOTRUN']

	def __init__(self, trackerType = "BOOSTING"):
		"""Create tracker.
		:param str trackerType: String specifying tracker, see trackerTypes.
		"""
		trackerTypes_constructor = {
			'BOOSTING': cv2.TrackerBoosting_create,
			'MIL': cv2.TrackerMIL_create,
			'KCF': cv2.TrackerKCF_create,
			'CSRT': cv2.TrackerCSRT_create,
			'MEDIANFLOW': cv2.TrackerMedianFlow_create,
			'TLD': cv2.TrackerTLD_create,
			'MOSSE': cv2.TrackerMOSSE_create,
			'GOTRUN': cv2.TrackerGOTURN_create,
		}
		if trackerType not in trackerTypes_constructor:
			raise Exception("Tracker type not known:" + trackerType)    
		self._tracker = trackerTypes_constructor[trackerType]()

	def track_rectangles(self, jobid, start_shape, start_frame, stop_frame, label_id):
		"""
		Follow an the rectangle in consecutive frames of a task.
		:param jobid: The Django jobid with the images
		:param TrackedShape start_shape: Start tracking with this shape; This
			specifies the frame to start at (start_shape.frame).
		:param int stop_frame: Stop tracking at this frame (excluded).
		:return: List of Shapes (Rectangles) with new shapes.
		"""
		# if not isinstance(start_shape, TrackedShape):
		# 	 raise Exception("start_shape must be of type TrackedShape")    

		# Only track in to future.
		# start_frame = start_shape.frame
		if stop_frame < start_frame:
			return []

		# Load the image iterable for range of frames
		# and init the tracker with the bounding box from the user given shape
		images = make_image_list(jobid, start_frame, stop_frame)
		img0 = next(images)[1]
		bbox = rectangle_to_cv_bbox(start_shape)
		no_error = self._tracker.init(img0, bbox)

		#Generated shapes
		shapes_by_tracking = []
		result = {}
		result[label_id] = []

		for frame, img  in images:
			# Let the tracker find the bounding box in the next image(s)
			no_error, bbox = self._tracker.update(img)
			if no_error:
				# print()
				cv_box = cv_bbox_to_rectangle(bbox)
				result[label_id].append([frame, cv_box[0],cv_box[1],cv_box[2],cv_box[3]])
			
			else:
				break
		return shapes_by_tracking, result