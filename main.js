import { generateDotCode } from '../proto/generateDotCode.js';

//Button handler to download graphic as SVG
document.getElementById('downloadBtn').addEventListener('click', function() {
  var svgElement = document.querySelector('#graph svg'); // Select the SVG element
  var svgData = new XMLSerializer().serializeToString(svgElement); // Serialize the SVG to a string
  var blob = new Blob([svgData], {type: 'image/svg+xml'}); // Create a Blob from the SVG string
  var url = URL.createObjectURL(blob); // Create a URL from the Blob

  // Create a new <a> element, set its href to the Blob URL, and programmatically click it to initiate download
  var link = document.createElement('a');
  link.href = url;
  link.download = 'graph.svg';
  link.click();

  // Clean up by revoking the Blob URL
  URL.revokeObjectURL(url);
});

var editor = ace.edit("editor");
        editor.setTheme("ace/theme/twilight");
        editor.getSession().setMode("ace/mode/text");
        //the following line allows the editor to directly read in dot
        //editor.session.setMode("ace/mode/dot");

        var margin = 40; // to avoid scrollbars
        var graphviz; // Declare the graphviz variable

        function attributer(datum, index, nodes) {
            var selection = d3.select(this);
            if (datum.tag == "svg") {
                var editorWidth = document.getElementById("editor").clientWidth; // Get the width of the editor element
                var width = Math.min(window.innerWidth - editorWidth, window.innerHeight) - margin; // Calculate the width to fit within the remaining space
                var height = window.innerHeight;
                selection
                    .attr("width", width)
                    .attr("height", height);
                datum.attributes.width = width - margin;
                datum.attributes.height = height - margin;
            }
        }

        function resetZoom() {
            console.log('Resetting zoom');
            graphviz
                .resetZoom(d3.transition().duration(1000));
        }

        function resizeSVG() {
            console.log('Resize');
            var editorWidth = document.getElementById("editor").clientWidth; // Get the width of the editor element
            var width = Math.min(window.innerWidth - editorWidth, window.innerHeight) - margin; // Calculate the width to fit within the remaining space
            var height = window.innerHeight;
            d3.select("#graph").selectWithoutDataPropagation("svg")
                .transition()
                .duration(700)
                .attr("width", width - margin)
                .attr("height", height - margin);
        }

        d3.select(window).on("resize", resizeSVG);
        d3.select(window).on("click", resetZoom);

        function renderGraph() {
            var protoTextSource = editor.getValue();
            generateDotCode(protoTextSource)
              .then(dotSource => {
                if (graphviz) {
                  graphviz
                    .attributer(attributer)
                    .renderDot(dotSource);
                } else {
                  graphviz = d3.select("#graph").graphviz()
                    .zoomScaleExtent([0.5, 2])
                    .attributer(attributer)
                    .renderDot(dotSource);
                }
              })
              .catch(error => {
                // Handle any errors that occurred during loading or generating dotCode
                console.error(error);
              });
          }
          

        // Initial rendering
        renderGraph();

        // Reload the graph when the file changes
        function watchFileChanges() {
            renderGraph(); // Render the graph on each check
            setTimeout(watchFileChanges, 1000); // Check for file changes every second
        }

        watchFileChanges();