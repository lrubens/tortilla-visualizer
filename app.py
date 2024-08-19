from flask import Flask, request, render_template
from flask_cors import CORS
from google.protobuf import text_format
import tortilla_pb2
import comal_pb2
from utils import process_proto

app = Flask(__name__)
CORS(app)


@app.route('/process', methods=['POST'])
def process():
    proto_text = request.data

    # Parse the protobuf text proto.
    program = comal_pb2.ComalGraph()
    text_format.Parse(bytes.decode(proto_text), program)

    # Process the protobuf message.
    result = "digraph SAM {\n"
    result += process_proto(program.graph)
    result += "}"

    return result


if __name__ == '__main__':
    app.run(port=5000)
