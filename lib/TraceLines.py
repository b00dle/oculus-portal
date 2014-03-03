#!/usr/bin/python

## @file
# Contains class Trace.

# import guacamole libraries
import avango
import avango.gua

import Tools

import time

## Trace class which handles the creating and updating of the trace lines.
#
# Is used by the platforms to draw the trace of their movement.
class Trace:

  ## @var time_offset
  # The time difference in seconds after which a new trace line segment is created.
  time_offset = 0.2   # seconds

  ## Default constructor.
  # @param PARENT_NODE A node in the scene graph to which the line segments are appended.
  # @param ID A numerical ID that is appended to the scene graph name to separate the line segments of multiple instances of this class.
  # @param TRACING_TIME The time line segments should be kept before they disappear.
  # @param INITIAL_MAT This matrix is used as initial position of all line segments.
  def __init__(self, PARENT_NODE, ID, TRACING_TIME, INITIAL_MAT):

    # number of tracelines is calculated such as the line segments are kept the desired TRACING_TIME
    self.num_tracelines = int( round(TRACING_TIME / self.time_offset) )

    # initialize lists, one more point than line segments
    ## @var points
    # A list of the points the line segments are build of.
    self.points = [ INITIAL_MAT.get_translate() ] * (self.num_tracelines + 1)
    ## @var nodes
    # A list of scene graph nodes that contain the line geometry.
    self.nodes  = []

    ## @var transform_node
    # A transform node that is the parent of all line segments. It groups the line segments in the scene graph as the given ID is added to it's name and therefore allows multiple instances of this class.
    self.transform_node = avango.gua.nodes.TransformNode(Name = 'platform_trace_' + str(ID))
    PARENT_NODE.Children.value.append(self.transform_node)

    # create each line segment node by loading the geometry and appending it to the PARENT_NODE
    _loader = avango.gua.nodes.GeometryLoader()
    for i in range(self.num_tracelines - 1):
      self.nodes.append(_loader.create_geometry_from_file('line_geometry', 'data/objects/cube.obj', 'ShadelessGrey', avango.gua.LoaderFlags.DEFAULTS))
      self.transform_node.Children.value.append(self.nodes[i])

    # initalize the timer
    ## @var timer
    # A timer instance to get the current time in seconds.
    self.timer      = avango.nodes.TimeSensor()
    ## @var last_time
    # This variable stores the last time the line segments were updated and is used to check at every update call if the time given in time_offset has passed.
    self.last_time  = self.timer.Time.value


  ## Calculates the transformation matrix of a line segment node in the scene graph.
  def calc_transform_mat(self, START_VEC, END_VEC):

    # calc the vector in between the two points, the resulting center of the line segment and the scaling needed to connect both points
    _vec = avango.gua.Vec3( END_VEC.x - START_VEC.x, END_VEC.y - START_VEC.y, END_VEC.z - START_VEC.z)
    _center = START_VEC + (_vec * 0.5)
    _scale  = 0.5 * _vec.length()
    # calc the rotation according negative z-axis
    _rotation_mat = Tools.get_rotation_between_vectors(avango.gua.Vec3(0, 0, -1), _vec)

    # build the complete matrix
    return avango.gua.make_trans_mat(_center) * _rotation_mat * avango.gua.make_scale_mat(0.05, 0.05, _scale)


  ## Iterates over the line segment nodes and updates them according to the point list.
  def update_scenegraph(self):
    for i in range(self.num_tracelines - 1):
      self.nodes[i].Transform.value = self.calc_transform_mat(self.points[i], self.points[i + 1])

  ## Update function that updates the point list whenever the time_offset was reached.
  def update(self, ABS_MAT):

    # only update when time_offset is reached
    if self.timer.Time.value > self.last_time + self.time_offset:
    
      # copy every point in the point list one to the left
      for i in range(self.num_tracelines):
        self.points[i] = self.points[i + 1]

      # last point of the point list is set to new matrix
      self.points[self.num_tracelines] = ABS_MAT.get_translate()

      self.update_scenegraph()

      # current time stored for time_offset check
      self.last_time = self.timer.Time.value
