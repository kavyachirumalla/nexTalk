function scrollToBottom() {
    const chatBox = document.getElementById("chat-box");
    chatBox.scrollTop = chatBox.scrollHeight;
}
function updateStatus(username, status) {
    const statusText = document.getElementById("status-text");
    if(username === CURRENT_USER)return;
    if(status === "online") {
        statusText.innerText = `${username} is online`;
    }
    else {
        statusText.innerText = ``;
    }
}
let typingTimeout;

function renderTyping(username) {
    const typingbox = document.getElementById("typing-status");
    typingbox.innerHTML =
    `
    ${username} is typing
    <div class="typing-dots">
    <span>●</span>
    <span>●</span>
    <span>●</span>
    </div>
    `;
    clearTimeout(typingTimeout);
    typingTimeout = setTimeout(() => {
        typingbox.innerHTML = "";
    }, 1000);
}
function appendMessage(data) {
    const chatBox = document.getElementById("chat-box");

    let msgHTML;
    if (data.username === CURRENT_USER) {
        msgHTML = `<div class="message msg-sent"
            data-sender="${data.username}">
            <div class="bubble">
                <div class="text">${data.message}</div>
                <div class="meta">
                    ${data.time}
                    <a href="/chat/delete/${data.id}" class="delete">×</a>
                </div>
            </div>
        </div>`;
    } else {
        msgHTML = `<div class="message msg-received"
            data-sender="${data.username}">
            <div class="bubble">
                <div class="text">${data.message}</div>
                <div class="meta">
                <span id="status-${data.id}"
                class="msg-status">
                ${data.seen ? "✓✓ Seen" : data.delivered ? "✓✓ Delivered" : "✓Sent"}
                </span>
                    ${data.time}
                </div>
            </div>
        </div>`;
    }
    chatBox.innerHTML += msgHTML;
    groupMessages();
    scrollToBottom();
}
function showNotification(message) {
    console.log("NOTIFICATION:", message);
}
const socket = new WebSocket('ws://' + window.location.host + '/ws/chat/'+ROOM_NAME+'/');

socket.onopen = function() {
    console.log("CONNECTED");
};
socket.onmessage = function(e) {


    const data = JSON.parse(e.data);
    console.log(data);
        if(data.type === "status") {
            updateStatus(data.username, data.status);
            return;
        }
        if(data.type==="typing") {

            if(data.username !== CURRENT_USER) {
             renderTyping(data.username);
    }
            return;
        }
    appendMessage(data);
};
function groupMessages() {
    const messages = document.querySelectorAll(".message");
    messages.forEach(msg => {
    msg.classList.remove("grouped"); 
    msg.style.marginTop = "12px";
});
    
    for(let i=1;i<messages.length;i++) {
        const current = messages[i];
        const previous = messages[i-1];
        
        const currentsender=current.dataset.sender;
        const previoussender=previous.dataset.sender;
        if(currentsender === previoussender){
            current.classList.add("grouped");
        } 
    }
}

function sendMessage() {
    console.log("buttton clicked");

    const input = document.getElementById("msg");
    const fileInput = document.getElementById("file-input");
    const form = document.getElementById("chat-form");
    const message = input.value.trim();
    console.log("MESSAGE:", message);
    const hasFile = fileInput.files.length > 0;
    if(message === "" && !hasFile) return;
    if(hasFile) {
        form.submit();
        return;
    }
    socket.send(JSON.stringify({
        type:"message",
        message: message,
        username: CURRENT_USER,
    }));
        input.value = "";
}
document.getElementById("msg").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }
});
const inputField = document.getElementById("msg");
inputField.addEventListener("input", function() {
    socket.send(JSON.stringify({
        type: "typing",
        username: CURRENT_USER,
    }));
});
groupMessages();
document.getElementById("send-btn").addEventListener("click", sendMessage);

const searchInput =
document.getElementById(
"search-input"
);

searchInput.addEventListener(
"input",
searchMessages
);

function searchMessages(){

const query =
searchInput.value
.toLowerCase();

const messages =
document.querySelectorAll(
".message"
);

messages.forEach(
msg=>{

const text =
msg.querySelector(
".text"
);

const original =
text.innerText;

if(
query === ""
){

msg.style.display=
"block";

text.innerHTML=
original;

return;

}

if(
original
.toLowerCase()
.includes(
query
)
){

msg.style.display=
"block";

const regex =
new RegExp(
query,
"gi"
);

text.innerHTML=
original.replace(
regex,

match=>
`<span class="highlight">${match}</span>`

);

}
else{

msg.style.display=
"none";

}

}

);

}