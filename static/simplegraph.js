export class SimpleGraph {
    constructor() {

    }
    data() {
        return { nodes: [1, 2, 3, 4], links: [{ from: 1, to: 2 }, { from: 2, to: 3 }, { from: 3, to: 4 }, { from: 4, to: 1 }] }
    }
}

console.log('loading simpel graph')