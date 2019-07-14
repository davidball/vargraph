export class ToyModule {

    dosomething() {
        console.log("like what?")
        console.log(window.islove);
    }
}

export var weird = 2;
//export  ToyModule;


var w = new ToyModule();
console.log("in module")
w.dosomething();
