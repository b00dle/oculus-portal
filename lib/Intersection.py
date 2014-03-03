#!/usr/bin/python

## @file
# Contains class Intersection.

# import guacamole libraries
import avango
import avango.gua
import avango.script

# import python libraries
import math
import numpy

## Helper class to determine the intersections of a ray with the objects in
# a scene.

class Intersection(avango.script.Script):

  # input fields
  ## @var sf_pick_mat
  # Starting matrix of the ray to be analyzed.
  sf_pick_mat = avango.gua.SFMatrix4()

  # output fields
  ## @var mf_pick_result
  # Intersections of the ray with the objects in the scene.
  mf_pick_result = avango.gua.MFPickResult()

  # attributes
  ## @var activated
  # Indicates if the intersection computation is activated or not. In the last case,
  # nothing will be written in mf_pick_result.
  activated = True

  ## Default constructor.
  def __init__(self):
    self.super(Intersection).__init__()

  ## Custom constructor.
  # @param SCENEGRAPH The scenegraph where to look for intersections of the ray.
  # @param SF_MAT Starting matrix of the ray.
  # @param PICK_LENGTH Length of the ray in meters.
  # @param PICK_DIRECTION Direction of the ray.
  def my_constructor(self, SCENEGRAPH, SF_MAT, PICK_LENGTH, PICK_DIRECTION):
    
    ## @var SCENEGRAPH
    # Reference to the scenegraph.
    self.SCENEGRAPH = SCENEGRAPH
  
    # set initial parameters
    self.set_pick_length(PICK_LENGTH)
    self.set_pick_direction(PICK_DIRECTION)
  
    ## @var ray
    # The spatial ray to be analyzed.
    self.ray = avango.gua.nodes.RayNode()
  
    ## @var picking_options
    # Picking options for the intersection process.
    self.picking_options = avango.gua.PickingOptions.PICK_ONLY_FIRST_OBJECT \
                         | avango.gua.PickingOptions.GET_WORLD_NORMALS \
                         | avango.gua.PickingOptions.INTERPOLATE_NORMALS \
                         | avango.gua.PickingOptions.PICK_ONLY_FIRST_FACE
    
    ## @var picking_mask
    # Picking mask of the intersection process.
    self.picking_mask = ""
  
    # init field connections
    self.sf_pick_mat.connect_from(SF_MAT)
  
    self.always_evaluate(True)
    
  ## Evaluated every frame.
  def evaluate(self):
    if self.activated:

      # update interscetion ray parameters
      _ref_vec = avango.gua.Vec3(0.0,0.0,-1.0)
     
      _angle = math.acos(self.dot(_ref_vec, self.pick_direction))
      _angle = math.degrees(_angle)
     
      _axis = self.cross(_ref_vec, self.pick_direction)
         
      self.ray.Transform.value = avango.gua.make_trans_mat(self.sf_pick_mat.value.get_translate()) * \
                                  avango.gua.make_rot_mat(_angle, _axis) * \
                                  avango.gua.make_scale_mat(self.pick_length,self.pick_length,self.pick_length)
          
      # compute picking results
      _pick_result = self.SCENEGRAPH.ray_test(self.ray, self.picking_options, self.picking_mask)
      self.mf_pick_result.value = _pick_result.value


  ## Sets the pick_length attribute.
  # @param PICK_LENGTH New pick length.
  def set_pick_length(self, PICK_LENGTH):
    ## @var pick_length
    # Length of the ray in meters.
    self.pick_length = PICK_LENGTH

  ## Sets the pick_direction attribute.
  # @param PICK_DIRECTION New pick direction.
  def set_pick_direction(self, PICK_DIRECTION):
    ## @var pick_direction
    # Direction of the ray.
    self.pick_direction = PICK_DIRECTION
    self.pick_direction.normalize()
  
  ## Dot prodcut between two vectors.
  # @param VEC1 Left vector.
  # @param VEC2 Right vector.
  def dot(self, VEC1, VEC2):
    _dot = numpy.dot( (VEC1.x,VEC1.y,VEC1.z), (VEC2.x,VEC2.y,VEC2.z))
    return _dot

  ## Cross prodcut between two vectors.
  # @param VEC1 Left vector.
  # @param VEC2 Right vector.
  def cross(self, VEC1, VEC2):
    _cross = numpy.cross( (VEC1.x,VEC1.y,VEC1.z), (VEC2.x,VEC2.y,VEC2.z))
    return avango.gua.Vec3(_cross[0], _cross[1], _cross[2])

  ## Activate the intersection procedure.
  def activate(self):
    self.activated = True

  ## Deactivate the intersection procedure.
  def deactivate(self):
    self.activated = False
