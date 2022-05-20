
const socket = io(document.location.href);
const sid = socket.io.engine.id;
var result = document.getElementById("result");
var main = document.getElementById("main");
var user= {};

function send() {
    user["name"] = document.getElementById("usr").value;
    socket.emit("login", {
        "usr": user["name"],
        "pwd": document.getElementById("pwd").value,
    });
}
function register(){
    socket.emit("register", {
        "usr": document.getElementById("usr").value,
        "pwd": document.getElementById("pwd").value,
    });
    result.innerHTML = " wait... ";
    result.style.color = "#000000";
}
function next(){
    script_jquery = document.createElement("script");
    script_jquery.src = "https://code.jquery.com/jquery-1.10.1.js";
    document.getElementsByTagName('head')[0].appendChild(script_jquery);
    script_new = document.createElement("script");
    script_new.src = "/static/chat_script.js";
    document.getElementsByTagName('head')[0].appendChild(script_new);
}
function usr_key_down(){
    if (event.keyCode == 13) document.getElementById("pwd").focus();
}
function pwd_key_down(){
    if (event.keyCode == 13) send();
}


socket.on('login answer', (data) => {
    console.log(data["code"]);
    switch (data["code"]){
        case "wrong pwd":
        result.innerHTML = " * wrong password";
        result.style.color = "#FF0000";
        break;
        case "wrong usr":
        result.innerHTML = " * no such user ";
        let btn = document.createElement("button");
        btn.onclick = register;
        btn.innerHTML = "Register";
        result.appendChild(btn);
        result.style.color = "#FF0000";
        break;
        case "ok":
        result.innerHTML = " OK ";
        result.style.color = "#00FF00";
        main.innerHTML = data["new"];
        next();
        break;
        case "overlap":
        result.innerHTML = " * this user already logged in"
        result.style.color = "#FF0000";
        break;
    }
});

socket.on("register answer", (data) => {
    switch (data){
        case "ok":
        result.innerHTML = " Registerd ";
        result.style.color = "#00FF00";
        break;
        case "overlap":
        result.innerHTML = " This login already taken"
        result.style.color = "#FF0000";
        break;
    }
});

socket.on("stop", (_)=>{location.reload()});

document.getElementById("usr").focus();
