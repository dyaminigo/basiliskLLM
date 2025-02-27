"""Test module for MessageSegmentManager class.

This module contains unit tests for verifying the functionality of the
MessageSegmentManager class and its operations on MessageSegment objects.
"""

import unittest

from basilisk.message_segment_manager import (
	MessageSegment,
	MessageSegmentManager,
	MessageSegmentType,
)


class TestMessagePositionManager(unittest.TestCase):
	"""Test cases for MessageSegmentManager class.

	This test suite verifies the behavior of MessageSegmentManager including
	navigation, manipulation, and state management of message segments.
	"""

	def setUp(self):
		"""Initialize test fixtures.

		Creates a MessageSegmentManager instance with three test segments:
		- Content segment of length 7
		- Prefix segment of length 14
		- Content segment of length 21
		"""
		self.segments = [
			MessageSegment(length=7, kind=MessageSegmentType.CONTENT),
			MessageSegment(length=14, kind=MessageSegmentType.PREFIX),
			MessageSegment(length=21, kind=MessageSegmentType.CONTENT),
		]
		self.manager = MessageSegmentManager(self.segments)

	def test_initial_state(self):
		"""Test the initial state of the MessageSegmentManager.

		Verifies that both position and absolute_position start at 0.
		"""
		self.assertEqual(self.manager.position, 0, "Initial index should be 0")
		self.assertEqual(
			self.manager.absolute_position,
			0,
			"Initial absolute position should be 0",
		)

	def test_next(self):
		"""Test the next() method for basic movement.

		Verifies moving to the next segment updates position and boundaries correctly.
		"""
		self.manager.next()
		self.assertEqual(self.manager.position, 1)
		self.assertEqual(self.manager.start, 7)
		self.assertEqual(self.manager.end, 7 + 14)

	def test_next_with_type(self):
		"""Test the next() method with type filtering.

		Verifies moving to the next segment of a specific type works correctly.
		"""
		self.manager.next(MessageSegmentType.CONTENT)
		self.assertEqual(self.manager.position, 2)
		self.assertEqual(self.manager.start, 7 + 14)
		self.assertEqual(self.manager.end, 7 + 14 + 21)

	def test_next_with_type_not_found(self):
		"""Test the next() method with non-existent type.

		Verifies appropriate exception is raised when type is not found.
		"""
		self.manager.position = len(self.segments) - 1
		with self.assertRaises(IndexError):
			self.manager.next("nonexistent_type")

	def test_previous(self):
		"""Test the previous() method for basic movement.

		Verifies moving to the previous segment updates position and boundaries correctly.
		"""
		self.manager.next()
		self.manager.next()
		self.manager.previous()
		self.assertEqual(self.manager.position, 1)
		self.assertEqual(self.manager.start, 7)
		self.assertEqual(self.manager.end, 7 + 14)

	def test_previous_with_type(self):
		"""Test the previous() method with type filtering.

		Verifies moving to the previous segment of a specific type works correctly.
		"""
		self.manager.next()
		self.manager.next()
		self.manager.previous(MessageSegmentType.PREFIX)
		self.assertEqual(self.manager.position, 1)
		self.assertEqual(self.manager.start, 7)
		self.assertEqual(self.manager.end, 7 + 14)

	def test_previous_with_type_not_found(self):
		"""Test the previous() method with non-existent type.

		Verifies appropriate exception is raised when type is not found.
		"""
		with self.assertRaises(IndexError):
			self.manager.previous("nonexistent_type")

	def test_insert(self):
		"""Test segment insertion.

		Verifies that inserting a new segment maintains correct positions and boundaries.
		"""
		new_position = MessageSegment(length=5, kind=MessageSegmentType.PREFIX)
		self.manager.insert(2, new_position)
		self.assertEqual(self.manager.segments[2], new_position)
		self.assertEqual(self.manager.start, 0)
		self.assertEqual(self.manager.end, 7)
		self.assertEqual(self.manager.segments[3].length, 7 + 14)
		self.manager.position = 3
		self.assertEqual(self.manager.start, 7 + 5 + 14)
		self.assertEqual(self.manager.end, 7 + 5 + 14 + 21)

	def test_append(self):
		"""Test segment appending.

		Verifies that appending a new segment maintains correct list state.
		"""
		new_position = MessageSegment(length=28, kind=MessageSegmentType.PREFIX)
		self.manager.append(new_position)
		self.assertEqual(self.manager.segments[-1], new_position)
		self.assertEqual(self.manager.start, 0)
		self.assertEqual(self.manager.end, 7)

	def test_remove(self):
		"""Test segment removal.

		Verifies that removing a segment maintains correct list state.
		"""
		position_to_remove = self.segments[1]
		self.manager.remove(position_to_remove)
		self.assertNotIn(position_to_remove, self.manager.segments)
		self.assertEqual(self.manager.start, 0)
		self.assertEqual(self.manager.end, 7)

	def test_absolute_position_setter(self):
		"""Test absolute position setter.

		Verifies that setting absolute position correctly updates internal state
		and handles boundary conditions.
		"""
		self.manager.absolute_position = 0
		self.assertEqual(self.manager.position, 0)
		self.assertEqual(self.manager.start, 0)
		self.assertEqual(self.manager.end, 7)
		self.manager.absolute_position = 7
		self.assertEqual(self.manager.position, 1)
		self.assertEqual(self.manager.start, 7)
		self.assertEqual(self.manager.end, 7 + 14)
		self.manager.absolute_position = 20
		self.assertEqual(self.manager.position, 1)
		self.assertEqual(self.manager.start, 7)
		self.assertEqual(self.manager.end, 7 + 14)
		self.manager.absolute_position = 7 + 14 + 21
		self.assertEqual(self.manager.position, 2)
		self.assertEqual(self.manager.absolute_position, 42)
		with self.assertRaises(ValueError):
			self.manager.absolute_position = -1
		self.manager.absolute_position = 1024
		self.assertEqual(self.manager.absolute_position, 42)

	def test_out_of_bounds_positions(self):
		"""Test position bounds checking.

		Verifies that setting invalid positions raises appropriate exceptions.
		"""
		with self.assertRaises(ValueError):
			self.manager.position = -1
		with self.assertRaises(ValueError):
			self.manager.position = len(self.segments)

	def test_str_repr(self):
		"""Test string representation.

		Verifies correct string formatting of the manager state.
		"""
		self.assertEqual(str(self.manager), "MessageBlockPosition(0/3)")
		self.assertEqual(repr(self.manager), "MessageBlockPosition(0/3)")

	def test_iteration_and_indexing(self):
		"""Test iteration and indexing operations.

		Verifies that the manager supports proper iteration and index access.
		"""
		expected = self.segments[0]
		self.assertEqual(self.manager[0], expected)
		self.assertEqual(len(self.manager), len(self.segments))
		for pos in self.manager:
			self.assertIn(pos, self.segments)

	def test_focus_content_block_prefix(self):
		"""Test focusing content block from prefix position.

		Verifies correct movement to content block when starting from prefix.
		"""
		self.manager.position = 1
		self.manager.focus_content_block()
		self.assertEqual(self.manager.position, 2)

	def test_focus_content_block_suffix(self):
		"""Test focusing content block from suffix position.

		Verifies correct movement to content block when starting from suffix.
		"""
		self.manager.append(
			MessageSegment(length=10, kind=MessageSegmentType.SUFFIX)
		)
		self.manager.position = 3
		self.manager.focus_content_block()
		self.assertEqual(self.manager.position, 2)

	def test_focus_content_block_noop(self):
		"""Test focusing content block when already on content.

		Verifies no position change when already on a content block.
		"""
		self.manager.focus_content_block()
		self.assertEqual(self.manager.position, 0)

	def test_empty_segments(self):
		"""Test operations on empty segment list.

		Verifies proper exception handling with no segments.
		"""
		manager = MessageSegmentManager([])
		with self.assertRaises(IndexError):
			manager.next()
		with self.assertRaises(IndexError):
			manager.previous()

	def test_single_segment_next(self):
		"""Test next() with single segment.

		Verifies proper exception handling when moving past single segment.
		"""
		manager = MessageSegmentManager(
			[MessageSegment(length=7, kind=MessageSegmentType.CONTENT)]
		)
		with self.assertRaises(IndexError):
			manager.next()

	def test_single_segment_previous(self):
		"""Test previous() with single segment.

		Verifies proper exception handling when moving before single segment.
		"""
		manager = MessageSegmentManager(
			[MessageSegment(length=7, kind=MessageSegmentType.CONTENT)]
		)
		with self.assertRaises(IndexError):
			manager.previous()

	def test_current_segment(self):
		"""Test current segment accessor.

		Verifies correct segment is returned for current position.
		"""
		self.assertEqual(self.manager.current_segment, self.segments[0])
		self.manager.next()
		self.assertEqual(self.manager.current_segment, self.segments[1])

	def test_position_setter_invalid(self):
		"""Test invalid position setting.

		Verifies appropriate exceptions for invalid position values.
		"""
		with self.assertRaises(ValueError):
			self.manager.position = -1
		with self.assertRaises(ValueError):
			self.manager.position = 100

	def test_absolute_position_setter_large(self):
		"""Test setting large absolute position.

		Verifies handling of absolute position values beyond segment bounds.
		"""
		self.manager.absolute_position = 999
		self.assertEqual(self.manager.absolute_position, 42)

	def test_getitem_setitem_delitem(self):
		"""Test item access operations.

		Verifies get, set, and delete operations on segments work correctly.
		"""
		segment = MessageSegment(length=50, kind=MessageSegmentType.SUFFIX)
		self.manager[1] = segment
		self.assertEqual(self.manager[1], segment)

		del self.manager[1]
		self.assertNotIn(segment, self.manager.segments)
		self.assertEqual(len(self.manager), 2)

	def test_clear(self):
		"""Test clearing all segments.

		Verifies manager state after removing all segments.
		"""
		self.manager.clear()
		self.assertEqual(len(self.manager.segments), 0)
		self.assertEqual(self.manager.position, -1)
		self.assertEqual(self.manager.absolute_position, -1)

	def test_insert_at_beginning(self):
		"""Test insertion at start of list.

		Verifies correct state updates when inserting at position 0.
		"""
		segment = MessageSegment(length=5, kind=MessageSegmentType.PREFIX)
		self.manager.insert(0, segment)
		self.assertEqual(self.manager[0], segment)
		self.assertEqual(self.manager.position, 0)
		self.assertEqual(self.manager.absolute_position, 5)

	def test_multiple_content_segments(self):
		"""Test navigation with multiple content segments.

		Verifies correct movement between content segments.
		"""
		self.segments.append(
			MessageSegment(length=10, kind=MessageSegmentType.CONTENT)
		)
		self.manager = MessageSegmentManager(self.segments)
		self.manager.position = 1
		self.manager.next(MessageSegmentType.CONTENT)
		self.assertEqual(self.manager.position, 2)
		self.manager.next(MessageSegmentType.CONTENT)
		self.assertEqual(self.manager.position, 3)


if __name__ == "__main__":
	unittest.main()
