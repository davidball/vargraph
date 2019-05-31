var showText = function(text, x, y) {
var t = d3.transition()
    .duration(750)
    .ease(d3.easeLinear);
    
    var txt = svg.append('text').text(text)
    txt.attr("x", x).attr("y",y);
    
    txt.transition(t).style("font-size",64).remove()
    
}
var rjsquiz = {
    newGame:function(statusTextCallback) {
        $('#quiz_status').remove()
        //count reactions
        var reactions = rjs.reactions()
        
        this.reactions = reactions;
        var remaining_reactions = {}
        
        var reactant_needed_as_input_count = {}
        $.each(reactions,function(i,r){
            remaining_reactions[r.stId]= true;
            $.each(r.input, function(ii, input){
                if (input.stId  in reactant_needed_as_input_count) {
                    reactant_needed_as_input_count[input.stId] = reactant_needed_as_input_count[input.stId] + 1;
                } else {
                    reactant_needed_as_input_count[input.stId] = 1;
                }
            })
        })
        this.reactant_needed_as_input_count = reactant_needed_as_input_count;
        this.remaining_reactions = remaining_reactions;
        //count orphans. 
        var orphans = rjs.parentlessNodes()
        
        // count final products
        
        var finals = rjs.childlessNodes();
        var status_msg = "New game with " + reactions.length + " reactions.   Start with " + orphans.length + " and try to reach " + finals.length + " final products. "
        statusTextCallback(status_msg)
        
        this.renderNodes(orphans, "input");
        
        var div = $('<div id="quiz_status"><p>Match reactants to identify reactions</p><p><span id="foundreactions">0</span> of <span id="reactioncount"/></p><p><textarea id="quizstatus"></textarea></div>');
        div.find('#reactioncount').text(reactions.length);
        div.find('#quizstatus').text(status_msg)
        $('#viewer').prepend(div);
        this.score = 0;
    },
    updateScore:function(increment) {
        this.score = this.score + increment;
        $('#foundreactions').text(this.score);
    },
    reactantUsed:function(stId){
        
        this.reactant_needed_as_input_count[stId] = this.reactant_needed_as_input_count[stId] -1;
        if (this.reactant_needed_as_input_count[stId] == 0) {
            d3.select('#'+stId).remove();
            d3.select("#label" + stId).remove();
        } 
    },
    gameOver:function(){
        var t = d3.transition()
        .duration(750)
        .ease(d3.easeLinear);
        
        var txt = svg.append('text').text('Game Over')
        txt.attr("x", 50).attr("y",100);
        
        txt.transition(t).style("font-size",128)
        
        svg.transition(t).style('background-color','red')
        
        svg.transition(t).style('background-color','white')
    },
    renderNodes:function(nodes, className) {
        var thisQuiz = this; //for access in the nested loops below
        clearCanvas()
        setupForce()
        var n_inputs = nodes.length
        var w = parseInt(svg.attr('width'))
        var width_per = w/(n_inputs+1)
        var data;
        //deep clone so graphic attributes will not affect
        //reaction = $.extend(true, {}, reaction);
     
        var color = d3.scaleBand();
     
        
        

        
        for (var i=0;i<n_inputs;i++) {
            nodes[i].left = Math.random() * 0.8 * width + width*0.2
            nodes[i].top =  Math.random() * 0.8 * height + height*0.2
        }
     
        var g = svg.selectAll('g').data(nodes)
     
        gs = g.enter().append('g') //.attr('x',function(d){return d*50 + 10}).attr('y',153)
     
        gs.each(function(g){reactantNode(d3.select(this),g);})
         
            function dragstarted(d) {
                           console.log('dstart1')
              d3.select(this).raise().classed("active", true);
              console.log('dstart2')
            }

            function dragged(d) {
              d3.select(this).attr("cx", d.x = d3.event.x).attr("cy", d.y = d3.event.y);
                         d3.select(this.parentNode).selectAll('text').attr("x", d.x = d3.event.x).attr("y", d.y = d3.event.y);
                         window.ddd = d;
   //              d3.select(this.parentNode).attr("transform", "translate(" + d3.event.x+","+d3.event.y+")");
            }

            function dragended(d) {
                console.log(d)
                window.ddd = d;
                var neighbor_map = Array.from(rjs.G.get(d));
                var neighbors = []
             
                neighbor_map.forEach(function(a,b){neighbors.push(a[0])})
             
                console.log(neighbors)
                window.neighbors = neighbors
                var reactions = neighbors.filter(x => x.className == 'Reaction')
                var peer_inputs = reactions.map(x=> x.input).reduce(function(a, b) {return a.concat(b);}).filter(x=> x.stId != d.stId);
             
                $.each(peer_inputs, function(i,n) {
                    var domid = "#" + n.stId
                    var potential_match = svg.select(domid);
                    if (svg.selectAll(domid).size()==1) {
                    window.potential_match = potential_match
                 
                    var target_x = parseInt(potential_match.attr('cx'));
                    var target_y = parseInt(potential_match.attr('cy'));
                     
                    var distsq = (d3.event.x - target_x )**2 + (d3.event.y - target_y)**2;
                    if (distsq < 36) {
                        console.log("match")
                        //todo
                        var reaction = reactions[0];//hack not necessarily THAT reaction
                        showText('Reaction! ' + reaction.displayName, d3.event.x, d3.event.y);
                        thisQuiz.reactantUsed(n.stId);
                        thisQuiz.reactantUsed(d.stId);
                            
                        thisQuiz.updateScore(1);
                        delete thisQuiz.remaining_reactions[reaction.stId];
                        var n_outputs = reaction.output.length
                        var width_per = w/(n_outputs+1)
//                        var c = svg.selectAll('g .outputnode').data(reaction.output);
     
                        for (var i=0;i<n_outputs;i++) {
                            reaction.output[i].left = width_per * (i+1);
                            reaction.output[i].top = d3.event.y + 15
                        }
     
                        var c = svg.selectAll('g .outputnode').data(reaction.output);
                        var output_gs = c.enter().append('g')
                        output_gs.each(function(g ){
                            reactantNode(d3.select(this),g)
                        })
                        
                        if (Object.keys(thisQuiz.remaining_reactions).length ==0) {
                            thisQuiz.gameOver();
                        } else {
                            svg.selectAll("circle")
                            .call(d3.drag()
                            .on("start", dragstarted)
                            .on("drag", dragged)
                            .on("end", dragended));
                        }
                     
                    } else {
                        console.log("you missed")
                    }
                } else {
                    console.log("Invalid number of matches to " + domid + ' had ' + svg.selectAll(domid).size())
                }
                })
                console.log("peer_inputs")
                console.log(peer_inputs)
              d3.select(this).classed("active", false);
            }
         
         
        svg.selectAll("circle")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));
    }
}