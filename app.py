from flask import Flask, request, render_template
from flask_cors import CORS
from google.protobuf import text_format
import tortilla_pb2

app = Flask(__name__)
CORS(app)


@app.route('/process', methods=['POST'])
def process():
    proto_text = request.data

    # Parse the protobuf text proto.
    program = tortilla_pb2.ProgramGraph()
    text_format.Parse(bytes.decode(proto_text), program)

    # Process the protobuf message.
    result = "digraph SAM {\n"
    result += process_proto(program)
    result += "}"

    return result


def process_proto(program):
    dot = ""
    channel_map = {}

    # add broadcast hooks first since order matters for connections
    for operator in program.operators:
        op = operator.WhichOneof("op")
        op_id = operator.id
        if op == "broadcast":
            bd = operator.broadcast
            bd_conn = {}
            bd_conn["crd"] = bd.crd
            bd_conn["ref"] = bd.ref
            bd_conn["repsig"] = bd.repsig
            bd_conn["val"] = bd.val
            dot += f"{operator.id} [shape=point style=invis type=\"broadcast\"]"
            bd_type = bd.WhichOneof("conn")
            for output in bd_conn[bd_type].outputs:
                channel_map[output.id.id] = operator.id
        elif op == "func":
            intrin = operator.func
            dot += f"{operator.id} [label=\"{intrin.name}\" color=palevioletred2 shape=box style=filled type=\"intrinsic\"]"
            channel_map[intrin.output_val.id.id] = operator.id

    for operator in program.operators:
        op = operator.WhichOneof("op")
        op_id = operator.id
        if op == "fiber_lookup":
            fl = operator.fiber_lookup
            label = fl.label
            dot += f"{operator.id} [label = \"{label}\" color=green4 shape=box style=filled type=\"{operator.name}\" index=\"{fl.index}\" tensor=\"{fl.tensor}\" format=\"{fl.mode}\" src=\"{fl.src}\" root=\"{fl.root}\"]\n"
            if fl.input_ref.id.id in channel_map:
                dot += f"{channel_map[fl.input_ref.id.id]} -> {operator.id} [label=\"ref_in-{fl.tensor}\" style=bold type=\"ref\"]\n"
            channel_map[fl.output_ref.id.id] = operator.id
            channel_map[fl.output_crd.id.id] = operator.id
        elif op == "joiner":
            joiner = operator.joiner
            label = joiner.label
            dot += f"{operator.id} [label = \"{label}\" color=\"#800080\" shape=box style=filled type=\"{operator.name}\" index=\"{joiner.index}\"]\n"
            if joiner.input_pairs[0].crd.id.id in channel_map:
                dot += f"{channel_map[joiner.input_pairs[0].crd.id.id]} -> {operator.id} [label=\"{joiner.input_pairs[0].crd.name}\" style=dashed type=\"crd\"]\n"
            if joiner.input_pairs[0].ref.id.id in channel_map:
                dot += f"{channel_map[joiner.input_pairs[0].ref.id.id]} -> {operator.id} [label=\"{joiner.input_pairs[0].ref.name}\" style=bold type=\"ref\"]\n"
            if joiner.input_pairs[1].crd.id.id in channel_map:
                dot += f"{channel_map[joiner.input_pairs[1].crd.id.id]} -> {operator.id} [label=\"{joiner.input_pairs[1].crd.name}\" style=dashed type=\"crd\"]\n"
            if joiner.input_pairs[1].ref.id.id in channel_map:
                dot += f"{channel_map[joiner.input_pairs[1].ref.id.id]} -> {operator.id} [label=\"{joiner.input_pairs[1].ref.name}\" style=bold type=\"ref\"]\n"
            channel_map[joiner.output_ref1.id.id] = operator.id
            channel_map[joiner.output_ref2.id.id] = operator.id
            channel_map[joiner.output_crd.id.id] = operator.id
        elif op == "fiber_write":
            fw = operator.fiber_write
            label = fw.label
            dot += f"{operator.id} [label=\"{label}\" color=green3 shape=box style=filled type=\"{operator.name}\" index=\"{fw.index}\" tensor=\"{fw.tensor}\" mode=\"{fw.mode_val}\" format=\"{fw.format}\" segsize=\"{fw.segsize}\" crdsize=\"{fw.crdsize}_dim\" sink=\"{fw.sink}\"]\n"
            if fw.input_crd.id.id in channel_map:
                dot += f"{channel_map[fw.input_crd.id.id]} -> {operator.id} [label=\"{fw.input_crd.name}\" style=dashed type=\"crd\"]\n"
        elif op == "val_write":
            vw = operator.val_write
            label = vw.label
            dot += f"{operator.id} [label=\"{label}\" color=green3 shape=box style=filled type=\"{operator.name}\" tensor=\"{fw.tensor}\"]\n"
            if vw.input_val.id.id in channel_map:
                dot += f"{channel_map[vw.input_val.id.id]} -> {operator.id} [label=\"{vw.input_val.name}\" type=\"val\"]\n"
        elif op == "array":
            av = operator.array
            label = av.label
            dot += f"{operator.id} [label=\"{label}\" color=green2 shape=box style=filled type=\"operator.name\" tensor=\"{av.tensor}\"]\n"
            if av.input_ref.id.id in channel_map:
                dot += f"{channel_map[av.input_ref.id.id]} -> {operator.id} [label=\"{av.input_ref.name}\" style=bold type=\"ref\"]\n"
            channel_map[av.output_val.id.id] = operator.id
        elif op == "alu":
            alu = operator.alu
            dot += f"{operator.id} [label=\"{operator.name}\" color=\"#a52a2a\" shape=box style=filled type=\"{operator.name}\"]\n"
            for val in alu.vals.inputs:
                if val.id.id in channel_map:
                    dot += f"{channel_map[val.id.id]} -> {operator.id} [label=\"{val.name}\" type=\"val\"]\n"
            channel_map[alu.vals.output.id.id] = operator.id
        elif op == "reduce":
            red = operator.reduce
            dot += f"{operator.id} [label=\"{operator.name}\" color=brown shape=box style=filled type=\"reduce\"]\n"
            if red.input_val.id.id in channel_map:
                dot += f"{channel_map[red.input_val.id.id]} -> {operator.id} [label=\"{red.input_val.name}\" type=\"val\"]\n"
            channel_map[red.output_val.id.id] = operator.id
        elif op == "repeat":
            rep = operator.repeat
            dot += f"{operator.id} [label=\"{rep.label}\" color=cyan2 shape=box style=filled type=\"repeat\" index=\"{rep.index}\" tensor=\"{rep.tensor}\" root=\"{rep.root}\"]\n"
            if rep.input_ref.id.id in channel_map:
                dot += f"{channel_map[rep.input_ref.id.id]} -> {operator.id} [label=\"{rep.input_ref.name}\" style=bold type=\"val\"]\n"
            if rep.input_rep_sig.id.id in channel_map:
                dot += f"{channel_map[rep.input_rep_sig.id.id]} -> {operator.id} [label=\"{rep.input_rep_sig.name}\" style=dotted type=\"val\"]\n"
            channel_map[rep.output_ref.id.id] = operator.id
        elif op == "repeatsig":
            repsig = operator.repeatsig
            dot += f"{operator.id} [label=\"{repsig.label}\" color=cyan3 shape=box style=filled type=\"repsiggen\" index=\"{repsig.index}\"]\n"
            if repsig.input_crd.id.id in channel_map:
                dot += f"{channel_map[repsig.input_crd.id.id]} -> {operator.id} [label=\"{repsig.input_crd.name}\" style=dashed type=\"val\"]\n"
            channel_map[repsig.output_rep_sig.id.id] = operator.id
        elif op == "coord_drop":
            cd = operator.coord_drop
            dot += f"{operator.id} [label=\"{cd.label}\" color=orange shape=box style=filled type=\"crddrop\" outer=\"{cd.outer_crd}\" inner=\"{cd.inner_crd}\"]\n"
            if cd.input_inner_crd.id.id in channel_map:
                dot += f"{channel_map[cd.input_inner_crd.id.id]} -> {operator.id} [label=\"{cd.input_inner_crd.name}\" style=dashed type=\"val\"]\n"
            if cd.input_outer_crd.id.id in channel_map:
                dot += f"{channel_map[cd.input_outer_crd.id.id]} -> {operator.id} [label=\"{cd.input_outer_crd.name}\" style=dashed type=\"val\"]\n"
            channel_map[cd.output_inner_crd.id.id] = operator.id
            channel_map[cd.output_outer_crd.id.id] = operator.id
        elif op == "spacc":
            sp = operator.spacc
            dot += f"{operator.id} [label=\"SparseAccumulator 0 0=i \" color=brown shape=box style=filled type=\"spaccumulator\" order=\"0\" in0=\"{sp.inner_crd}\"]\n"
            if sp.input_val.id.id in channel_map:
                dot += f"{channel_map[sp.input_val.id.id]} -> {operator.id} [label=\"{sp.input_val.name}\" type=\"val\"]\n"
            channel_map[sp.output_val.id.id] = operator.id
        elif op == "func":
            intrin = operator.func
            if intrin.input_val.id.id in channel_map:
                dot += f"{channel_map[intrin.input_val.id.id]} -> {operator.id} [label=\"{intrin.input_val.name}\" type=\"val\"]\n"

        elif op == "broadcast":
            bd = operator.broadcast
            bd_conn = {}
            bd_conn["crd"] = (bd.crd, "dashed")
            bd_conn["ref"] = (bd.ref, "bold")
            bd_conn["repsig"] = (bd.repsig, "dotted")
            bd_conn["val"] = (bd.val, "solid")
            bd_type = bd.WhichOneof("conn")
            if bd_conn[bd_type][0].input.id.id in channel_map:
                dot += f"{channel_map[bd_conn[bd_type][0].input.id.id]} -> {operator.id} [label=\"{bd_type}\" style=\"{bd_conn[bd_type][1]}\"]\n"

    return dot


if __name__ == '__main__':
    app.run(port=5000)
