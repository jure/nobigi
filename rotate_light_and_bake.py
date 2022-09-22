import bpy, os, math
from mathutils import Euler, Vector
res = 512

output_dir = 'C:\\Users\\Jure\\Documents\\MLGIBakes\\pbakes2'
output_pattern  = '%s%s_%s_%s.jpg'

print(bpy.context.scene.objects)

def image():
    print(bpy.data.images)
    if 'baking' in bpy.data.images:
        img = bpy.data.images['baking']
        bpy.data.images.remove(img)

    # Baking image
    img = bpy.data.images.new('baking', int(res), int(res), alpha=False, float_buffer=True)
    img.source = 'GENERATED'
    return img

# If TEST is true, no images will be baked, instead lights will be created in the positions in
# which they would be, if we were really baking. This allows you to test your setttings.
TEST = True
levels = 10
density = 2
radius = 2
covering = 90/180; # how much of the angle is covered
covering_offset = 45/180;
z_offset = math.pi/16 # total angle
target_name = 'Empty'

obj_to_bake = ['Coffee Cup', 'Coffee Spoon', 'Coffee Plate', 'Plane001', 'Plane002', 'Plane003']
if TEST:
    obj_to_bake = obj_to_bake[:1] # We only need one object when testing

for obj in bpy.context.scene.objects:
    if obj.name in obj_to_bake:
        img = image()
        img_node = False
        for slot in obj.material_slots:
            mat = slot.material
            mat.use_nodes = True
            nodes = mat.node_tree.nodes

            if "Baked Image" in nodes:
                img_node = nodes["Baked Image"]
                img_node.image = img
            else:
                img_node = nodes.new('ShaderNodeTexImage')
                img_node.name = 'Baked Image'
                img_node.location = (100, 100)
                img_node.select = True
                img_node.image = img
            nodes.active = img_node



        light = bpy.context.scene.objects.get('Light')

        target_obj = bpy.data.objects[target_name]
        target_origin = target_obj.location

        numImages= 0
        for l in range(0, 2*levels):
            zAngle = (l / levels) * (z_offset)
            if(levels != 0):
                leveled_z = radius * math.sin(zAngle)
            else:
                leveled_z = 0
            z = target_origin.z + leveled_z

            for angle in [(i * covering * math.pi) / density for i in range(0, density + 1)]:
                # estimate new direction based on the angle in the unit circle
                angle = angle - 1/4 * math.pi - covering_offset * math.pi;
                d = Vector((math.cos(angle), math.sin(angle)))
                (x, y) = Vector((target_origin.x, target_origin.y)) + (radius * math.cos(zAngle)) * d
                # build absolute position
                position = (x, y, z)

                light.location = Vector(position)
                ttc = light.constraints.new(type='TRACK_TO')
                ttc.target = target_obj
                ttc.track_axis = 'TRACK_NEGATIVE_Z'
                ttc.up_axis = 'UP_Y'
                bpy.ops.object.select_all(action='DESELECT')
                light.select_set(True)
                bpy.ops.object.visual_transform_apply()
                light.rotation_euler.z = light.rotation_euler.z % 360

                z_rot = light.rotation_euler.z
                x_rot = light.rotation_euler.x


                if TEST:
                    name = 'LightTest' + str(numImages)
                    light_data = bpy.data.lights.new(name, type="SUN")
                    light_obj = bpy.data.objects.new(name=name, object_data=light_data)
                    bpy.context.collection.objects.link(light_obj)
                    light_obj.location = Vector(position)
                    light_obj.rotation_euler = light.rotation_euler
                    # print(x_rot, z_rot)
                else:
                    # Bake it yo
                    bpy.ops.object.select_all(action='DESELECT')
                    obj.select_set(True)
                    img.filepath = os.path.join(output_dir, (output_pattern % ('d', obj.name, f"{x_rot:+.8f}", f"{z_rot:+.8f}")))
                    bpy.ops.object.bake(type="DIFFUSE", pass_filter={"DIRECT", 'INDIRECT'}, use_clear=False)
                    img.save()
                    img.source = 'GENERATED'
                    print("Saved " + str(numImages))

                numImages = numImages + 1