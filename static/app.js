//application variables will be stored here
var app = {"sample_pathways":{"R-HSA-69541":"Stabilization of p53"}, "all_nodes":{}, "reactions" : {}}; 

    var showPathwayList = function(r) {
        $.each(r,function(ok,dok) {

    
            var li = $("<li/>");
            li.attr("reactomeid",dok.stId).text(dok.displayName);
            $("#pathways").append(li)
    });
    }
    
    
    
    
    var nodeFromReactantIfExists = function(r) {
        //not everything in the input and output arrays from reactome is an object

        if (typeof(r)=='object') {
            var id = r['stId'];
            if (id in app.all_nodes ) {
                return app.all_nodes[id]
            } else {
                    var n ={'name':r['displayName'],'group':1, 'type':"reactant", stId:id};
                    app.all_nodes[id] = n;
                    return n;
            }
        } else {
            return null;
        }
    }
    

    var clearCanvas = function() {
        svg = d3.select("#svg_viewer"); //##div"+pathway_id).append("svg")
        svg.selectAll('*').remove()
    }
    var renderReactions = function() {
        
        clearCanvas();
        
        g = graphObjectOfAllReactions();
        
        doGraph(g);
        
    }
    
    var graphObjectOfAllReactions = function() {
        //todo add memoization so not regenerated if no new data has been feteched
        var g = {"nodes":[],"links":[]};
                
        var keys = Object.keys(app.reactions);
        
        var node_indexes = {}
        
        var nodes = []
        
        $(keys).each(function(i,key) {
            var reaction = app.reactions[key];
            
            if (!(reaction.stId in node_indexes)) {
                var n = makeReactionNode(reaction);
                nodes.push(n);
                node_indexes[reaction.stId] = nodes.length-1 
            }
            
            for (j=0;j<reaction.input.length;j++){
                var r = reaction.input[j]
                if (typeof(r) =='object') {
                    var stId = r.stId;
                    if (!(stId in node_indexes)) {
                        n = app.all_nodes[stId];
                        nodes.push(n);
                        node_indexes[stId]  = nodes.length-1;
                    }
                }
            }
            for (j=0;j<reaction.output.length;j++){
                var r = reaction.output[j]
                if (typeof(r) =='object') {
                    var stId = r.stId;
                    if (!(stId in node_indexes)) {
                        n = app.all_nodes[stId];
                        nodes.push(n);
                        node_indexes[stId]  = nodes.length-1;
                    }
                }
            }
        });
        
        
        $.each(keys, function(i, key) {
            var reactionIdx = node_indexes[key];
            
            var reaction = app.reactions[key];
                        
            for (j=0;j<reaction.input.length;j++){

                var r = reaction.input[j]
                if (typeof(r) =='object') {
                    var stId = r.stId;
                    var inputIdx = node_indexes[stId];
                    g.links.push({"source":inputIdx,"target":reactionIdx, "weight":1, "type":"input","sourceStId": stId, "targetStId":key});
                }
            }
            for (j=0;j<reaction.output.length;j++){
                var r = reaction.output[j]
                if (typeof(r) =='object') {
                    var stId = r.stId;
                    var outputIdx = node_indexes[stId];
                    g.links.push({source:reactionIdx,target:outputIdx, weight:1, "type":"output","sourceStId": key, "targetStId":stId});                

                }
            }
        });
        
        g.nodes = nodes;
        
        return g;
    }
    
    var makeReactionNode = function(r) {
        return {name:r.displayName,group:1,type:"reaction", stId:r.stId};
    }

    var pathway_viewer = function(resp,status) {
        console.log(pathway_viewer)
        app.active_pathway = resp;
        var reactions = resp.hasEvent;
        var pathway_id = resp.stId;
        var pathway_title = $("#pathwaytitle")
        pathway_title.text(resp.displayName);
        
        var pwurl = $('<a/>').attr('href',rjs.reactomeUrl(pathway_id)).attr('target','_blank').text("View on Reactome");
        $('#pathwayurl').html(pwurl)
        var reaction_list = $("#reactions");
        $.each(reactions,function(idx, reaction){
            if (reaction.className=="Reaction") {
                console.log("got a reaction");
            var li = $('<li/>')
            .addClass('reaction')
            .attr("stId",reaction.stId)
            .appendTo(reaction_list).text(reaction.name[0]);   
        }
        });
        reaction_list.click(function(a,b){
            window.rlista = a; 
            var reaction_id = $(rlista.target).attr('stid');
            
            var onLoadReaction = function(resp) {
                window.reaction = resp;
//                reaction_div.text(resp);
                svg = d3.select("#svg_viewer"); //##div"+pathway_id).append("svg")
                svg.selectAll('*').remove()
//                .attr("width", width)
 //               .attr("height", height);
                 $('#pathways').hide()

                refreshDisplay(resp);
                
            }
            rjs.getReaction(reaction_id, onLoadReaction);

        })
        
        
        window.lastPathway = resp;
    }
    
    
    var refreshDisplay = function(resp) {
        $('#viewer').show();
        if (!resp) {
            resp = app.lastDisplay
        } 
        
        switch($('#viewmode').val()){
            case 'reaction':
                renderReaction(resp);
                app.lastDisplay = resp
                break;
            case 'network':
                renderFullNetwork(resp);
                break;
            case 'animation':
                renderAnimation(resp);
                app.lastDisplay = resp;                
                break;
            case 'quiz':
                rjsquiz.newGame(function(statusText){console.log(statusText)});
                break;
            case 'pathway':
                renderNetworkManual();
                break;
            default:
                alert("No view option selected");
        }

    }


    var renderFullNetwork = function(resp) {
        clearCanvas();
        rjs.draw('#svg_viewer');
    }

var width = 900,
height = 600;

var svg, force;
// svg = d3.select("#svg_viewer")
var setupForce = function(){
 svg = d3.select("#svg_viewer")
    //$('#svg_viewer').width()
    svg.attr("width", width)
    .attr("height", height);
/*
 force = d3.layout.force()
    .gravity(.05)
    .distance(100)
    .charge(-100)
    .size([width, height]);
 */
 setupMarkers(svg)   
}



var setupMarkers = function(svg) {
    
// define arrow markers for graph links
svg.append('svg:defs').append('svg:marker')
    .attr('id', 'end-arrowz')
    .attr('viewBox', '0 -5 10 10')
    .attr('refX', 6)
    .attr('markerWidth', 3)
    .attr('markerHeight', 3)
    .attr('orient', 'auto')
  .append('svg:path')
    .attr('d', 'M0,-5L10,0L0,5')
    .attr('fill', '#000');

svg.append('svg:defs').append('svg:marker')
    .attr('id', 'start-arrowz')
    .attr('viewBox', '0 -5 10 10')
    .attr('refX', 4)
    .attr('markerWidth', 3)
    .attr('markerHeight', 3)
    .attr('orient', 'auto')
  .append('svg:path')
    .attr('d', 'M10,-5L0,0L10,5')
    .attr('fill', '#000');
    

    
svg.append("svg:defs").append("svg:marker")
    .attr("id", "start-arrow")
    .attr("refX", 6)
    .attr("refY", 6)
    .attr("markerWidth", 30)
    .attr("markerHeight", 30)
    .attr("orient", "auto")
    .append("path")
    .attr("d", "M 0 0 12 6 0 12 3 6")
    .style("fill", "yellow");  
    
 
svg.append("svg:defs").append("svg:marker")
    .attr("id", "end-arrow")
    .attr("refX", 35)
    .attr("refY", 10)
    .attr("markerWidth", 20)
    .attr("markerHeight", 20)
    .attr("orient", "auto")
    .append("path")
        .attr('viewBox','0 0 30 30')
    .attr("d", "M 0 0 0 20 20 10 0 0")   //think of it like tip, side point of arrow 1, side point of arrow 2,  tip
    .style("fill", "red");  
    
    //    .attr("d", "M 0 10 0 0 30 10 0 30")
    //    .attr("d", "M 0 0 30 30 30 0 0 0")
//    .attr('viewBox','-5 -5 10 10')
  //  .attr("d", "M 0,0 m -5,-5 L 5,0 L -5,5 Z")
    
    
    //path: 'M 0,0 m -5,-5 L 5,0 L -5,5 Z', viewbox: '-5 -5 10 10'
    
    
 }   
 
 
 var manualLayout = function(nodesAndLinks) {
        nodesAndLinks =  graphObjectOfAllReactions();
        
        G = getDiGraph(nodesAndLinks);
        
        var orphans = parentlessNodes(G)
        //https://bl.ocks.org/mbostock/22994cc97fefaeede0d861e6815a847e
        
        
        var w = parseInt(svg.attr('width'))
        var width_per = w/(orphans.length+1)
        var data;
        for (var i=0;i<orphans.length;i++) {
            orphans[i].left = width_per * (i+1)
        }
        
        var a = svg.selectAll('circle').data(orphans)
        
        a.enter().append("circle").attr('r',12).attr('cx',function(d) {return d.left}).attr('cy',30);
        
        console.log("did ido it?")
             
 }
 
 var colorByProperty = function(prop_name, domain, range) {
     var color_scale = d3.scaleLinear().domain(domain).range(range);
     svg.selectAll('circle').style('fill', function(d){return color_scale(d[prop_name])});

 }
 var reactantNode = function(sg, dataElement) {
     var circ = sg.selectAll('circle').data([dataElement]).enter()
     .append('circle').attr('cy',dataElement.top).attr('cx',function(d){return d.left}).classed('nodecircle',true).attr('r',12)
     .attr('id',function(d){return d.toString()})
     
     sg.append('text').text(dataElement.displayName).attr('y',dataElement.top-15)
     .attr('x',dataElement.left-14)
     .attr('id',"label" + dataElement.stId)
     .classed('nodecirclelabel',true);
     
     return circ
//     .style("fill", function(d, i) { return color(i); });
     
 }
 
 var reactionNode = function(sg, dataElement, x,y,w,h) {
     var rect = sg.selectAll('rect').data([dataElement]).enter()
     .append('rect').classed('noderect',true)
     .attr('x',x).attr('y',y).attr('width',w).attr('height',h).attr('id',function(d){return d.toString()}).style('fill','#eee')
     .attr('id',function(d){return d.toString()})
     
     sg.append('text').text(dataElement.displayName).attr('y',y+15)
     .attr('x',x)
     .attr('id',"label" + dataElement.stId)
     .classed('noderectlabel',true);
     
     return rect
     
 }
 var renderReaction = function(reaction) {
     clearCanvas()
     setupForce()
     var n_inputs = reaction.input.length
     var w = parseInt(svg.attr('width'))
     var width_per = w/(n_inputs+1)
     var data;
     //deep clone so graphic attributes will not affect
     //reaction = $.extend(true, {}, reaction);
     
     var color = d3.scaleBand(); //category20();
     
     for (var i=0;i<n_inputs;i++) {
         reaction.input[i].left = width_per * (i+1);
         reaction.input[i].top = 30
     }
     
     var g = svg.selectAll('g').data(reaction.input)
     
     gs = g.enter().append('g') //.attr('x',function(d){return d*50 + 10}).attr('y',153)
     
     gs.each(function(g){reactantNode(d3.select(this),g);})
         
         
         
     var b = svg.selectAll('g .reactionnode').data([reaction])
          
     var rnameblock = b.enter().append("g").classed('reactionnode',true);
     
     
     //rnameblock.attr('x',w/2).attr('y',150).attr('width',80).attr('height',30).attr('id',function(d){return d.toString()}).style('fill','#eee')
     //rnameblock.append('text').text("reactionanme").attr('y',150).attr('x',w/2).attr('id','tryme');
     rnameblock.each(function(g){reactionNode(d3.select(this),g, w/2-110,150, 220,30);})
     
     
     
     var n_outputs = reaction.output.length
     var width_per = w/(n_outputs+1)
     var c = svg.selectAll('g .outputnode').data(reaction.output);
     
     for (var i=0;i<n_outputs;i++) {
         reaction.output[i].left = width_per * (i+1);
         reaction.output[i].top = 300
     }
     
     var c = svg.selectAll('g .outputnode').data(reaction.output);
     var output_gs = c.enter().append('g')
     output_gs.each(function(g){
         reactantNode(d3.select(this),g)
     })
     
     var inputlinkData = reaction.input.map(x => [x,reaction])
     var outputLinkData = reaction.output.map(x=> [reaction,x]);
     
     var links= svg.selectAll(".link .inputlink").data(inputlinkData);
     
     links.enter()
         .append('line')
             .attr('x1',function(d){return $('#' + d[0].toString()).attr('cx')})
             .attr('y1',function(d){return $('#' + d[0].toString()).attr('cy')})
             .attr('x2',function(d){var el = $('#' + d[1].toString());return parseInt(el.attr('x')) + parseInt(el.attr('width'))/2})
             .attr('y2',function(d){return $('#' + d[1].toString()).attr('y')})
             .classed("link",true)
             .style('marker-end','url(#end-arrow)');
     
      var links= svg.selectAll(".link .outputlink").data(outputLinkData);
     
             links.enter()
                  .append('line')     
                  .attr('x1',function(d){var el = $('#' + d[0].toString());return parseInt(el.attr('x')) + parseInt(el.attr('width'))/2})
                  .attr('y1',function(d){var el = $('#' + d[0].toString());return parseInt(el.attr('y')) + parseInt(el.attr('height'))})
                  .attr('x2',function(d){return $('#' + d[1].toString()).attr('cx')})
                  .attr('y2',function(d){return $('#' + d[1].toString()).attr('cy')})
              .classed("link",true)
              .style('marker-end','url(#end-arrow)').append('text').text("heyeverybody");

 }
 
 
 var renderAnimation = function(reaction) {
     clearCanvas()
     setupForce()
     var n_inputs = reaction.input.length
     var w = parseInt(svg.attr('width'))
     var width_per = w/(n_inputs+1)
     var data;
     //deep clone so graphic attributes will not affect
     //reaction = $.extend(true, {}, reaction);
     
     var color = d3.scaleBand();
     
     for (var i=0;i<n_inputs;i++) {
         reaction.input[i].left = width_per * (i+1);
         reaction.input[i].top = 30
     }
     
     var g = svg.selectAll('g').data(reaction.input)
     
     gs = g.enter().append('g') //.attr('x',function(d){return d*50 + 10}).attr('y',153)
     
     gs.each(function(g){reactantNode(d3.select(this),g);})
         
         
     var t = d3.transition()
     .duration(3000)
     .ease(d3.easeLinear);
     
     
         
     
     var meetingX = width/2;
     var meetingY = height/2;
     
     d3.selectAll('text').transition(t).attr('y',meetingY).attr('x', meetingX).remove()
     d3.selectAll('circle').transition(t).attr('cy',meetingY).attr('cx', meetingX).remove().on('end', function() {

         var n_outputs = reaction.output.length
         var width_per = w/(n_outputs+1)
         var c = svg.selectAll('g .outputnode').data(reaction.output);

         var outputLeft = meetingX - 30;
         
         for (var i=0;i<n_outputs;i++) {
             reaction.output[i].left = outputLeft;
             reaction.output[i].top = meetingY + (i%2) *15 ;
             outputLeft += 60
         }

         var c = svg.selectAll('g .outputnode').data(reaction.output);
         var output_gs = c.enter().append('g')
         output_gs.each(function(g){
             reactantNode(d3.select(this),g)
         })
                  
         var ttext = d3.transition()
         .duration(2000)
         .ease(d3.easeLinear);
         
         var txt = svg.append('text').text(reaction.displayName)
         txt.attr("x", meetingX).attr("y",meetingY).style('font-size',2);
     
         txt.transition(ttext).style("font-size",64).attr('x',meetingX/2).attr('y',0).remove()
         
     });     
 }
 
 
 var renderNetworkManual = function() {
    var reactions = rjs.reactions()

 }
    var doGraph = function(nodesAndLinks) {
        
        //manualLayout(nodesAndLinks);

        app.lastgraph = nodesAndLinks;
        //return
        
        /* sample json
        var json = {
          "nodes":[
        		{"name":"node1","group":1},
        		{"name":"node2","group":2},
        		{"name":"node3","group":2},
        		{"name":"node4","group":3}
        	],
        	"links":[
        		{"source":2,"target":1,"weight":1},
        		{"source":0,"target":2,"weight":3}
        	]
        }
        */
        var json = nodesAndLinks;

          force
              .nodes(json.nodes)
              .links(json.links)
              .start();

              setupMarkers(svg);
                  
          var link = svg.selectAll(".link")
              .data(json.links)
            .enter().append("line")   //enter selects those elements corresponding to newly added data elements
              .attr("class", "link")
            .style("stroke-width", function(d) { return Math.sqrt(d.weight); })
              .style('marker-end','url(#end-arrow)')
            .style('marker-start','url(#start-arrow)');

          link.append("text").text("hello")
          var node = svg.selectAll(".node")
              .data(json.nodes)
            .enter().append("g")
              .attr("class", "node")
              .attr('type', function(d) {
                      return  'type' in d ? d['type'] : 'reactantdog';
                })
              .call(force.drag).on("click", function(d) {
                  console.log(d);
                  
          });

          
          node.filter(function(d){return d.type!="reaction"}).append("circle").attr("r","12");

          node.filter(function(d){return d.type=="reaction"}).append("rect").attr("width",10).attr("height",10);
            
          node.append("text")
              .attr("dx", 12)
              .attr("dy", ".35em")
              .text(function(d) { return d.name });

          force.on("tick", function() {
            link.attr("x1", function(d) { return d.source.x; })
                .attr("y1", function(d) { return d.source.y; })
                .attr("x2", function(d) { return d.target.x; })
                .attr("y2", function(d) { return d.target.y; });
            node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
          });
          
          /*
      force
          .nodes(svg.select('.node'))
          .links(svg.select('.link'))
          .start();
          */
          

    }



    
    
    $(function() {
        setupForce()
        rjs.getPathwayList(showPathwayList)

        rjs.getPathway(Object.keys(app.sample_pathways)[0], pathway_viewer)
        //var pathway = jQuery.get({url:"http://reactome.org/ContentService/data/query/R-HSA-141409",success:renderReaction});
        
        $('#viewmode').change(function(){refreshDisplay()})
    });
    