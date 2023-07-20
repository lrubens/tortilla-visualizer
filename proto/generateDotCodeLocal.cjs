const protobuf = require('protobufjs');
const root = protobuf.loadSync("/home/pbeni/Research/tortilla/d3-graphviz/proto/tortilla.proto"); // abs path
const Operation = root.lookupType("Operation");
const ProgramGraph = root.lookupType("ProgramGraph");

// Update this list with your operation data
var operationsData = [
  {
    name: "fiberLookup",
    id: 10,
    fiber_lookup: {
      ref: true,
      output_ref: {
        id:9
      },
      output_crd:{
        id:9
      },
      index: "i",
      tensor: "B",
      mode:0,
      format: "compressed",
      src: true,
      root: true,
      label: "FiberLookup i: B0\ncompressed"
    }
  },

  {
    name: "fiberLookup",
    id: 11,
    fiber_lookup: {
      ref: true, 
      output_ref: {
        id: 9 
      },
      output_crd:{
        id: 9
      },
      index: "i",
      tensor: "C",
      mode: 0,
      format: "compressed",
      src: true,
      root: true,
      label: "FiberLookup i: C0\ncompressed"
    }
  },

  {
    name: "fiberwrite",
    id: 2,
    fiber_write: {
      ref: false,
      input_crd: { 
        id: 9 
      },
      index: "i",
      tensor: "X",
      mode: "0",
      format: "compressed",
      segsize: 2,
      crdsize: "B0",
      sink: true,
      label: "FiberWrite i: X0\ncompressed"
    }
  },

  {
    name: "fiberLookup",
    id: 7,
    fiber_lookup: {
      ref: true,
      output_ref: {
        id: 6
      },
      output_crd:{
        id: 6
      },
      index: "j",
      tensor: "B",
      mode: 1,
      format: "compressed",
      src: true,
      root: false,
      label: "FiberLookup j: B1\ncompressed"
    }
  },

  {
    name: "fiberLookup",
    id: 8,
    fiber_lookup: {
      ref: true,
      output_ref: {
        id: 6
      },
      output_crd:{
        id: 6
      },
      index: "j",
      tensor: "C",
      mode: 1,
      format: "compressed",
      src: true,
      root: false,
      label: "FiberLookup j: C1\ncompressed"
    }
  },

  {
    name: "fiberwrite",
    id: 1,
    fiber_write: {
      ref: false,
      input_crd: {
        id: 1 
      },
      index: "j",
      tensor: "X",
      mode: "1",
      format: "compressed",
      segsize: "B0_dim+1",
      crdsize: "B0_dim*B1_dim",
      sink: true,
      label: "FiberWrite j: X1\ncompressed"
    }
  },

  {
    name: "arrayVals",
    id: 4,
    arrayvals: {
      tensor: "B",
    }
  },

  {
    name: "arrayVals",
    id: 5,
    arrayvals: {
      tensor: "C",
    }
  },

  {
    name: "fiberwrite",
    id: 0,
    fiber_write: {
      ref: false,
      input_crd: {
        id: 1 
      },
      tensor: "X",
      mode: "vals",
      size: "1*B0_dim*B1_dim",
      sink: true,
      label: "FiberWrite Vals: X"
    }
  },


  {
    name: "union",
    id: 9,
    joiner: {
      join_type: 1,
      bundles: [
        {
        crd: 2,
        crd_label: "crd",
        ref: 0,
        }, 
        {
          crd: 0,
          ref: 7,
          ref_label: "ref_out-B"
        },
        {
          crd:0,
          ref: 8,
          ref_label: "ref-out-C"
        }
      ],
      index: "i",
      label: "union i"
    }
  },

  {
    name: "union",
    id: 6,
    joiner: {
      join_type: 1,
      bundles: [
        {
        crd: 1,
        crd_label: "crd",
        ref: 0,
        },
        {
          crd: 0,
          ref: 4,
          ref_label: "ref_out-B"
        },
        {
          crd:0,
          ref: 5,
          ref_label: "ref-out-C"
        }
      ],
      index: "j",
      label: "union j"
    }
  },

  {
    name: "add",
    id: 3,
    alu: {
      conn: {
        vals: {
          inputs: [
            { id: 4 },
            { id: 5 }
          ],
          output: { id: 0 },
        }
      },
      stages: [
        {
          inputs: [4, 5],
          output: 0,
          op: 0
        }
      ],
      output_val: 0
    }
  }
];

// Create an array of operation instances from the operation data
var operations = operationsData.map(data => Operation.create(data));

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
  console.log(dotCode);
  return dotCode;
