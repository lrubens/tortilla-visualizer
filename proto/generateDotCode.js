export function generateDotCode(protoText) {
  return protobuf.load("../proto/tortilla.proto")
    .then(root => {
      const Operation = root.lookupType("Operation");
      const ProgramGraph = root.lookupType("ProgramGraph");


      const parsedProtoText = eval(`(${protoText})`); // Evaluate the string as JavaScript code

  // Create an array of operation instances from the operation data
  var operations = parsedProtoText.map(data => Operation.create(data));

  // Create a ProgramGraph instance with the operations
  var programGraphData = {
    name: "MyProgramGraph",
    operators: operations
    // You can include your streams here...
  };
  var programGraph = ProgramGraph.create(programGraphData);

  // Now you can use the programGraph instance as needed...
    let dotCode = `digraph SAM {\n`;
    for(let operation of programGraph.operators){
      var operationMessage = Operation.fromObject(operation);

      if(operationMessage.fiber_lookup){
        const fl = operationMessage.fiber_lookup;
        //adding node
        dotCode += `${operationMessage.id}[label = "${fl.label}" color=green4 shape=box style=filled type="${operationMessage.name}" index="${fl.index}" tensor="${fl.tensor}" mode="${fl.mode}" format="${fl.mode}" src="${fl.src}" root="${fl.root}"]\n`;
        
        //set red.id to 0 for nodes that are a part of a joiner
        if(fl.ref == true){ 
          //adding CRD edge 
          dotCode += `${operationMessage.id} -> ${fl.output_ref.id} [label="crd_in-B" style=dashed type="crd" comment="in-B"]\n`;
          //adding edge
          dotCode += `${operationMessage.id} -> ${fl.output_crd.id} [label="ref_in-B" style=bold type="ref" comment="in-B"]\n`;
        } 
      }

      else if(operationMessage.joiner){
        const joiner = operationMessage.joiner;
        dotCode += `${operationMessage.id}[label = "${joiner.label}" color="#800080" shape=box style=filled type="${operationMessage.name}" index="${joiner.index}"]\n`;

        //add edges from inside the bundles
        joiner.bundles.forEach(bundle => {
          if(bundle.crd != 0){
          dotCode += `${operationMessage.id} -> ${bundle.crd} [label="${bundle.crd_label}" style=dashed type="crd" comment="join-crd"]\n`;
          }
          if(bundle.ref != 0){
            dotCode += `${operationMessage.id} -> ${bundle.ref} [label="${bundle.ref_label}" style=bold type="ref" comment="join-crd"]\n`;
          }
        })
      }

      else if(operationMessage.fiber_write){
        const fw = operationMessage.fiber_write;
        //adding node
        dotCode += `${operationMessage.id}[label="${fw.label}" color=green3 shape=box style=filled type="${operationMessage.name}" index="${fw.index}" tensor="${fw.tensor}" mode="${fw.mode}" format="${fw.format}" segsize="${fw.segsize}" crdsize="${fw.crdsize}_dim" sink="${fw.sink}"]\n`;
      }

      else if(operationMessage.arrayvals){
        const av = operationMessage.arrayvals;
        dotCode += `${operationMessage.id}[label="Array Vals: ${av.tensor}" color=green2 shape=box style=filled type="${operationMessage.name}" tensor="${av.tensor}"]\n`;
      }

      else if(operationMessage.alu){
        const alu = operationMessage.alu;
        // Adding node
        dotCode += `${operationMessage.id}[label="${operationMessage.name}" color="#a52a2a" shape=box style=filled type="${alu.type}" sub="${alu.sub}"]\n`;

        //add edges from ALU input
        // Add edges from ALU inputs
        for (let input of alu.conn.vals.inputs) {
          dotCode += `${input.id} -> ${operationMessage.id} [label="val" type="val"]\n`;
        }
        //add edge from output 
        dotCode += `${operationMessage.id} -> ${alu.conn.vals.output.id} [label="val" type="val"]\n`;
      }
    }

    dotCode += `}`;
    //console.log(dotCode);
    return dotCode;
    })

    .catch(error => {
      console.error("Failed to load protobuf:", error);
      throw error;
    });
}
