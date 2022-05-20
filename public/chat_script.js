const messages = document.getElementById("messages");
var nickname = user["name"];
function toBottom(){
    messages.scrollTop = messages.scrollHeight;
}
function sort(){
    $("#messages div").sort(function(a, b) {
        return parseInt(a.id) - parseInt(b.id);
    }).each(function() {
        var elem = $(this);
        elem.remove();
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
socket.on("message", (data)=>{
    n_m = document.createElement("div");
    n_m.classList.add("scroll-page");
    n_m.id = data[0];
    n_m.innerHTML = data[1];
    messages.appendChild(n_m);
    sort();
    toBottom();
})

if (user["name"].length > 5)
    nickname = user["name"].substring(0, 5) + "...";
else 
    nickname = user["name"];
document.getElementById("user").innerHTML = nickname;

sort();
toBottom();