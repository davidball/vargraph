/*
partial wrapper of the reactome.org api

stores data in jsnetworkx
*/

var idFunctionizeNode = function(node) {
    node.toString = function() {return node.stId}
}
var rjs = {
    G:new jsnx.DiGraph(),
    urls: {
        pathwayList:"https://reactome.org/ContentService/data/pathways/top/Homo+sapiens",
        generalQuery:"https://reactome.org/ContentService/data/query/"
    },
    getPathwayList: function(onSuccess){
        var pathwaylist = jQuery.get({"url":this.urls.pathwayList,success:onSuccess});
    },
    getPathway:function(id, onSuccess){
        var f = this.cachePathwayData;
        var responder = function(resp){
            f(resp, onSuccess);
        }
        jQuery.get({url:this.urls.generalQuery + id,success:responder});
    },
    cachePathwayData:function(resp, onSuccess){
        console.log('todo save pathway data')
        onSuccess(resp)
    },
    queryById:function(id, cachingFunction, onSuccess) {
        var responder = function(resp){
            cachingFunction(resp, onSuccess);
        }
        jQuery.get({url:this.urls.generalQuery + id,success:responder});
    }, 
    getReaction:function(id,onSuccess){
        this.queryById(id, this.cacheReactionData, onSuccess)
    },
    cacheReactionData:function(resp, onSuccess) {
        console.log('todo save reaction data')        
        console.log(resp)

        

        //sometimes the reactome response has numeric only entries in the input and output array, we exclude those here
        resp.input = resp.input.filter(x => typeof(x) == 'object')
        resp.output = resp.output.filter(x => typeof(x) == 'object')
        
        var all_nodes_in_resp = [resp].concat(resp.input).concat(resp.output)

        //jsnetworkx looks for a toString function on each node for it's unique id, add that here.
        $.each(all_nodes_in_resp, function(i,n) {idFunctionizeNode(n)});
        
        rjs.G.addNodesFrom(all_nodes_in_resp);
        
        rjs.G.addEdgesFrom(resp.input.map(x => [x,resp]))
        rjs.G.addEdgesFrom(resp.output.map(x => [resp,x]))
        
        onSuccess(resp);
    },
     parentlessNodes: function() {
        return Array.from(this.G.inDegree()).filter( node => node[1]==0).map( node => node[0])
    },
    
     childlessNodes: function() {
        return Array.from(this.G.inDegree()).filter( node => node[1]==0).map( node => node[0])
    },
    reactions: function() {
        return Array.from(this.G.nodes()).filter( node => node.className=="Reaction")
    },
    nodeById: function(stId) {
        
    },
    reactomeUrl:function(stId) {
      return 'https://reactome.org/PathwayBrowser/#/' + stId;
    },
    draw:function(inElement){
        var color = d3.scaleBand();
        
        jsnx.draw(this.G, {
            element: inElement,
            withLabels: true,
            layoutAttr: {
                charge: -120,
                linkDistance: 20
            },
            labels: function(d) { return d.node.name  },
            nodeShape: 'circle',
            nodeAttr: {
                r: 5,
                title: function(d) { return d.node.name;}
            },
            nodeStyle: {
                fill: function(d) { 
                    return color(d.data.group); 
                },
                stroke: 'none'
            },
            edgeStyle: {
                fill: '#999'
            }
        });
        
        
    }
    
}