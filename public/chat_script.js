const messages = document.getElementById("messages");
var nickname = user["name"];
var p1_out = document.getElementById("p1");
var p2_out = document.getElementById("p2");
var p3_out = document.getElementById("p3");
var p4_out = document.getElementById("p4");
last_message = {"id": "0"};
oldest_message = {"id": "0"};
first_message = {"id": "0"};
logged = {"in": false};

function toBottom(){
    messages.scrollTop = messages.scrollHeight;
}
function sort(){
    $("#messages div").sort(function(a, b) {
        return parseInt(a.id) - parseInt(b.id);
    }).each(function() {
        var elem = $(this);
        elem.remove();
        if ($(`#messages #${elem.context.id}`).length <= 0)
            $(elem).appendTo("#messages");
});}
function send_message(){
    socket.emit("message", document.getElementById("message").value);
    document.getElementById("message").value = "";
}
function send_message_key(){
    if (event.keyCode == 13)
        send_message();
}
function f(){
    //console.log("works");
    if (logged.in) {
        p = Math.round(messages.scrollTop) / (messages.scrollHeight - parseInt(messages.style.height));
        collection = document.getElementsByClassName("scroll-page");
        l = collection.length;
        last_message.id = collection.item(l - 1).id;
        first_message.id = collection.item(0).id;
        if (((p <= 0) || isNaN(p)) && (first_message.id > oldest_message.id)) {
            socket.emit("request", {"option": "before", "point":first_message.id});
        }
        if (((p >= 1) || isNaN(p)) && (last_message.id < new_message.id)) {
            socket.emit("request", {"option": "after", "point":last_message.id});
        }
        n = 20;
        if (l > 150)
            n = 100;
        for (i=0;i<n;i++) {
            if (l>50) {
                if (p >= 0.5)
                    messages.removeChild(collection.item(0));
                else
                    messages.removeChild(collection.item(collection.length - 1));
        }}
        // await new Promise(r => setTimeout(r, 500));
        // window.requestAnimationFrame(f);
    } else {
        socket.emit("request", {"option": "before", "point":new_message.id});
    }
}
function ff(){
    p = Math.round(messages.scrollTop) / (messages.scrollHeight - parseInt(messages.style.height));
    l = document.getElementsByClassName("scroll-page").length;
    return (!(p * l <= l - 1));
}
socket.on('request answer', (data)=>{
    data.forEach(element => {
        n_m = document.createElement("div");
        n_m.classList.add("scroll-page");
        n_m.id = element[0];
        n_m.innerHTML = element[1];
        messages.appendChild(n_m);
    });
    sort();
    if (!(logged.in))
        logged.in = true;
});
socket.on("message", (data)=>{
    // n_m = document.createElement("div");
    // n_m.classList.add("scroll-page");
    // n_m.id = data[0];
    // n_m.innerHTML = data[1];
    new_message.id = data;
    t = ff();
    // messages.appendChild(n_m);
    sort();
    if (t) {toBottom();}
        
});

if (user["name"].length > 5)
    nickname = user["name"].substring(0, 5) + "...";
else 
    nickname = user["name"];
document.getElementById("user").innerHTML = nickname;


toBottom();
// f();
i1 = setInterval(f, 500); //doesn't work properly, need to fix
console.log("all is done");
