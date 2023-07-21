export function generateDotCode(protoText) {
  return protobuf.load("../proto/tortilla.proto")
    .then(root => {
      const Operation = root.lookupType("Operation");
      const ProgramGraph = root.lookupType("ProgramGraph");

      const indexOfOpeningBracket = protoText.indexOf("[");
      // Check if "[" was found in the string (indexOfOpeningBracket will be -1 if not found)
      if (indexOfOpeningBracket !== -1) {
        // If "[" is found, slice the string from that position onwards
        var slicedProtoText = protoText.slice(indexOfOpeningBracket);
        console.log(slicedProtoText);
      } 
      const parsedProtoText = eval(`(${slicedProtoText})`); // Evaluate the string as JavaScript code

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
      var label = `${operationMessage.name} ${fl.index}: ${fl.tensor}${fl.mode}\\n${fl.format}`
      dotCode += `${operationMessage.id}[label = "${label}" color=green4 shape=box style=filled type="${operationMessage.name}" index="${fl.index}" tensor="${fl.tensor}" mode="${fl.mode}" format="${fl.mode}" src="${fl.src}" root="${fl.root}"]\n`;
      
      //set red.id to 0 for nodes that are a part of a joiner
      if(fl.ref == true){ 
        //adding CRD edge 
        dotCode += `${operationMessage.id} -> ${fl.output_ref.id} [label="crd_in-${fl.tensor}" style=dashed type="crd" comment="in-${fl.tensor}"]\n`;
        //adding edge
        dotCode += `${operationMessage.id} -> ${fl.output_crd.id} [label="ref_in-${fl.tensor}" style=bold type="ref" comment="in-${fl.tensor}"]\n`;
      } 
    }

    else if(operationMessage.joiner){
      const joiner = operationMessage.joiner;
      var label = `${operationMessage.name} ${joiner.index}`
      dotCode += `${operationMessage.id}[label = "${label}" color="#800080" shape=box style=filled type="${operationMessage.name}" index="${joiner.index}"]\n`;

      //add edges from inside the bundles
      joiner.bundles.forEach(bundle => {
        if(bundle.crd.id != 0){
        dotCode += `${operationMessage.id} -> ${bundle.crd.id} [label="${bundle.crd_label}" style=dashed type="crd" comment="join-crd"]\n`;
        }
        if(bundle.ref.id != 0){
          dotCode += `${operationMessage.id} -> ${bundle.ref.id} [label="${bundle.ref_label}" style=bold type="ref" comment="join-crd"]\n`;
        }
      })
    }

    else if(operationMessage.fiber_write){
      const fw = operationMessage.fiber_write;
      if(fw.mode != "vals"){
        var label = `${operationMessage.name} ${fw.index}: ${fw.tensor}${fw.mode}\\n${fw.format}`
      } else{
        var label = `${operationMessage.name} ${fw.mode}: ${fw.tensor}`
      }
      //adding node
      dotCode += `${operationMessage.id} [label="${label}" color=green3 shape=box style=filled type="${operationMessage.name}" index="${fw.index}" tensor="${fw.tensor}" mode="${fw.mode}" format="${fw.format}" segsize="${fw.segsize}" crdsize="${fw.crdsize}_dim" sink="${fw.sink}"]\n`;
    }

    else if(operationMessage.arrayvals){
      const av = operationMessage.arrayvals;
      dotCode += `${operationMessage.id} [label="Array Vals: ${av.tensor}" color=green2 shape=box style=filled type="${operationMessage.name}" tensor="${av.tensor}"]\n`;
    }

    else if(operationMessage.alu){
      const alu = operationMessage.alu;
      // Adding node
      dotCode += `${operationMessage.id}[label="${operationMessage.name}" color="#a52a2a" shape=box style=filled type="${alu.type}" sub="${alu.sub}"]\n`;

      //add edges from ALU input
      // Add edges from ALU inputs
      for (let input of alu.vals.inputs) {
        dotCode += `${input.id} -> ${operationMessage.id} [label="val" type="val"]\n`;
      }
      //add edge from output 
      dotCode += `${operationMessage.id} -> ${alu.vals.output.id} [label="val" type="val"]\n`;
    }
  }

  dotCode += `}`;
  console.log(dotCode);
  return dotCode;
  })

    .catch(error => {
      console.error("Failed to load protobuf:", error);
      throw error;
    });
}
