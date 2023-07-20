import ops_pb2
import tortilla_pb2
import stream_pb2
from google.protobuf import text_format


def parse_prototext_file(filename):
    program = tortilla_pb2.ProgramGraph()

    #debugging field attributes
    # res = [field.name for field in program.DESCRIPTOR.fields]
    # print(res)

    print("Hello")
    with open(filename, 'r') as file:
        text_proto = file.read()
        # print(text_proto)
        try:
            text_format.Parse(text_proto, program)
        except text_format.ParseError as e:
            print(f"Error parsing prototext: {e}")
            return
    print("Bye")

    program_name = program.name
    operators = program.operators

    for operator in operators:
        operator_name = operator.name
        operator_id = operator.id
        operator_op = operator.WhichOneof("op")

        if operator_op == "broadcast":
            broadcast_op = operator.broadcast
            # print(broadcast_op.output)
            input_id = broadcast_op.input.id
            output_id = broadcast_op.output[0].id

            #printing broadcast operators
            # print(f"Operator: {operator_name}")
            # print(f"ID: {operator_id}")
            # print(f"Input ID: {input_id}")
            # print(f"Output ID: {output_id}")
        print(operator)


# Provide the path to the prototext file
filename = "visualizeSAM.textproto"

parse_prototext_file(filename)
