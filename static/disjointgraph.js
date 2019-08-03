

export function disjointGraph(data) {
    var width = 500;
    var height = 500;
    

    let drag = simulation => {
  
  function dragstarted(d) {
    if (!d3.event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }
  
  function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
  }
  
  function dragended(d) {
    if (!d3.event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }
  
  return d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended);
}


function cleanData(data) {
  
}

    //derived from https://observablehq.com/@d3/disjoint-force-directed-graph
    // and https://bl.ocks.org/heybignick/3faf257bbbbc7743bb72310d03b86ee8   
  const links = data.links.map(d => Object.create(d));
  const nodes = data.nodes.map(d => Object.create(d));

  const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id(d => d.id))
      .force("charge", d3.forceManyBody())
      .force("x", d3.forceX())
      .force("y", d3.forceY());
      

  const svg = d3.select('svg')
      .attr("viewBox", [-width / 2, -height / 2, width, height]);

  const link = svg.append("g")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
    .selectAll("line")
    .data(links)
    .join("line")
      .attr("stroke-width", d => Math.sqrt(d.value));
    let color = 'red';

/*
  const node = svg.append("g")
      .attr("stroke", "#fff")
      .attr("stroke-width", 1.5)
    .selectAll("g")
    .data(nodes).enter().append('g');
    */
    var node = svg.append("g")
      .attr("class", "nodes")
    .selectAll("g")
    .data(nodes)
    .enter().append("g");

    let circles = node.append("circle")
      .attr("r", 5)
      .attr("fill", function(d){if (d.type=="pathway")
      {return 'blue'} 
      else if(d.type=="gene") {
          if (d.classification=="pathogenic") {
            return 'red'
          } else {
              return 'grey'
          }
          
          } 
      else {return 'orange';}  })
      .call(drag(simulation));

      let texts = node.append('text').text(function(d){
          if (d.type=="gene") {
            return d.id
          } else {
              return '';
          }
          
          ;}).attr('x',6).attr('y',3);
      //.append('text').text(function(d){return d.id;});
      
      node.append("title")
      .text(function(d) { return d.id; });
      

  node.append("title")
      .text(d => d.id);


      simulation
      .nodes(nodes)
      .on("tick", ticked);

  simulation.force("link")
      .links(links);

  function ticked() {
    link
        .attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    node
        .attr("transform", function(d) {
          return "translate(" + d.x + "," + d.y + ")";
        })
  }

//  invalidation.then(() => simulation.stop());

  //return svg.node();
}
