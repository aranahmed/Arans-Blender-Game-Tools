import hou


obj_level = hou.node('/obj')
geo_node = obj_level.createNode('geo')
file_node = geo_node.createNode('file')

path = 'F:/Tools/temp_geo.fbx'

file_node.parm('file').set(path)