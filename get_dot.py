import tortilla_pb2
import comal_pb2
from google.protobuf import text_format
import pydot
import argparse
from utils import process_proto

def process():
    parser = argparse.ArgumentParser(
                    prog='Tortilla Visualizer',
                    description='Converts samml protobuf output to dot png')
    parser.add_argument('-f', '--file', required=True)
    parser.add_argument('-o', '--outfile', default='graph.png')
    args = parser.parse_args()
    with open(args.file, "r") as f:
        proto_text = f.read()
    program = comal_pb2.ComalGraph()
    text_format.Parse(proto_text, program)

    result = "digraph SAM {\n"
    result += process_proto(program.graph)
    result += "}"
    # print(result)
    (graph,) = pydot.graph_from_dot_data(result)
    out_file = args.outfile
    graph.write_png(out_file)
    print("Generated graph in: " + out_file)


process()
