import os

def test_func(input_path, output_path):
    my_list = os.listdir(input_path)
    output_path = os.path.join(output_path, "output.txt")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(my_list))