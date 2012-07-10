from automata_view.automataview import states_to_dot
import tempfile, os

# check if list2 is suffix of list1
def is_suffix(list1, list2):
    if len(list2) > len(list1):
        return False
    for (n2, n1) in zip(reversed(list2), reversed(list1)):
        if n2 != n1:
            return False
    return True

# convert state machine to a png image file
def to_png(png_name, width, length, states):
    dot_str = states_to_dot(png_name, width, length, states)
    temp_dir = tempfile.gettempdir()
    dot_file_name = temp_dir + os.sep + png_name + '.dot'
    dot_file = open(dot_file_name, 'w')
    dot_file.write(dot_str)
    dot_file.close()
    if not os.path.exists('output'):
        os.mkdir('output')
    img_file_name = 'output' + os.sep + png_name + '.png'
    os.system("dot -Tpng %r > %r" % (dot_file_name, img_file_name))
    os.remove(dot_file_name)
