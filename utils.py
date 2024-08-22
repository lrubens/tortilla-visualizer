import tortilla_pb2
import comal_pb2


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
        elif op == "fork":
            bd = operator.fork
            bd_conn = {}
            bd_conn["crd"] = bd.crd
            bd_conn["ref"] = bd.ref
            bd_conn["repsig"] = bd.repsig
            bd_conn["val"] = bd.val
            dot += f"{operator.id} [label = \"Fork\" shape=box color=purple style=invis type=\"fork\"]"
            bd_type = bd.WhichOneof("conn")
            for output in bd_conn[bd_type].outputs:
                channel_map[output.id.id] = operator.id
        elif op == "join":
            bd = operator.join
            bd_conn = {}
            bd_conn["crd"] = bd.crd
            bd_conn["ref"] = bd.ref
            bd_conn["repsig"] = bd.repsig
            bd_conn["val"] = bd.val
            dot += f"{operator.id} [label = \"Join\" shape=box color=purple style=invis type=\"fork\"]"
            bd_type = bd.WhichOneof("conn")
            # for output in bd_conn[bd_type].outputs:
            channel_map[bd_conn[bd_type].output.id.id] = operator.id
        elif op == "func":
            intrin = operator.func
            dot += f"{operator.id} [label=\"{intrin.name}\" color=palevioletred2 shape=box style=filled type=\"intrinsic\"]"
            channel_map[intrin.output_val.id.id] = operator.id
        elif op == "spacc":
            sp = operator.spacc
            in_lst = [f"0={sp.inner_crd}"]
            in_lst.extend([f"{num+1}={index}" for num,
                           index in enumerate(sp.outer_crds)])
            dot += f"{operator.id} [label=\"{sp.label} {' '.join(in_lst)} \" color=brown shape=box style=filled type=\"spaccumulator\" order=\"{sp.order}\" in0=\"{sp.inner_crd}\"]\n"

    for operator in program.operators:
        op = operator.WhichOneof("op")
        op_id = operator.id
        if op == "fiber_lookup":
            fl = operator.fiber_lookup
            label = fl.label
            lab = label.split(" ")
            new_label = lab[0] + " " + fl.tensor + \
                " : " + lab[1] + " (" + fl.format + ")"
            dot += f"{operator.id} [label = \"{new_label}\" color=green1 shape=box style=filled type=\"{operator.name}\" index=\"{fl.index}\" tensor=\"{fl.tensor}\" format=\"{fl.format}\" src=\"{fl.src}\" root=\"{fl.root}\"]\n"
            if fl.input_ref.id.id in channel_map:
                dot += f"{channel_map[fl.input_ref.id.id]} -> {operator.id} [label=\"ref_in-{fl.tensor}\" style=bold type=\"ref\"]\n"
            channel_map[fl.output_ref.id.id] = operator.id
            channel_map[fl.output_crd.id.id] = operator.id
        elif op == "root":
            root = operator.root
            label = root.label
            dot += f"{operator.id} [label = \"{label}\" color=green4 shape=box style=filled type=\"{operator.name}\"]\n"
            channel_map[root.output_ref.id.id] = operator.id
        elif op == "joiner":
            joiner = operator.joiner
            label = joiner.label
            dot += f"{operator.id} [label = \"{label}\" color=\"#800080\" shape=box style=filled type=\"{operator.name}\" index=\"{joiner.index}\"]\n"
            for i, val_bundle in enumerate(joiner.input_pairs):
                if val_bundle.crd.id.id in channel_map:
                    dot += f"{channel_map[val_bundle.crd.id.id]} -> {operator.id} [label=\"{val_bundle.crd.name}\" style=dashed type=\"crd\"]\n"

                payload = val_bundle.in_ref.WhichOneof("stream")
                ref_id = 0
                ref_name = ""
                if payload == "ref_stream":
                    ref_id = val_bundle.in_ref.ref_stream.id.id
                    ref_name = val_bundle.in_ref.ref_stream.name
                else:
                    ref_id = val_bundle.in_ref.val_stream.id.id
                    ref_name = val_bundle.in_ref.val_stream.name
                if ref_id in channel_map:
                    dot += f"{channel_map[ref_id]} -> {operator.id} [label=\"{ref_name}\" style=bold type=\"ref\"]\n"
                out_ref_id = 0
                out_payload = joiner.output_refs[i].WhichOneof("stream")
                if out_payload == "ref_stream":
                    out_ref_id = joiner.output_refs[i].ref_stream.id.id
                else:
                    out_ref_id = joiner.output_refs[i].val_stream.id.id
                channel_map[out_ref_id] = operator.id
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
            dot += f"{operator.id} [label=\"{label}\" color=green3 shape=box style=filled type=\"{operator.name}\" tensor=\"{vw.tensor}\"]\n"
            if vw.input_val.id.id in channel_map:
                dot += f"{channel_map[vw.input_val.id.id]} -> {operator.id} [label=\"{vw.input_val.name}\" type=\"val\"]\n"
        elif op == "array":
            av = operator.array
            label = av.label
            stream_label = "ref_in-" + av.tensor
            # print(av.tensor)
            dot += f"{operator.id} [label=\"{label}\" color=green2 shape=box style=filled type=\"operator.name\" tensor=\"{av.tensor}\"]\n"
            if av.input_ref.id.id in channel_map:
                dot += f"{channel_map[av.input_ref.id.id]} -> {operator.id} [label=\"{stream_label}\" style=bold type=\"ref\"]\n"
            channel_map[av.output_val.id.id] = operator.id
        elif op == "alu":
            alu = operator.alu
            color = "#a52a2a"
            if operator.name == "max" or operator.name == "exp":
                color = "pink1"
            dot += f"{operator.id} [label=\"{operator.name}\" color=\"{color}\" shape=box style=filled type=\"{operator.name}\"]\n"
            for val in alu.vals.inputs:
                if val.id.id in channel_map:
                    dot += f"{channel_map[val.id.id]} -> {operator.id} [label=\"{val.name}\" type=\"val\"]\n"
            channel_map[alu.vals.output.id.id] = operator.id
        elif op == "reduce":
            red = operator.reduce
            name = operator.name
            color = "brown"
            if red.reduce_type == 1:
                name = "max reduce"
            dot += f"{operator.id} [label=\"{name}\" color={color} shape=box style=filled type=\"reduce\"]\n"
            if red.input_val.id.id in channel_map:
                dot += f"{channel_map[red.input_val.id.id]} -> {operator.id} [label=\"{red.input_val.name}\" type=\"val\"]\n"
            channel_map[red.output_val.id.id] = operator.id
        elif op == "gen_ref":
            red = operator.gen_ref
            dot += f"{operator.id} [label=\"{operator.name}\" color=purple shape=box style=filled type=\"gen_ref\"]\n"
            if red.input_crd.id.id in channel_map:
                dot += f"{channel_map[red.input_crd.id.id]} -> {operator.id} [label=\"{red.input_crd.name}\" type=\"val\"]\n"
            channel_map[red.output_ref.id.id] = operator.id
        elif op == "repeat":
            rep = operator.repeat
            dot += f"{operator.id} [label=\"{rep.label}\" color=cyan2 shape=box style=filled type=\"repeat\" index=\"{rep.index}\" tensor=\"{rep.tensor}\" root=\"{rep.root}\"]\n"
            in_ref_id = 0
            in_ref_one = rep.WhichOneof("input_ref")
            if in_ref_one == "in_val":
                in_ref_id = rep.in_val.id.id
            else:
                in_ref_id = rep.in_ref.id.id
            rep_id = 0
            in_rep_one = rep.WhichOneof("input_rep_sig")
            if in_rep_one == "rep_val":
                rep_id = rep.rep_val.id.id
            else:
                rep_id = rep.rep_ref.id.id
            if in_ref_id in channel_map:
                dot += f"{channel_map[in_ref_id]} -> {operator.id} [label=\"ref\" style=bold type=\"val\"]\n"
            if rep_id in channel_map:
                dot += f"{channel_map[rep_id]} -> {operator.id} [label=\"sig\" style=dashed type=\"crd\"]\n"
            # if rep.input_rep_sig.id.id in channel_map:
            #     dot += f"{channel_map[rep.input_rep_sig.id.id]} -> {operator.id} [label=\"{rep.input_rep_sig.name}\" style=dotted type=\"val\"]\n"
            if in_ref_one == "in_val":
                channel_map[rep.out_val.id.id] = operator.id
            else:
                channel_map[rep.out_ref.id.id] = operator.id
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
            # in_lst = [f"0={sp.inner_crd}"]
            # in_lst.extend([f"{num+1}={index}" for num,
            #                index in enumerate(sp.outer_crds)])
            # dot += f"{operator.id} [label=\"{sp.label} {' '.join(in_lst)} \" color=brown shape=box style=filled type=\"spaccumulator\" order=\"{sp.order}\" in0=\"{sp.inner_crd}\"]\n"
            if sp.input_val.id.id in channel_map:
                dot += f"{channel_map[sp.input_val.id.id]} -> {operator.id} [label=\"{sp.input_val.name}\" type=\"val\"]\n"
            if sp.input_inner_crd.id.id in channel_map:
                dot += f"{channel_map[sp.input_inner_crd.id.id]} -> {operator.id} [label=\"{sp.input_inner_crd.name}\" style=\"dashed\" type=\"crd\"]\n"
            for in_outer_crd in sp.input_outer_crds:
                if in_outer_crd.id.id in channel_map:
                    dot += f"{channel_map[in_outer_crd.id.id]} -> {operator.id} [label=\"{in_outer_crd.name}\" style=\"dashed\" type=\"crd\"]\n"
            channel_map[sp.output_val.id.id] = operator.id
            for out_outer_crd in sp.output_outer_crds:
                channel_map[out_outer_crd.id.id] = operator.id
            channel_map[sp.output_inner_crd.id.id] = operator.id
        elif op == "func":
            intrin = operator.func
            if intrin.input_val.id.id in channel_map:
                dot += f"{channel_map[intrin.input_val.id.id]} -> {operator.id} [label=\"{intrin.input_val.name}\" type=\"val\"]\n"

            channel_map[sp.output_inner_crd.id.id] = operator.id
            for outer_crd in sp.output_outer_crds:
                channel_map[outer_crd.id.id] = operator.id
        elif op == "broadcast":
            bd = operator.broadcast
            bd_conn = {}
            bd_conn["crd"] = (bd.crd, "dashed")
            bd_conn["ref"] = (bd.ref, "bold")
            bd_conn["repsig"] = (bd.repsig, "dotted")
            bd_conn["val"] = (bd.val, "solid")
            bd_type = bd.WhichOneof("conn")
            if bd_conn[bd_type][0].input.id.id in channel_map:
                dot += f"{channel_map[bd_conn[bd_type][0].input.id.id]} -> {operator.id} [label=\"{bd_conn[bd_type][0].input.name}\" style=\"{bd_conn[bd_type][1]}\"]\n"
        elif op == "fork":
            bd = operator.fork
            bd_conn = {}
            bd_conn["crd"] = (bd.crd, "dashed")
            bd_conn["ref"] = (bd.ref, "bold")
            bd_conn["repsig"] = (bd.repsig, "dotted")
            bd_conn["val"] = (bd.val, "solid")
            bd_type = bd.WhichOneof("conn")

            dot += f"{operator.id} [label=\"{operator.name}\" color=\"#416aa3\" shape=box style=filled type=\"{operator.name}\"]\n"
            if bd_conn[bd_type][0].input.id.id in channel_map:
                dot += f"{channel_map[bd_conn[bd_type][0].input.id.id]} -> {operator.id} [label=\"{bd_type}\" style=\"{bd_conn[bd_type][1]}\"]\n"
        elif op == "join":
            bd = operator.join
            bd_conn = {}
            bd_conn["crd"] = (bd.crd, "dashed")
            bd_conn["ref"] = (bd.ref, "bold")
            bd_conn["repsig"] = (bd.repsig, "dotted")
            bd_conn["val"] = (bd.val, "solid")
            bd_type = bd.WhichOneof("conn")
            dot += f"{operator.id} [label=\"{operator.name}\" color=\"#416aa3\" shape=box style=filled type=\"{operator.name}\"]\n"
            for inputs in bd_conn[bd_type][0].inputs:
                if inputs.id.id in channel_map:
                    dot += f"{channel_map[inputs.id.id]} -> {operator.id} [label=\"{bd_type}\" style=\"{bd_conn[bd_type][1]}\"]\n"

    return dot
